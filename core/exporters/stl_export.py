import bpy
import bmesh
from .base_export import Base_Export


class STL_Export(Base_Export):
    formats = [".stl"]

    def __init__(self, context):
        super().__init__(context, format=".stl")

    def export(self, obj, materials_removed):
        bpy.ops.export_mesh.stl(
            filepath=self._Base_Export__export_folder + "/" + obj.name + ".stl",
            use_selection=True,
            ascii=False,
            use_mesh_modifiers=True,
            axis_forward="Y",
            axis_up="Z",
        )
