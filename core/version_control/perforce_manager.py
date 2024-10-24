import subprocess
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)


class PerforceManager:
    """Handles interactions with the Perforce version control system."""

    def check_connection(self) -> bool:
        """Check if there is a valid connection to the Perforce server."""
        try:
            result = subprocess.run(["p4", "info"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Connected to Perforce server.")
                return True
            logger.error(f"Perforce connection failed: {result.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to Perforce: {e}")
            return False

    def file_exists(self, filepath: str) -> bool:
        """Check if the file already exists in the export folder."""
        return os.path.isfile(filepath)

    def is_file_checked_in(self, filepath: str) -> bool:
        """Check if the file is checked into Perforce."""
        try:
            result = subprocess.run(["p4", "fstat", filepath], capture_output=True, text=True)
            return result.returncode == 0 and "depotFile" in result.stdout
        except Exception as e:
            logger.error(f"Error checking file status in Perforce: {e}")
            return False

    def checkout_file(self, filepath: str):
        """Check out the file in Perforce."""
        result = subprocess.run(["p4", "edit", filepath], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Checked out: {filepath}")
        else:
            if "already opened for edit" in result.stderr:
                logger.warning(f"File '{filepath}' is already checked out by another user.")
                raise Exception(f"Cannot check out '{filepath}': It is already checked out by another user.")
            logger.error(f"Error checking out file: {result.stderr}")
            raise Exception(f"Error checking out '{filepath}': {result.stderr}")
