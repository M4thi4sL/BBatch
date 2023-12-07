import bpy
from .base_export import Base_Export


class DAE_Export(Base_Export):
    def __init__(self, context):
        super().__init__(context, format=".dae")

    def export(self, obj, materials_removed):
        bpy.ops.wm.collada_export(
            filepath=self._Base_Export__export_folder + "/" + obj.name + ".dae",
            selected=True,
            apply_modifiers=True,
        )
