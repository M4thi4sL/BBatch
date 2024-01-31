import zipfile
import os
import re


def get_bl_info_name(init_file_path):
    with open(init_file_path, "r") as file:
        content = file.read()
        match = re.search(r'"name": "(.+?)"', content)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Unable to extract addon name from {init_file_path}")


def get_bl_info_version(init_file_path):
    with open(init_file_path, "r") as file:
        content = file.read()
        match = re.search(r'"version": \((\d+), (\d+), (\d+)\)', content)
        if match:
            return ".".join(map(str, map(int, match.groups())))
        else:
            raise ValueError(f"Unable to extract version from {init_file_path}")


def zip_files_with_version(init_file_path, root_directory):
    # Increment the version in __init__.py
    addon_name = get_bl_info_name(init_file_path)
    version = get_bl_info_version(init_file_path)

    # Create the .builds directory if it doesn't exist
    output_directory = ".builds"
    os.makedirs(output_directory, exist_ok=True)

    # Combine the directory and filename for the ZIP file
    zip_filename = f"{addon_name}_{version}.zip"
    zip_filepath = os.path.join(output_directory, zip_filename)

    with zipfile.ZipFile(zip_filepath, "w") as zip_file:
        # Walk through the root directory and its subdirectories
        for foldername, _, filenames in os.walk(root_directory):
            for filename in filenames:
                # Check if the file has a .py or .md extension or is LICENSE, exclude build.py
                if (
                    filename.endswith((".py", ".md", ".png"))
                    or filename.upper() == "LICENSE"
                ) and filename != "build.py":
                    # Create the relative path from the root directory
                    relative_path = os.path.relpath(
                        os.path.join(foldername, filename), root_directory
                    )
                    # Add the file to the ZIP archive with its relative path
                    zip_file.write(
                        os.path.join(foldername, filename),
                        os.path.join(addon_name, relative_path),
                    )


if __name__ == "__main__":
    # Example usage:
    # Specify the path to __init__.py and the root directory to search for Python files
    init_file_path = "./__init__.py"
    root_directory = "./"

    # Call the function to create the ZIP file with version in the .builds directory
    zip_files_with_version(init_file_path, root_directory)

    print("Files zipped successfully with incremented version.")
