#!/usr/bin/env python3

import os
import sys
import time
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('hosts-manager')

# Constants
HOSTS_MARKER_START = '# ================ hosts manager start ================'
HOSTS_MARKER_END = '# ================ hosts manager end ================'
DEFAULT_HOSTS_FILE = '/data2/code/hosts-manager/hosts'
SYSTEM_HOSTS_FILE = '/etc/hosts'
DEFAULT_INTERVAL = 60  # seconds


def read_custom_hosts(hosts_file_path):
    """
    Read the custom hosts file and extract the content between markers.
    """
    try:
        with open(hosts_file_path, 'r') as f:
            content = f.read()

        # Find the content between markers
        start_idx = content.find(HOSTS_MARKER_START)
        end_idx = content.rfind(HOSTS_MARKER_END)

        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            logger.error(f"Markers not found or in wrong order in {hosts_file_path}")
            return None

        # Extract the content between markers (including the markers)
        hosts_section = content[start_idx:end_idx + len(HOSTS_MARKER_END)]
        return hosts_section
    except Exception as e:
        logger.error(f"Error reading hosts file {hosts_file_path}: {e}")
        return None


def read_system_hosts():
    """
    Read the current system hosts file.
    """
    try:
        with open(SYSTEM_HOSTS_FILE, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading system hosts file: {e}")
        return None


def update_system_hosts(custom_hosts_content):
    """
    Update the system hosts file with the custom hosts content.
    Preserves any content outside the markers.
    """
    try:
        system_hosts = read_system_hosts()
        if system_hosts is None:
            return False

        # Check if markers already exist in the system hosts file
        start_idx = system_hosts.find(HOSTS_MARKER_START)
        end_idx = system_hosts.rfind(HOSTS_MARKER_END)

        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            # Replace existing section
            new_content = (
                system_hosts[:start_idx] +
                custom_hosts_content +
                system_hosts[end_idx + len(HOSTS_MARKER_END):]
            )
        else:
            # Append to the end
            new_content = system_hosts.rstrip() + "\n\n" + custom_hosts_content

        # Create a backup of the current hosts file
        backup_path = f"{SYSTEM_HOSTS_FILE}.bak.{int(time.time())}"
        with open(backup_path, 'w') as f:
            f.write(system_hosts)
        logger.info(f"Backup created at {backup_path}")

        # Write the new content to a temporary file
        temp_file = f"{SYSTEM_HOSTS_FILE}.tmp"
        with open(temp_file, 'w') as f:
            f.write(new_content)

        # Use sudo to move the temporary file to the system hosts file
        result = subprocess.run(
            ['sudo', 'mv', temp_file, SYSTEM_HOSTS_FILE],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Failed to update system hosts file: {result.stderr}")
            return False

        logger.info("System hosts file updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating system hosts file: {e}")
        return False


def run_daemon(hosts_file_path, interval):
    """
    Run as a daemon, periodically checking for changes and updating.
    """
    logger.info(f"Starting hosts manager daemon with interval {interval} seconds")
    logger.info(f"Monitoring hosts file: {hosts_file_path}")

    last_modified = 0

    while True:
        try:
            current_modified = os.path.getmtime(hosts_file_path)

            # Check if the file has been modified since last check
            if current_modified > last_modified:
                logger.info(f"Hosts file modified, updating system hosts")
                custom_hosts = read_custom_hosts(hosts_file_path)

                if custom_hosts:
                    update_system_hosts(custom_hosts)
                    last_modified = current_modified

            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in daemon loop: {e}")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description='Linux hosts file manager')
    parser.add_argument(
        '--hosts-file',
        default=DEFAULT_HOSTS_FILE,
        help=f'Path to the custom hosts file (default: {DEFAULT_HOSTS_FILE})'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=DEFAULT_INTERVAL,
        help=f'Update check interval in seconds (default: {DEFAULT_INTERVAL})'
    )
    parser.add_argument(
        '--update-once',
        action='store_true',
        help='Update once and exit'
    )

    args = parser.parse_args()

    # Validate hosts file path
    hosts_file_path = Path(args.hosts_file)
    if not hosts_file_path.exists():
        logger.error(f"Hosts file not found: {hosts_file_path}")
        return 1

    # Check if running as root or with sudo
    if os.geteuid() != 0:
        logger.warning("Not running as root. You may be prompted for sudo password when updating hosts file.")

    if args.update_once:
        logger.info("Running in one-time update mode")
        custom_hosts = read_custom_hosts(hosts_file_path)
        if custom_hosts:
            update_system_hosts(custom_hosts)
    else:
        run_daemon(hosts_file_path, args.interval)

    return 0


if __name__ == '__main__':
    sys.exit(main())
