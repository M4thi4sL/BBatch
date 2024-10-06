import bpy
from .base_export import Base_Export


class FBX_Export(Base_Export):
    formats = [".fbx"]

    def __init__(self, context):
        super().__init__(context, format=".fbx")

    def export(self, obj, materials_removed):
        bpy.ops.export_scene.fbx(
            check_existing=False,
            filepath=self._Base_Export__export_folder + "/" + obj.name + ".fbx",
            filter_glob="*.fbx",
            use_selection=True,
            object_types={"MESH", "ARMATURE", "EMPTY"} if self._Base_Export__export_animations else {"MESH", "EMPTY"},
            bake_anim=self._Base_Export__export_animations,
            bake_anim_use_all_bones=self._Base_Export__export_animations,
            bake_anim_use_all_actions=self._Base_Export__export_animations,
            use_armature_deform_only=True,
            mesh_smooth_type=self._Base_Export__context.scene.export_smoothing,
            add_leaf_bones=False,
            path_mode="ABSOLUTE",
        )
