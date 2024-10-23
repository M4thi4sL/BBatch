import bpy
import subprocess


class BBATCH_OT_TestPerforceConnection(bpy.types.Operator):
    bl_idname = "bbatch.test_perforce_connection"
    bl_label = "Test Perforce Connection"
    bl_description = "Test connection to the Perforce server using the configured settings"

    def execute(self, context):
        # Retrieve the Perforce settings from the preferences
        addon_name = "BBatch"  # Make sure this matches bl_info['name'] in __init__.py
        prefs = context.preferences.addons[addon_name].preferences
        server = prefs.p4_server
        user = prefs.p4_user
        client = prefs.p4_client
        password = prefs.p4_password

        # Set environment variables for Perforce
        subprocess.run(["p4", "set", f"P4PORT={server}"], capture_output=True, text=True)
        subprocess.run(["p4", "set", f"P4USER={user}"], capture_output=True, text=True)
        subprocess.run(["p4", "set", f"P4CLIENT={client}"], capture_output=True, text=True)

        # Attempt to log in to Perforce
        try:
            login_process = subprocess.run(["p4", "login"], input=password + "\n", capture_output=True, text=True)

            if login_process.returncode != 0:
                self.report({"ERROR"}, f"Perforce login failed: {login_process.stderr}")
                prefs.connection_status = "FAILED"
                return {"CANCELLED"}

            # Test the connection with 'p4 info' to verify it's successful
            info_process = subprocess.run(["p4", "info"], capture_output=True, text=True)
            if info_process.returncode == 0:
                self.report({"INFO"}, "Perforce connection successful!")
                prefs.connection_status = "SUCCESS"
                return {"FINISHED"}
            else:
                self.report({"ERROR"}, f"Error connecting to Perforce: {info_process.stderr}")
                prefs.connection_status = "FAILED"
                return {"CANCELLED"}

        except Exception as e:
            self.report({"ERROR"}, f"An error occurred: {str(e)}")
            prefs.connection_status = "FAILED"
            return {"CANCELLED"}
