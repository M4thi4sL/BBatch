import bpy
from .base_export import Base_Export

class ABC_Export(Base_Export):
    def __init__(self, context):
        super().__init__(context, format=".abc")

    def export(self, obj, materials_removed):
        bpy.ops.wm.alembic_export(
            filepath=self._Base_Export__export_folder + "/" + obj.name + ".abc",
            selected=True,
            start=bpy.context.scene.frame_start,
            end=bpy.context.scene.frame_end,
            global_scale=obj.scale[0],
        )
