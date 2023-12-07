import bpy
import bmesh
from .base_export import Base_Export


class OBJ_Export(Base_Export):
    formats = [".obj"]

    def __init__(self, context):
        super().__init__(context, format=".obj")

    def export(self, obj, materials_removed):
        bpy.ops.export_scene.obj(
            filepath=self._Base_Export__export_folder + "/" + obj.name + ".obj",
            use_selection=True,
            use_materials=not materials_removed,
            use_animation=self._Base_Export__export_animations,
            axis_forward="Y",
            axis_up="Z",
            path_mode="COPY",
        )
