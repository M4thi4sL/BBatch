from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .perforce_utils import get_perforce_settings_from_system


class BBATCH_AddonPreferences(AddonPreferences):
    bl_idname = "BBatch"

    # fmt:off
    enable_perforce: BoolProperty(
        name="Enable Perforce",
        description="Enable or disable Perforce integration",
        default=True
    )

    show_password: BoolProperty(
        name="Show Password",
        description="Reveal or hide the password",
        default=False
    )

    p4_server: StringProperty(
        name="Perforce Server",
        description="The address of the Perforce server (e.g., perforce:1666)",
        default="perforce:1666"
    )

    p4_user: StringProperty(
        name="Perforce User",
        description="Your Perforce username",
        default=""
    )

    p4_client: StringProperty(
        name="Perforce Client",
        description="Your Perforce workspace/client name",
        default=""
    )

    p4_password: StringProperty(
        name="Perforce Password",
        description="Your Perforce password (optional)",
        default="",
        subtype='PASSWORD'
    )

    p4_password_plain: StringProperty(
        name="Perforce Password (Plain)",
        description="Your Perforce password in plain text",
        default=""
    )

    connection_status: EnumProperty(
        name="Connection Status",
        description="Status of the last Perforce connection test",
        items=[
            ('NOT_TESTED', "Not Tested", ""),
            ('SUCCESS', "Success", ""),
            ('FAILED', "Failed", "")
        ],
        default='NOT_TESTED'
    )

    # fmt: on

    def draw(self, context):
        layout = self.layout

        # Check if we already have values; if not, auto-detect them
        if not self.p4_server or not self.p4_user or not self.p4_client:
            detected_settings = get_perforce_settings_from_system()
            self.p4_server = detected_settings.get("server", "perforce:1666") or ""
            self.p4_user = detected_settings.get("user", "") or ""
            self.p4_client = detected_settings.get("client", "") or ""

        # Toggle button to enable/disable Perforce
        layout.prop(self, "enable_perforce")

        # Create a box to contain Perforce settings
        box = layout.box()
        if self.enable_perforce:
            box.enabled = True
        else:
            box.enabled = False

        box.label(text="Perforce Settings")
        box.prop(self, "p4_server")
        box.prop(self, "p4_user")
        box.prop(self, "p4_client")
        box.prop(self, "p4_password")

        # Determine the icon based on the connection status
        if self.connection_status == "SUCCESS":
            icon = "CHECKMARK"
        elif self.connection_status == "FAILED":
            icon = "ERROR"
        else:
            icon = "FILE_REFRESH"

        # Add a "Test Connection" button
        box.operator("bbatch.test_perforce_connection", text="Test Connection", icon=icon)
