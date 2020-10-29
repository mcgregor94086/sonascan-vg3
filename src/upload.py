"""
upload.py

upload.py manages uploading LOCAL_SCAN_ID_DIRs to SERVER_SCAN_ID_DIRs, and once uploaded, it
moves the LOCAL_SCAN_ID_DIR to a LOCAL_MODEL_ID_DIR.
"""


# GLOBAL PACKAGE IMPORTS
import os
from glob import glob

import shutil
import subprocess
import time

import paramiko
# from ffmpeg import LOCAL_SCAN_ID_DIR_PATH

from src.CONSTANTS import LOCAL_SCAN_DIR_ROOT_PATH, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, \
    SERVER_SCAN_DIR_ROOT_PATH, SERVER_UPLOADED_DIR_ROOT_PATH
#from debugging import get_line_number, FILENAME
from src.forge import PEM_KEY, PEM_KEY_FILE


def scandir_upload(src_dir, dest_dir, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, window ):
    """
    scandir_upload(src_dir, dest_dir,LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID) is used to upload scan directories to the Sonautics Cloud server

    scandir_upload(src_dir, dest_dir, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID) is used to upload scan directories to the Sonautics Cloud server
    """
    tic = time.perf_counter()
    source_dir = os.path.abspath(src_dir)
    source_basename = os.path.basename(source_dir)
    print()
    print("source_basename=", source_basename, ".")
    print("upload", source_dir, "->", dest_dir)
    dir_listing = os.listdir(source_dir)

    print(len(source_dir), "files to source_dir", source_dir)
    PEM_KEY_FILE
    window.FindElement('_ACTION_STATUS_LINE_3_').Update(
        f"Uploading {source_basename}")
    try:
        rsync_cmd = subprocess.run(['/usr/bin/rsync', '-e',
                                  f'ssh -i {PEM_KEY_FILE}', "-irah", "--stats", "--progress",
                                  "--ignore-existing",
                                  # "--remove-source-files",
                                  source_dir, dest_dir],
                                 universal_newlines=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    except Exception as e:
        print(rsync_cmd)
        print("Error", repr(e))
        print("Unable to upload local scan directory", source_dir, "to ", dest_dir, "on server. Will try again later.")
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"Unable to upload {source_basename}")
        print(rsync_cmd.stderr)
        return False

    # If we fall through to here, there was no error,
    # so as each file is uploaded there should be data coming in on the stdout.PIPE

    print(rsync_cmd.stdout)
    if not rsync_cmd.stderr:
        print("Uploaded scan_id:", source_basename)

        upload_dir = os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID)
        new_path = shutil.move(source_dir, upload_dir)
        toc = time.perf_counter()
        print(f"Upload Complete for {source_basename} in: {toc - tic:0.0f} seconds")
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"Uploaded {source_basename} in: {toc - tic:0.0f} seconds")

        return dest_dir
    else:
        print("Server Connection Error:")
        print(rsync_cmd)
        print(rsync_cmd.stderr)
        # print("Unable to upload local scan directory", source_dir, "to ", dest_dir, "on server. Will try again later.")
        print("Unable to upload local scan directory to Sonautics Cloud Server.")
        print("Scan Saved.  Will try uploading again later.")
        toc = time.perf_counter()
        print(f"Unable to upload {source_basename} in: {toc - tic:0.0f} seconds")
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"Unable to upload {source_basename} in: {toc - tic:0.0f} seconds")
        return False


def test_rsync():
    """
    test_rsync() is used to test if there is connectivity and files waiting for upload to Sonautics Cloud server

    test_rsync() is used to test if there is connectivity and files waiting for upload to Sonautics Cloud server
    """
    tic = time.perf_counter()
    source_dir = LOCAL_SCAN_DIR_ROOT_PATH
    dest_dir = SERVER_SCAN_DIR_ROOT_PATH
    try:  # --dry-run does NOT actually transfer files, but it does determine if there is a connection, and how many files would be transfered
        test_rsync_cmd = subprocess.run(
            ['/usr/bin/rsync', '-e', 'ssh -i ~/.ssh/tridi-mpl.pem', "--dry-run", "-irah", "--stats",
             "--remove-source-files", "--ignore-existing",
             source_dir, dest_dir],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if not test_rsync_cmd.stderr:
            # print("stdout=", test_rsync_cmd.stdout)
            print("stderr=", test_rsync_cmd.stderr)
            toc = time.perf_counter()
            print(f"Server Connection found in: {toc - tic:0.0f} seconds")
            return dest_dir   # THIS IS THE TRUE CASE, and returns the directory that needs to be uploaded.
        else:
            print("Server Connection Error:")
            # print("Unable to upload local scan directory", source_dir, "to ", dest_dir, "on server. Will try again later.")
            print("Unable to upload local scan directory to Sonautics Cloud Server.")
            print("Scan Saved.  Will try uploading again later.")
            # print(test_rsync_cmd.stderr)
            toc = time.perf_counter()
            print(f"No Server Connection found in: {toc - tic:0.0f} seconds")
            return False
    except Exception as e:
        print("Error", repr(e))
        print("Unable to upload local scan directory", source_dir, "to ", dest_dir, "on server. Will try again later.")
        print(test_rsync_cmd.stderr)
        toc = time.perf_counter()
        print(f"Problem with Server Connection found in: {toc - tic:0.0f} seconds")
        return (False)


def scan_root_sync(window):
    """
    scan_root_sync () is used to sync ALL upload scan files and directories to the Sonautics Cloud server

    scan_root_sync () is used to sync ALL upload scan files and directories to the Sonautics Cloud server
    """
    tic = time.perf_counter()
    dest_dir = SERVER_SCAN_DIR_ROOT_PATH
    source_dir_root =os.path.join( LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID )
    print("source_dir = ", source_dir_root)
    scandirs_to_upload = glob(source_dir_root + "/*/")
    number_of_scanddirs_to_upload = len(scandirs_to_upload)
    if number_of_scanddirs_to_upload == 0:
        print("Done Uploading all ScanDirs")
        toc = time.perf_counter()
        print(f"No ScanDirs waiting for upload found in: {toc - tic:0.0f} seconds")
        return scandirs_to_upload
    print(number_of_scanddirs_to_upload, "scandirs to upload", scandirs_to_upload)
    for source_dir in scandirs_to_upload:
        scanID = source_dir.rsplit('/', 2)[1]
        print("uploading", scanID)
        scandir_upload(source_dir, dest_dir, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, window)
    toc = time.perf_counter()
    print(f"{number_of_scanddirs_to_upload} ScanDirs uploaded in: {toc - tic:0.0f} seconds")
    return scandirs_to_upload


def move_scandir_to_upload_dir_on_server(full_scan_id):
    tic = time.perf_counter()
    source_dir = SERVER_SCAN_DIR_ROOT_PATH + full_scan_id
    dest_dir   = SERVER_UPLOADED_DIR_ROOT_PATH + full_scan_id

    remote_userid = 'scansteruser'
    server_hostname = 'cloud1.tri-di.com'
    # pem_key = os.path.normpath(PEM_KEY)

    cmd = "/bin/mv _scans/" + full_scan_id + ' _uploaded/'

    # private_key = paramiko.RSAKey.from_private_key_file(pem_key)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=server_hostname, username=remote_userid, pkey=PEM_KEY)

    print(f"preparing to copy {source_dir} to {dest_dir}")
    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
        print (ssh_stdout)
        print(ssh_stderr)
        return(True)
    except Exception as e:
        print("Error", repr(e))
        print("Unable to move {full_scan_id} from _scans to +uploaded on server")
        print (ssh_stdout)
        print(ssh_stderr)
        return(False)


def main():
    """
        main()

        main() runs all the commands to take a scan and process it (with no GUI)
        """
    tic = time.perf_counter()

    uploaded_dest_dir = scandir_upload(LOCAL_SCAN_ID_DIR_PATH, SERVER_SCAN_DIR_PATH, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID)
    if uploaded_dest_dir != False:
        print(uploaded_dest_dir, 'was successfully uploaded.')
    else:
        # There is no directory_path, and thus no images to process
        exit(4)

    # Now that we have uploaded the current scan, we will attempt to finish uploading any previous _scans that
    # did not complete earlier (probably due to no connection to server at the earlier time)
    scan_root_sync()

    toc = time.perf_counter()
    duration_in_min = (toc - tic) / 60
    print(f"Completed Scan, upload and submitting model  in: {duration_in_min:0.2f} minutes")
    return


if __name__ == "__main__":
    # execute only if run as a script
    main()
