import subprocess
import re


def get_perforce_settings_from_system():
    """
    Detects and returns Perforce settings (server, user, client) from the system.
    Cleans up output to remove extra information like config paths in parentheses.
    Returns a dictionary with keys: 'server', 'user', and 'client'.
    """
    settings = {"server": None, "user": None, "client": None}

    try:
        # Run `p4 set` to get all Perforce settings
        result = subprocess.run(["p4", "set"], capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            # Parse each line for P4PORT, P4USER, and P4CLIENT
            for line in result.stdout.splitlines():
                if "P4PORT" in line:
                    settings["server"] = clean_perforce_value(extract_value_from_line(line))
                elif "P4USER" in line:
                    settings["user"] = clean_perforce_value(extract_value_from_line(line))
                elif "P4CLIENT" in line:
                    settings["client"] = clean_perforce_value(extract_value_from_line(line))

    except Exception as e:
        print(f"Error detecting Perforce settings: {e}")

    return settings


def extract_value_from_line(line):
    """
    Extracts the value from a line in the format 'P4PORT=server_address'.
    """
    match = re.search(r"=(.+)", line)
    if match:
        return match.group(1).strip()
    return None


def clean_perforce_value(value):
    """
    Cleans the Perforce value by removing any text within parentheses and trimming whitespace.
    """
    # Remove text in parentheses
    cleaned_value = re.sub(r"\s*\(.*?\)\s*", "", value)
    return cleaned_value.strip()
