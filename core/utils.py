import bpy


def get_object_loc(obj):
    """Return a copy of the object's location."""
    if obj is None:
        raise ValueError("Provided object is None.")
    return obj.location.copy()


def set_object_to_loc(obj, loc):
    """Set the location of an object."""
    if obj is None:
        raise ValueError("Provided object is None.")
    obj.location = loc
    print(f"Set location of '{obj.name}' to {loc}.")


def get_children(obj):
    """Recursively retrieve all children of the specified object."""
    if obj is None:
        raise ValueError("Provided parent object is None.")

    children = []
    for ob in bpy.data.objects:
        if ob.parent == obj:
            children.append(ob)
            children.extend(get_children(ob))
    return children


def get_cursor_loc(context):
    """Return the current cursor location."""
    return context.scene.cursor.location.copy()


def selected_to_cursor():
    """Snap selected objects to the cursor location."""
    bpy.ops.view3d.snap_selected_to_cursor()
    print("Snapped selected objects to the cursor.")


def set_cursor_loc(context, loc: tuple):
    """Set the 3D cursor location."""
    context.scene.cursor.location = loc
    print(f"Set cursor location to {loc}.")


def get_addon_preferences(addon_name: str):
    """Retrieve the preferences for the specified addon."""
    try:
        return bpy.context.preferences.addons[addon_name].preferences
    except KeyError:
        raise Exception(f"Addon '{addon_name}' not found in preferences.")
