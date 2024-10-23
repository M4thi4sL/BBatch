import bpy
import bmesh
import os
import re
from ..utils import get_object_loc, set_object_to_loc, get_children


class Base_Export:
    formats = []

    def __init__(self, context, format):

        props = context.scene.panel_properties

        self.__context = context
        self.__export_folder = props.export_folder

        if self.__export_folder.startswith("//"):
            self.__export_folder = os.path.abspath(bpy.path.abspath(props.export_folder))

        self.__center_transform = props.center_transform
        self.__one_material_id = props.one_material_ID
        self.__export_objects = context.selected_objects
        self.__export_animations = props.export_animations
        self.__export_smoothing = props.export_smoothing
        self.__mat_faces = {}
        self.__materials = []
        self.__format = format
        self.original_names = {}  # Store original names for restoration

    def store_original_names(self):
        # Store the original names of all objects
        for obj in bpy.data.objects:
            self.original_names[obj] = obj.name

    def do_center(self, obj):
        if self.__center_transform:
            loc = get_object_loc(obj)
            set_object_to_loc(obj, (0, 0, 0))
            return loc

        return None

    def remove_materials(self, obj):
        if obj.type == "ARMATURE":
            return False

        mat_count = len(obj.data.materials)

        if mat_count > 1 and self.__one_material_id:
            # Save material ids for faces
            bpy.ops.object.mode_set(mode="EDIT")

            bm = bmesh.from_edit_mesh(obj.data)

            for face in bm.faces:
                self.__mat_faces[face.index] = face.material_index

            # Save and remove materials except the last one
            # so that we keep this as material id
            bpy.ops.object.mode_set(mode="OBJECT")
            self.__materials.clear()

            for idx in range(mat_count):
                self.__materials.append(obj.data.materials[0])
                if idx < mat_count - 1:
                    obj.data.materials.pop(index=0)

            return True
        else:
            return False

    def restore_materials(self, obj):
        # Restore the materials for the object
        obj.data.materials.clear()

        for mat in self.__materials:
            obj.data.materials.append(mat)

        obj.data.update()

        # Reassign the material ids to the faces of the mesh
        bpy.ops.object.mode_set(mode="EDIT")

        bm = bmesh.from_edit_mesh(obj.data)

        for face in bm.faces:
            mat_index = self.__mat_faces[face.index]
            face.material_index = mat_index

        bmesh.update_edit_mesh(obj.data)

        bpy.ops.object.mode_set(mode="OBJECT")

    def rename_non_export_objects_with_prefix(self, prefix="%BBatch%_"):
        # Rename all non-export objects with prefix
        for obj in bpy.data.objects:
            if obj not in self.current_export_objects:
                obj.name = f"{prefix}{obj.name}"

    def strip_suffix_and_rename(self, obj):
        # Strip the .xxx suffix if present
        if re.match(r".*\.\d{3}$", obj.name):
            base_name = obj.name.rsplit(".", 1)[0]  # Strip the .xxx suffix
            obj.name = base_name

    def restore_original_names(self):
        # Restore all original names from stored dictionary
        for obj, original_name in self.original_names.items():
            obj.name = original_name

    def do_export(self):
        bpy.ops.object.mode_set(mode="OBJECT")

        # Store the original names of all objects before any modifications
        self.store_original_names()

        for root_obj in self.__export_objects:
            # Gather the export object and its children for processing
            self.current_export_objects = [root_obj] + get_children(root_obj)

            # Step 1: Rename all non-export objects with the prefix
            self.rename_non_export_objects_with_prefix()

            # Step 2: Rename the export object and its children (strip .xxx suffix)
            for export_obj in self.current_export_objects:
                self.strip_suffix_and_rename(export_obj)

            # Deselect all and select the export object and its children
            bpy.ops.object.select_all(action="DESELECT")
            for export_obj in self.current_export_objects:
                export_obj.select_set(state=True)

            # Center selected object
            old_pos = self.do_center(root_obj)

            # Remove materials except the last one
            materials_removed = self.remove_materials(root_obj)

            ex_object_types = {"MESH"}

            if self.__export_animations:
                ex_object_types.add("ARMATURE")

            # Export the selected object
            self.export(root_obj, materials_removed)

            # Restore the materials if they were altered
            if materials_removed:
                self.restore_materials(root_obj)

            # Restore the original location
            if old_pos is not None:
                set_object_to_loc(root_obj, old_pos)

            # Step 3: Restore all original names after exporting
            self.restore_original_names()

    def export(self, obj, materials_removed):
        raise NotImplementedError("Subclasses must implement the export method")
