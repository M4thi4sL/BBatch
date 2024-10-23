from bpy.types import Panel


class BBATCH_PT_MainPanel(Panel):
    bl_label = "BBatch Exporter"
    bl_idname = "BBATCH_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BBatch"

    def draw(self, context):
        layout = self.layout

        # Access the panel properties
        props = context.scene.panel_properties

        # Export folder settings
        layout.label(text="Export Folder", icon="FILE_FOLDER")

        box = layout.box()
        row = box.row()
        row.prop(props, "export_folder", text="")

        # File format dropdown
        row = layout.row()
        row.label(text="File Format:", icon="FILE_BLEND")
        row.prop(context.scene, "export_file_format", text="")

        # Options toggle button
        row = layout.row(align=True)
        row.operator(
            "object.bbatch_ot_toggle_options",
            text="Advanced Options",
            icon="TRIA_DOWN" if props.show_options else "TRIA_RIGHT",
        )

        # Advanced options
        if props.show_options:
            box = layout.box()

            box.prop(props, "center_transform", text="Center Transform", icon="EMPTY_ARROWS")
            box.prop(props, "one_material_ID", text="Single Material ID", icon="MATERIAL")

            row = box.row()
            row.label(text="Smoothing:", icon="MOD_SMOOTH")
            row.prop(props, "export_smoothing", text="")

        # Export button
        layout.separator()
        layout.operator("object.bbatch_ot_operator", text="Export", icon="EXPORT")
