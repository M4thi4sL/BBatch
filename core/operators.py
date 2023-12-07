import bpy

from bpy.types import Operator
from .exporters import (
    OBJ_Export,
    FBX_Export,
    STL_Export,
    GLTF_Export,
    ABC_Export,
    DAE_Export,
)


class BBatch_OT_ExportOperator(Operator):
    bl_idname = "object.bex_ot_operator"
    bl_label = "Batch Export"
    bl_description = "export the selected objects"
    bl_options = {"REGISTER"}

    def execute(self, context):
        export_format = context.scene.export_file_format

        if export_format == ".obj":
            exporter = OBJ_Export(context)
        elif export_format == ".fbx":
            exporter = FBX_Export(context)
        elif export_format == ".stl":
            exporter = STL_Export(context)
        elif export_format == ".gltf":
            exporter = GLTF_Export(context)
        elif export_format == ".dae":
            exporter = DAE_Export(context)
        elif export_format == ".abc":
            exporter = ABC_Export(context)
        else:
            self.report(
                {"ERROR"}, "Unsupported export format: {}".format(export_format)
            )
            return {"CANCELLED"}

        exporter.do_export()

        self.report({"INFO"}, "Exported to " + context.scene.export_folder)
        return {"FINISHED"}


class BBatch_OT_ToggleOptionsOperator(Operator):
    bl_idname = "object.bex_ot_toggle_options"
    bl_label = "Toggle Options"

    def execute(self, context):
        context.scene.show_options = not context.scene.show_options
        return {"FINISHED"}
