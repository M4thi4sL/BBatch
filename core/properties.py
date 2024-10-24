# settings.py

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import PropertyGroup


class BBatch_PanelProperties(PropertyGroup):
    export_folder: StringProperty(
        name="Export folder",
        subtype="DIR_PATH",
        description="Directory to export the fbx files into",
        default=".\\",
    )

    center_transform: BoolProperty(
        name="Center Transform",
        description="Move the object back to world origins (0,0,0) before exporting it.",
        default=True,
    )

    export_smoothing: EnumProperty(
        name="Smoothing",
        description="Defines the export smoothing information",
        items=(
            ("EDGE", "Edge", "Write edge smoothing", 0),
            ("FACE", "Face", "Write face smoothing", 1),
            ("OFF", "Normals Only", "Write normals only", 2),
        ),
        default="OFF",
    )

    show_options: BoolProperty(
        name="Show Options",
        description="Display additional options",
        default=False,
    )

    export_animations: BoolProperty(
        name="Export Rig & Animations",
        description="Export rig and animations",
        default=False,
    )

    one_material_ID: BoolProperty(
        name="One material ID",
        description="Export just one material per object",
        default=False,
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.panel_properties = bpy.props.PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.panel_properties
