import subprocess


def connect_to_perforce(server, user, client, password=None):
    """
    Establishes a connection to the Perforce server using the given credentials.
    Sets up environment variables and logs into the Perforce server.
    """
    # Set environment variables for Perforce
    subprocess.run(["p4", "set", f"P4PORT={server}"])
    subprocess.run(["p4", "set", f"P4USER={user}"])
    subprocess.run(["p4", "set", f"P4CLIENT={client}"])

    # Attempt to log in to Perforce
    if password:
        login_process = subprocess.run(["p4", "login"], input=password.encode(), capture_output=True, text=True)
    else:
        login_process = subprocess.run(["p4", "login", "-s"], capture_output=True, text=True)

    # Check if the login was successful
    if login_process.returncode == 0:
        print("Perforce login successful.")
        return True
    else:
        print(f"Perforce login failed: {login_process.stderr}")
        return False


def checkout_file(filepath):
    """
    Checks out a file in Perforce to make it writable.
    """
    result = subprocess.run(["p4", "edit", filepath], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error checking out file: {result.stderr}")
    else:
        print(f"File checked out: {filepath}")
