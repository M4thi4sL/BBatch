import bpy
import bmesh
import os
import re
import logging
from ..utils import get_object_loc, set_object_to_loc, get_children, get_addon_preferences
from ..version_control.perforce_manager import PerforceManager

# Set up logging
logger = logging.getLogger(__name__)


class Base_Export:
    formats = []

    def __init__(self, context: bpy.types.Context, format: str):
        self.__context = context
        props = context.scene.panel_properties
        self.__export_folder = self._resolve_export_folder(props.export_folder)
        self.__center_transform = props.center_transform
        self.__one_material_id = props.one_material_ID
        self.__export_objects = context.selected_objects
        self.__export_animations = props.export_animations
        self.__export_smoothing = props.export_smoothing
        self.__mat_faces = {}
        self.__materials = []
        self.__format = format
        self.original_names = {}

        # Access the addon preferences to get the use_perforce property
        addon_prefs = get_addon_preferences("BBatch")
        self.use_perforce = addon_prefs.enable_perforce  # Accessing use_perforce from preferences
        self.perforce_manager = PerforceManager() if self.use_perforce else None  # Initialize Perforce manager only if needed

    def _resolve_export_folder(self, export_folder: str) -> str:
        """Resolve the export folder path."""
        if export_folder.startswith("//"):
            return os.path.abspath(bpy.path.abspath(export_folder))
        return export_folder

    def store_original_names(self):
        """Store the original names of all objects."""
        for obj in bpy.data.objects:
            self.original_names[obj] = obj.name

    def do_center(self, obj):
        """Center the object's transform if the setting is enabled."""
        if self.__center_transform:
            loc = get_object_loc(obj)
            set_object_to_loc(obj, (0, 0, 0))
            return loc
        return None

    def remove_materials(self, obj):
        """Remove materials from the object except the last one, if needed."""
        if obj.type == "ARMATURE":
            return False

        mat_count = len(obj.data.materials)

        if mat_count > 1 and self.__one_material_id:
            bpy.ops.object.mode_set(mode="EDIT")
            bm = bmesh.from_edit_mesh(obj.data)

            for face in bm.faces:
                self.__mat_faces[face.index] = face.material_index

            bpy.ops.object.mode_set(mode="OBJECT")
            self.__materials.clear()

            for idx in range(mat_count):
                self.__materials.append(obj.data.materials[0])
                if idx < mat_count - 1:
                    obj.data.materials.pop(index=0)

            return True
        return False

    def restore_materials(self, obj):
        """Restore the materials for the object."""
        obj.data.materials.clear()

        for mat in self.__materials:
            obj.data.materials.append(mat)

        obj.data.update()

        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)

        for face in bm.faces:
            mat_index = self.__mat_faces[face.index]
            face.material_index = mat_index

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")

    def rename_non_export_objects_with_prefix(self, prefix="%BBatch%_"):
        """Rename all non-export objects with the given prefix."""
        for obj in bpy.data.objects:
            if obj not in self.current_export_objects:
                obj.name = f"{prefix}{obj.name}"

    def strip_suffix_and_rename(self, obj):
        """Strip the .xxx suffix if present from the object's name."""
        if re.match(r".*\.\d{3}$", obj.name):
            base_name = obj.name.rsplit(".", 1)[0]  # Strip the .xxx suffix
            obj.name = base_name

    def restore_original_names(self):
        """Restore all original names from the stored dictionary."""
        for obj, original_name in self.original_names.items():
            obj.name = original_name

    def do_export(self):
        bpy.ops.object.mode_set(mode="OBJECT")

        # Store the original names and positions of all objects before any modifications
        self.store_original_names()
        original_positions = {obj: get_object_loc(obj) for obj in self.__export_objects}

        skipped_exports = []  # List to track skipped exports and reasons

        for root_obj in self.__export_objects:
            # Gather the export object and its children for processing
            self.current_export_objects = [root_obj] + get_children(root_obj)

            # Step 1: Rename all non-export objects with the prefix
            self.rename_non_export_objects_with_prefix()

            # Step 2: Strip .xxx suffix and rename export objects
            for export_obj in self.current_export_objects:
                # Ensure we don't rename already prefixed objects
                self.strip_suffix_and_rename(export_obj)

            # Deselect all and select the export object and its children
            bpy.ops.object.select_all(action="DESELECT")
            for export_obj in self.current_export_objects:
                export_obj.select_set(state=True)

            # Center selected object
            old_pos = self.do_center(root_obj)

            # Remove materials except the last one
            materials_removed = self.remove_materials(root_obj)

            export_filename = f"{root_obj.name}{self.__format}"  # Use the format property for extension
            export_filepath = os.path.join(self.__export_folder, export_filename)

            if self.use_perforce:  # Only check if using Perforce
                if self.perforce_manager.file_exists(export_filepath):
                    if self.perforce_manager.is_file_checked_in(export_filepath):
                        try:
                            self.perforce_manager.checkout_file(export_filepath)  # Check out the file
                        except PermissionError:
                            # Add to skipped exports list with the reason
                            skipped_exports.append((export_obj.name, "Checkout failed"))
                            continue  # Skip this object and move to the next

            # Check if the file is read-only before attempting to export
            if os.path.exists(export_filepath) and not os.access(export_filepath, os.W_OK):
                skipped_exports.append((root_obj.name, "File is read-only, skipping export."))
                # Restore the original scene
                if materials_removed:
                    self.restore_materials(root_obj)
                if old_pos is not None:
                    set_object_to_loc(root_obj, old_pos)
                self.restore_original_names()
                continue  # Skip this object and move to the next

            # Wrap the export in a try-except block to catch errors during export
            try:
                self.export(root_obj, materials_removed)
            except Exception as e:
                # Add to skipped exports list with a short error message
                skipped_exports.append((export_obj.name, f"Export failed: {type(e).__name__}"))
                print(f"Error exporting '{root_obj.name}': {type(e).__name__}")  # Print only the exception type
                continue  # Skip to the next root object

            # Restore the materials if they were altered
            if materials_removed:
                self.restore_materials(root_obj)

            # Restore the original location
            if old_pos is not None:
                set_object_to_loc(root_obj, old_pos)

            # Restore the original names immediately after exporting this object
            self.restore_original_names()

        # Final restoration of original names (if needed)
        self.restore_original_names()

        # Restore original positions for skipped objects
        for obj, original_pos in original_positions.items():
            set_object_to_loc(obj, original_pos)

        # Report the results
        if skipped_exports:

            def draw_callback(self, context):
                self.layout.label(text="Export completed with some issues:")
                for name, reason in skipped_exports:
                    self.layout.label(text=f"{name}: {reason}")

            self.__context.window_manager.popup_menu(draw_callback, title="Warning", icon="ERROR")
        else:
            self.__context.window_manager.popup_menu(lambda self, context: self.layout.label(text="All objects exported successfully!"), title="Info", icon="INFO")

    def export(self, obj, materials_removed):
        """Abstract method for exporting; must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement the export method")
