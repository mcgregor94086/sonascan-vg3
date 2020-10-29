"""
new_scan_id.py

new_scan_id.py contains all the GUI elements used by Sonascan
"""

# global imports
import os
import subprocess
from datetime import datetime

# local imports
from src.CONSTANTS import SCANNER_ID, SERVER_HOSTNAME, LOCAL_SCAN_DIR_ROOT_PATH, LOCAL_UPLOAD_DIR_ROOT_PATH, \
    LOCAL_MODEL_ROOT_PATH, LOCAL_FAILED_ROOT_PATH


def get_new_scan_id():
    # SCAN_ID DEPENDENT PATHS
    # Varies with each scan, but constant for life of a scan
    # The short_scan_id is used to ensure that each scan gets a unique identifier for this machine
    short_scan_id = datetime.today().strftime('%Y%m%d%H%M%S')
    # the full_scan_id is composed of the unique SCANNER_ID (above) and the short_scan_id ensuring a globally unique id
    full_scan_id = SCANNER_ID + short_scan_id
    return short_scan_id, full_scan_id

def create_scan_dirs():
    # if _scans, _uploaded, _models, and _failed folders do not exist, create them locally and remotely
    for directory in [LOCAL_SCAN_DIR_ROOT_PATH,
                      LOCAL_UPLOAD_DIR_ROOT_PATH, LOCAL_MODEL_ROOT_PATH, LOCAL_FAILED_ROOT_PATH]:
        scanner_directory = ( os.path.join(directory, SCANNER_ID ))
        source_dir = os.path.abspath(scanner_directory)
        source_basename = os.path.basename(scanner_directory)
        dest_dir = SERVER_HOSTNAME + 'cloud1.tri-di.com/' + scanner_directory
        if not os.path.exists( scanner_directory ):
            print("created local ", source_dir)
            os.makedirs( scanner_directory )
            try:
                rsync_cmd = subprocess.run(['/usr/bin/rsync', '-e',
                                            'ssh -i ~/.ssh/tridi-mpl.pem', "-aR",
                                            "--stats", "--progress",
                                            "--ignore-existing",
                                               # "--remove-source-files",
                                            source_dir, dest_dir],
                                            universal_newlines=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                print("created server side ", dest_dir)
                return True
            except Exception as e:
                print("Unable create server side directory", dest_dir)
                print(rsync_cmd.stderr)
                return False

def main():
    print(get_new_scan_id())
    create_scan_dirs()

if __name__ == "__main__":
    # execute only if run as a script
    main()
