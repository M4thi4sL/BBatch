import bpy
from bpy.types import Panel
from bpy.props import BoolProperty


class BBatch_PT_MainPanel(Panel):
    bl_label = "BBatch Exporter"
    bl_idname = "bbatch_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BBatch"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export folder settings
        layout.label(text="Folder:")

        box = layout.box()
        row = box.row()
        row.prop(context.scene, "export_folder", text="")

        # File format dropdown
        row = layout.row()
        row.label(text="File Format:")
        row.prop(context.scene, "export_file_format", text="")

        # Options toggle button
        row = layout.row(align=True)
        row.operator(
            "object.bex_ot_toggle_options",
            text="Advanced Options",
            icon="TRIA_DOWN" if context.scene.show_options else "TRIA_RIGHT",
        )

        # Options box
        if context.scene.show_options:
            box = layout.box()
            row = box.row()
            row.prop(context.scene, "center_transform", text="Center Transform")
            row.prop(context.scene, "one_material_ID")
            row = box.row()
            row.label(text="Smoothing:")
            row.prop(context.scene, "export_smoothing", text="")

        # Export button
        layout.operator("object.bex_ot_operator", text="Export")
