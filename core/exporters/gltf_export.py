import bpy
from .base_export import Base_Export


class GLTF_Export(Base_Export):
    def __init__(self, context):
        super().__init__(context, format=".gltf")

    def export(self, obj, materials_removed):
        bpy.ops.export_scene.gltf(
            filepath=self._Base_Export__export_folder + "/" + obj.name + ".gltf",
            export_materials="EXPORT" if materials_removed else "NONE",
            export_colors=True,
            use_mesh_edges=False,
            use_mesh_vertices=False,
            use_selection=True,
        )
