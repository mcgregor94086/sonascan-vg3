"""
CONSTANTS.py

CONSTANTS.py stores constants used by sonascan software.
"""

# imports
import os
import platform
import re
import socket
import subprocess
import uuid

# Local directory paths:
LOCAL_SCAN_DIR_ROOT_PATH = os.path.abspath('../_scans/')
LOCAL_UPLOAD_DIR_ROOT_PATH = os.path.abspath('../_uploaded/')
LOCAL_MODEL_ROOT_PATH = os.path.abspath('../_models/')
LOCAL_FAILED_ROOT_PATH = os.path.abspath('../_failed_scans/')
LOCAL_VIRTUAL_SCAN_DIR_ROOT_PATH = os.path.abspath('../_scans/VIRTUAL')

last_saved_value_file = os.path.abspath('../last_saved_values.py')


# Server directory paths
SERVER_HOSTNAME = 'scansteruser@cloud1.tri-di.com:'
SERVER_SCAN_DIR_ROOT_PATH = SERVER_HOSTNAME + 'cloud1.tri-di.com/_scans/'
SERVER_UPLOADED_DIR_ROOT_PATH = SERVER_HOSTNAME + 'cloud1.tri-di.com/_uploaded/'
SERVER_MODELED_DIR_ROOT_PATH = SERVER_HOSTNAME + 'cloud1.tri-di.com/_modeled/'
SERVER_FAILED_DIR_ROOT_PATH = SERVER_HOSTNAME + 'cloud1.tri-di.com/_failed_scans/'

# PATHS TO PROGRAMS  (MIGHT BE OS DEPENDENT!!!)
system_type = platform.system()
if system_type == "Darwin":  # MacOS X and iOS Systems only.  Use -f avfoundation to find USB cameras
    PATH_TO_MODEL_VIEWER_APP = os.path.abspath('../external_app_bin/macos64/meshlab.app')
    PATH_TO_OBJ_TO_STL_CONVERTOR = os.path.abspath('../external_app_bin/macos64/meshconv')
    PATH_TO_FFMPEG =  os.path.abspath('../external_app_bin/macos64/ffmpeg')
elif system_type == "Linux":  # Linux systems
    PATH_TO_MODEL_VIEWER_APP = os.path.abspath('../external_app_bin/linux64/meshlab.app')
    PATH_TO_OBJ_TO_STL_CONVERTOR = os.path.abspath('../external_app_bin/linux64/meshconv')
    machine_type = platform.machine()
    if "amd64" in machine_type:
        PATH_TO_FFMPEG =  os.path.abspath('../external_app_bin/linux64/ffmpeg-4.3-amd64-static/ffmpeg')
    elif "arm64" in machine_type:
        PATH_TO_FFMPEG = os.path.abspath('../external_app_bin/linux64/ffmpeg-4.3-arm64-static/ffmpeg')
    elif "armel" in machine_type:
        PATH_TO_FFMPEG = os.path.abspath('../external_app_bin/linux64/ffmpeg-4.3-armel-static/ffmpeg')
    elif "armhf" in machine_type:
        PATH_TO_FFMPEG = os.path.abspath('../external_app_bin/linux64/ffmpeg-4.3-armhf-static/ffmpeg')
    elif "i686" in machine_type:
        PATH_TO_FFMPEG = os.path.abspath('../external_app_bin/linux64/ffmpeg-4.3-i686-static/ffmpeg')
    else:
        print(machine_type, "This machine type is not supported")
        exit(-2)
elif system_type == "Windows":
    PATH_TO_MODEL_VIEWER_APP = os.path.abspath('../external_app_bin/win64/meshlab.exe')
    PATH_TO_OBJ_TO_STL_CONVERTOR = os.path.abspath('../external_app_bin/win64/meshconv.exe')
    PATH_TO_FFMPEG =  os.path.abspath('../external_app_bin/win64/ffmpeg.exe')
else:
    print(system_type,"This OS is not supported")
    exit(-1)

# end elif

# UNIQUE IDENTIFIERS USED FOR THIS SCANNER SYSTEM
HOSTNAME = socket.gethostname()
MAC_ID = ':'.join(re.findall('../..', '%012x' % uuid.getnode()))
# we should probably put a wifi network device or dongle inside the scanner to get a unique ID at some time
SCANNER_ID = HOSTNAME+"/"
LOCAL_SCAN_ID_DIR_PATH =  os.path.join( LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID  )

# GUI CONSTANTS
images_dir_path =   os.path.abspath('../images/')
# splash_icon =     os.path.join( images_dir_path,  "Sonautics-logo-banner.png")
warning_icon =      os.path.join( images_dir_path,  "warning-icon.png")
error_icon =        os.path.join( images_dir_path,  "Status-dialog-error-icon.png")
exiting_icon =      os.path.join( images_dir_path,  "Tomb-icon.png")
construction_icon = os.path.join( images_dir_path,  "Under-Construction-icon.png")
# small_logo =      os.path.join( images_dir_path,  "Sonautics_Logo_2019_Color_300x126.png")
small_logo =        os.path.join( images_dir_path,  "Sonautics_Logo_2019_Color_150x63.png")
splash_gif =        os.path.join( images_dir_path,  "self-test-animated-gif.gif")
# scan_button =     os.path.join( images_dir_path,  "sonascan-orange-scan-button.png")
scan_button =       os.path.join( images_dir_path,  "sonascan-scan-button.png")
# thumbnail =       os.path.join( images_dir_path,  "Sonautics-thumbnail-192x108.png")
thumbnail =         os.path.join( images_dir_path,  "status-ready.png")
status_ready =      os.path.join( images_dir_path,  "status-ready.png")
status_no_scanner = os.path.join( images_dir_path,  "status-no-scanner.png")
status_virtual_scanner = os.path.join( images_dir_path,  "status-virtual-scan.png")
ialert  =           os.path.join( images_dir_path, "ialert.png" )
igear =             os.path.join( images_dir_path, "igear.png" )
iquest =            os.path.join( images_dir_path,  "iquest.png" )
iupload =           os.path.join( images_dir_path,  "iupload.png" )
iwifi_bad =         os.path.join( images_dir_path,  "iwifi-bad,png" )
iwifi_good =        os.path.join( images_dir_path,  "iwifi-good.png" )


def syscmd(cmd, encoding=''):
    """
    syscmd(cmd, encoding='')

    Runs a command on the system, waits for the command to finish, and then
    returns the text output of the command. If the command produces no text
    output, the command's return code will be returned instead.
    """
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         close_fds=True)
    p.wait()
    output = p.stdout.read()
    if len(output) > 1:
        if encoding:
            return output.decode(encoding)
        else:
            return output
    return p.returncode


def save_last_form_values(last_saved_value_file, from_email, to_email, consumer_id, consumer_name, order_details,
                          monitor_scanning_flag, monitor_modeling_flag, monitor_upload_flag):
    if monitor_scanning_flag:
        monitor_scanning_str = "True"
    else:
        monitor_scanning_str = "False"

    if monitor_modeling_flag:
        monitor_modeling_str = "True"
    else:
        monitor_modeling_str = "False"

    if monitor_upload_flag:
        monitor_uploads_str = "True"
    else:
        monitor_uploads_str = "False"

    f = open(last_saved_value_file, "w+")
    f.write("from_email = '" + from_email + "'\n")
    f.write("to_email = '" + to_email + "'\n")
    f.write("consumer_id = '" + consumer_id + "'\n")
    f.write("consumer_name = '" + consumer_name + "'\n")
    f.write("order_details = '" + order_details + "'\n")
    f.write("monitor_scanning_flag = '" + monitor_scanning_str + "'\n")
    f.write("monitor_modeling_flag = '" + monitor_modeling_str + "'\n")
    f.write("monitor_upload_flag  = '" + monitor_uploads_str + "'\n")
    f.close()
    return last_saved_value_file
