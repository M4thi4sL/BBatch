import bpy
import subprocess
import os


def checkout_file(filepath):
    """
    Checks out a file in Perforce to make it writable.
    """
    if os.path.exists(filepath):
        # Run the Perforce command to check out the file
        result = subprocess.run(["p4", "edit", filepath], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error checking out file: {result.stderr}")
        else:
            print(f"File checked out: {filepath}")
    else:
        print(f"File does not exist yet: {filepath} - it will be added on export.")


def export_with_perforce_integration(context, obj, export_format):
    """
    Integrates Perforce file checkout before exporting.
    """
    # Define the file path based on the object and format
    export_directory = context.scene.export_directory
    filepath = os.path.join(export_directory, f"{obj.name}{export_format}")

    # Check out the file in Perforce before exporting
    checkout_file(filepath)

    # Call the export function (example for FBX)
    bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True, object_types={"MESH", "ARMATURE", "EMPTY"}, path_mode="ABSOLUTE", check_existing=False)
