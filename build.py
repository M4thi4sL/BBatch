import os
import sys
import subprocess
import requests
import logging
import colorlog
import re

from fnmatch import fnmatch
from enum import Enum
from zipfile import ZipFile, ZIP_DEFLATED


# Set up the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a color formatter
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)

# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

IGNORE_PATTERNS = [
    "*/__pycache__/*",
    "*/.git/*",
    "*/.github/*",
    "*/.idea/*",
    "*/.venv/*",
    "*/.vscode/*",
    "*/.gitignore",
    "*/.gitattributes",
    "*/.build/*",
    "*/build.py",
    "*/.output/*",
]

NAME = os.getenv("NAME")


class IncrementType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


def get_branch_name():
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving branch name: {e}")
        raise


def increment_tag(increment=IncrementType.PATCH):
    try:
        latest_tag = get_latest_tag()
        parts = latest_tag.split(".")
        major_version, minor_version, patch_version = map(int, parts)

        if increment == IncrementType.MAJOR:
            major_version += 1
            minor_version = 0
            patch_version = 0
        elif increment == IncrementType.MINOR:
            minor_version += 1
            patch_version = 0
        elif increment == IncrementType.PATCH:
            patch_version += 1
        else:
            raise ValueError(
                "Invalid increment type. Please choose from IncrementType.MAJOR, IncrementType.MINOR, or IncrementType.PATCH."
            )

        new_tag = f"{major_version}.{minor_version}.{patch_version}"

        push_tag(new_tag)
        return new_tag

    except subprocess.CalledProcessError as e:
        logger.error(msg=f"Error incrementing tag: {e}")
        raise


def get_latest_tag():
    try:
        output = subprocess.check_output(["git", "ls-remote", "--tags"]).decode("utf-8")
        tags = [line.split("\t")[1].split("/")[-1] for line in output.splitlines()]
        sorted_tags = sorted(tags, key=sort_tags_by_version, reverse=True)
        return sorted_tags[0] if sorted_tags else "1.0.0"
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving latest tag: {e}")
        return "1.0.0"  # Default to 1.0.0 if an error occurs or no tags are found


def sort_tags_by_version(tag):
    # Split the tag into numeric and non-numeric parts
    parts = re.split(r"(\d+)", tag)
    # Convert numeric parts to integers for proper sorting
    parts[1::2] = map(int, parts[1::2])
    return parts


def push_tag(tag):
    try:
        subprocess.run(["git", "tag", tag])
        subprocess.run(["git", "push", "origin", tag])
        logger.info(f"Tag {tag} pushed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error pushing tag {tag}: {e}")
        raise


def zip_directory(directory, zip_file):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file != zip_file.filename and not any(
                fnmatch(os.path.join(root, file), pattern)
                for pattern in IGNORE_PATTERNS
            ):
                zip_file.write(os.path.join(root, file))


def create_zip_file(directory, branch, tag):
    zip_path = f"./.build/{NAME}-{tag}.zip"
    if not os.path.exists("./.build"):
        os.makedirs("./.build")
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zipf:
        zip_directory(directory, zipf)
    return zip_path


def upload_release_asset(upload_url, zip_path):
    filename = os.path.basename(zip_path)
    headers = {
        "Authorization": f'token {os.getenv("GITHUB_TOKEN")}',
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/zip",
    }
    params = {"name": filename}
    with open(zip_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, params=params, data=f)
        if response.status_code == 201:
            logger.info("Asset uploaded successfully.")
        else:
            logger.error(
                f"Failed to upload asset. Status code: {response.status_code}, {response.text}"
            )


def create_github_release(tag, branch, zip_path):
    github_token = os.getenv("GITHUB_TOKEN")
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")

    release_tag = f"{tag}"
    release_title = f"{NAME} v{release_tag}"
    release_body = f"[BUILD] {branch} tagged:{tag}"

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "tag_name": release_tag,
        "target_commitish": branch,
        "name": release_title,
        "body": release_body,
        "draft": False,
        "prerelease": False,
        "generate_release_notes": False,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        logger.error(
            f"Failed to create GitHub release. Status code: {response.status_code},{response.text}"
        )
    else:
        release_id = response.json().get("id")
        upload_url = f"https://uploads.github.com/repos/{repo_owner}/{repo_name}/releases/{release_id}/assets"
        upload_release_asset(upload_url, zip_path)


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py [major|minor|patch]")
        return

    increment_type = sys.argv[1].lower()
    if increment_type not in ["major", "minor", "patch"]:
        print("Invalid increment type. Please choose from major, minor, or patch.")
        return

    branch = get_branch_name()
    tag = increment_tag(IncrementType[increment_type.upper()])
    zip_path = create_zip_file(f"{NAME}", branch, tag)
    create_github_release(tag, branch, zip_path)


if __name__ == "__main__":
    main()
