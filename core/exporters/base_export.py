import bpy
import bmesh
import os
import re
from ..utils import get_object_loc, set_object_to_loc, get_children


class Base_Export:
    formats = []

    def __init__(self, context, format):
        self.__context = context
        self.__export_folder = context.scene.export_folder

        if self.__export_folder.startswith("//"):
            self.__export_folder = os.path.abspath(bpy.path.abspath(context.scene.export_folder))

        self.__center_transform = context.scene.center_transform
        self.__one_material_id = context.scene.one_material_ID
        self.__export_objects = context.selected_objects
        self.__export_animations = context.scene.export_animations
        self.__mat_faces = {}
        self.__materials = []
        self.__format = format
        self.original_names = {}  # Store original names for restoration

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
        # Gather all objects in the scene
        all_objects = bpy.data.objects

        # Gather all export objects and their children to exclude from prefix renaming
        export_objects_and_children = list(self.__export_objects)
        for obj in self.__export_objects:
            export_objects_and_children.extend(get_children(obj))

        # Loop over all objects and add prefix to their names if not an export object or its child
        for obj in all_objects:
            if obj not in export_objects_and_children:
                self.original_names[obj] = obj.name  # Store original name
                obj.name = f"{prefix}{obj.name}"

        print("Added prefix to all non-export object names successfully.")

    def strip_suffix_from_export_objects(self):
        # Gather export objects and their children
        all_export_objects = list(self.__export_objects)

        for obj in self.__export_objects:
            all_export_objects.extend(get_children(obj))

        # Iterate through the combined list of objects
        for obj in all_export_objects:
            # Store the original name to restore later
            self.original_names[obj] = obj.name

            # Check if the object has a .xxx suffix and strip it
            if re.match(r".*\.\d{3}$", obj.name):
                base_name = obj.name.rsplit(".", 1)[0]  # Strip the .xxx suffix
                obj.name = base_name

        print("Stripped .xxx suffix from all export objects successfully.")

    def restore_original_names(self):
        # First, restore the names of the exported objects and their children
        export_objects_and_children = list(self.__export_objects)
        for obj in self.__export_objects:
            export_objects_and_children.extend(get_children(obj))

        for obj in export_objects_and_children:
            if obj in self.original_names:
                obj.name = self.original_names[obj]

        # Then, restore the names of all other objects
        for obj, original_name in self.original_names.items():
            if obj not in export_objects_and_children:
                obj.name = original_name

        print("Restored all original object names successfully.")

    def do_export(self):
        bpy.ops.object.mode_set(mode="OBJECT")

        # Step 1: Rename all non-export objects with the prefix
        self.rename_non_export_objects_with_prefix()

        # Step 2: Rename export objects by stripping .xxx suffix
        self.strip_suffix_from_export_objects()

        for obj in self.__export_objects:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(state=True)

            # Center selected object
            old_pos = self.do_center(obj)

            # Select children if exist
            for child in get_children(obj):
                child.select_set(state=True)

            # Remove materials except the last one
            materials_removed = self.remove_materials(obj)

            ex_object_types = {"MESH"}

            if self.__export_animations:
                ex_object_types.add("ARMATURE")

            # Export the selected object
            self.export(obj, materials_removed)

            if materials_removed:
                self.restore_materials(obj)

            if old_pos is not None:
                set_object_to_loc(obj, old_pos)

        # Step 3: Restore all original names after exporting
        self.restore_original_names()

    def export(self, obj, materials_removed):
        raise NotImplementedError("Subclasses must implement the export method")
