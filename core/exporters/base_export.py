import bpy
import bmesh
import os
from ..utils import get_object_loc, set_object_to_loc, get_children


class Base_Export:
    def __init__(self, context, format):
        self.__context = context
        self.__export_folder = context.scene.export_folder

        if self.__export_folder.startswith("//"):
            self.__export_folder = os.path.abspath(
                bpy.path.abspath(context.scene.export_folder)
            )

        self.__center_transform = context.scene.center_transform
        self.__apply_transform = context.scene.apply_transform
        self.__one_material_id = context.scene.one_material_ID
        self.__export_objects = context.selected_objects
        self.__export_animations = context.scene.export_animations
        self.__mat_faces = {}
        self.__materials = []
        self.__format = format

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

    def do_export(self):
        bpy.ops.object.mode_set(mode="OBJECT")

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

    def export(self, obj, materials_removed):
        raise NotImplementedError("Subclasses must implement the export method")
