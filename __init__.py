# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "BBatch",
    "author": "M4thi4sL",
    "description": "export assets to a specified folder",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "location": "BBatch panel",
    "warning": "",
    "category": "Import-Export",
}

from . import auto_load

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .core.panel import *
from .core.operators import *

auto_load.init()

bpy.types.Scene.export_folder = StringProperty(
    name="Export folder",
    subtype="DIR_PATH",
    description="Directory to export the fbx files into",
    default=".\\",
)

bpy.types.Scene.center_transform = BoolProperty(
    name="Center transform",
    description="Set the pivot point of the object to the center",
    default=True,
)

bpy.types.Scene.apply_transform = BoolProperty(
    name="Apply transform",
    description="Applies scale and transform (Experimental)",
    default=True,
)

bpy.types.Scene.export_smoothing = EnumProperty(
    name="Smoothing",
    description="Defines the export smoothing information",
    items=(
        ("EDGE", "Edge", "Write edge smoothing", 0),
        ("FACE", "Face", "Write face smoothing", 1),
        ("OFF", "Normals Only", "Write normals only", 2),
    ),
    default="OFF",
)


bpy.types.Scene.show_options = BoolProperty(default=False)

bpy.types.Scene.export_animations = BoolProperty(
    name="Export Rig & Animations",
    description="Export rig and animations",
    default=False,
)

bpy.types.Scene.one_material_ID = BoolProperty(
    name="One material ID",
    description="Export just one material per object",
    default=False,
)


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()
