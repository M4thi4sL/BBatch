import os
import importlib
import bpy
from bpy.props import EnumProperty

from .base_export import Base_Export


exporters_dir = os.path.dirname(os.path.abspath(__file__))
enum_items = []
module_members = []
py_files = [
    f[:-3]
    for f in os.listdir(exporters_dir)
    if f.endswith(".py") and not f.startswith("__")
]

# Import all classes from the Python files
for module_name in py_files:
    module_path = f".exporters.{module_name}"
    module = importlib.import_module(
        f"{__package__}.{module_name}", package="{module_path}"
    )

    # Filter for callable attributes (classes, functions, etc.)
    module_members.extend(
        [
            getattr(module, name)
            for name in dir(module)
            if (
                isinstance(getattr(module, name), type)
                and issubclass(getattr(module, name), Base_Export)
                and getattr(module, name) != Base_Export
            )
        ]
    )
    # Update globals with module members
    globals().update(
        {
            getattr(module, name).__name__: getattr(module, name)
            for name in dir(module)
            if callable(getattr(module, name))
        }
    )

for member in module_members:
    enum_items.append(
        (
            member.formats[0],
            member.formats[0].upper(),
            f"{member.formats[0]} format",
        )
    )


# Define __all__
__all__ = [name for name in globals() if not name.startswith("_")]

# Define export enum
bpy.types.Scene.export_file_format = bpy.props.EnumProperty(
    items=enum_items,
    default=".fbx",
)
