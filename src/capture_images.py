"""
capture_images.py

capture_images.py contains all the code specific to capturinng camera images from the sonascanner
"""

# global imports
import asyncio
import sys
import webbrowser
from datetime import datetime
# from inspect import currentframe, getframeinfo
import os
from os.path import basename
from PIL import Image

import paramiko
import platform
import PySimpleGUI as sg  # pip3 install --upgrade PySimpleGUI PySImpleGUI creates our GUI
# import re
# import socket
import subprocess
import time
from timeit import default_timer
import urllib.parse
# import uuid
import requests
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment

# local imports
from src.index_maker import scandir_index_maker
# from debugging import get_line_number, FILENAME
from src.CONSTANTS import SCANNER_ID, LOCAL_MODEL_ROOT_PATH, PATH_TO_FFMPEG, syscmd, \
    PATH_TO_MODEL_VIEWER_APP, LOCAL_VIRTUAL_SCAN_DIR_ROOT_PATH, LOCAL_SCAN_DIR_ROOT_PATH
# from GUI_Layouts import col1, settings, info_panel, layout

from src.last_saved_values import from_email
from src.last_saved_values import to_email

# from last_saved_values import consumer_id
# from last_saved_values import consumer_name
# from last_saved_values import order_details
# from last_saved_values import monitor_scanning_flag
# from last_saved_values import monitor_upload_flag
# from last_saved_values import monitor_processing_flag

# DEFAULT VALUES USED IN TESTING
FROM_EMAIL = 'devops@sonascan.com'
TO_EMAIL = 'scott@sonautics.com'
from_email = 'devops@sonautics.com'
to_email = 'devops@sonautics.com'
consumer_id = 'test'
order_details = "test details"

# EXCLUDED_CAMERAS:
# ffmpeg -device-list returns output containing a list of devices in the following format:
# [DeviceClass indev @ 0x7fd4e9721740] DeviceClass video devices:
# [DeviceClass indev @ 0x7fd4e9721740] [0] FaceTime HD Camera (Built-in)
# [DeviceClass indev @ 0x7fd4e9721740] [1] UNIQUESKY_CAR_CAMERA #7
# [DeviceClass indev @ 0x7fd4e9721740] [2] UNIQUESKY_CAR_CAMERA #8
# [DeviceClass indev @ 0x7fd4e9721740] [3] Capture screen 0
# [DeviceClass indev @ 0x7fd4e9721740] [4] Capture screen 1
# [DeviceClass indev @ 0x7fd4e9721740] DeviceClass audio devices:
# [DeviceClass indev @ 0x7fd4e9721740] [0] Microphone
# 1: Input/output error
#
# In this example, ONLY the lines containing the string "UNIQUESKY_CAR_CAMERA" are actually cameras in
# in our SonaScanner, so the other lines are ignored.
# We discard all lines that we know contain items that are not our cameras
# (For example, lines containing:
#  "DeviceClass" "FaceTime", "Capture" "audio", "Microphone", and "Input/output error")
# All the values that should be excluded should be added
# to the list contained in the predefined constant EXCLUDED_CAMERAS
# Note, we will exclude any cameras reported by ffmpeg, if any part
# of any of the strings below match anywhere in the camera name
# in a case blind comparison:
EXCLUDED_CAMERAS = ("AVFoundation video devices:",
                    "FaceTime HD Camera (Built-in)",
                    "FaceTime Camera (Built-in)",
                    "FaceTime",
                    "iGlasses",
                    "Virtual Camera",
                    "Apowersoft_AudioDevice",
                    "Built-in Microphone",
                    "Microphone",
                    "audio",
                    "Capture screen",
                    "AVFoundation audio devices:",
                    "MacBook Pro Microphone",
                    "error")

# When there are no cameras found we use saved data called the "VIRTUAL CAMERAS"
VIRTUAL_CAMERA_LIST = [('0', 'Virtual Camera #6'),
                       ('1', 'Virtual Camera #2'),
                       ('2', 'Virtual Camera #8'),
                       ('3', 'Virtual Camera #11'),
                       ('4', 'Virtual Camera #7'),
                       ('6', 'Virtual Camera #23'),
                       ('7', 'Virtual Camera'),
                       ('8', 'Virtual Camera #4'),
                       ('9', 'Virtual Camera #22'),
                       ('10', 'Virtual Camera #9'),
                       ('11', 'Virtual Camera #19'),
                       ('12', 'Virtual Camera #24'),
                       ('13', 'Virtual Camera #18'),
                       ('14', 'Virtual Camera #15'),
                       ('15', 'Virtual Camera #21'),
                       ('16', 'Virtual Camera #10'),
                       ('17', 'Virtual Camera #14'),
                       ('18', 'Virtual Camera #3'),
                       ('19', 'Virtual Camera #13'),
                       ('20', 'Virtual Camera #20'),
                       ('21', 'Virtual Camera #16'),
                       ('22', 'Virtual Camera #17'),
                       ('23', 'Virtual Camera #5')]


def prettify(xml_element_tree):
    """
    Return a pretty-printed XML string for the Element.
    """
    from xml.etree import ElementTree
    rough_string = ElementTree.tostring(xml_element_tree, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def show_image(image_file, window):

    filepath, file_extension = os.path.splitext(image_file)
    # stuff
    if file_extension.lower() == ".jpg":
        # PySimpleGUI uses tkinter which doesn't support JPG images, so we have to convert them
        im = Image.open(image_file)
        newsize = (192, 108)
        im = im.resize(newsize)
        filename = filepath + ".png"
        im.save(filename)
        window.FindElement('_IMAGE_ELEMENT_').Update(filename=filename, visible=True, size=[192, 108])
    else:
        filename = image_file

    # fall through
    # Changes some of the settings for the Image Element. Must call Window.Read or Window.Finalize prior

    # print ("display this image file =", image_file)
    return


def macos_camera_settings(cameraID, cameraName, image_file_path):
    """
    macos_camera_settings(cameraID, cameraName, image_file_path)

    macos_camera_setting() is a function that returns an string of ffmpeg commands for different camera manufacturers.
    This is specific to macos and ios operating systems using the 'avfoundation' interface to video cameras.
    """
    image_file_name = image_file_path
    ffmpeg_options_dict = {
        'FHD Camera': [PATH_TO_FFMPEG, '-y', '-hide_banner',
                       '-f', 'avfoundation',
                       # '-pixel_format', 'uyvy422',
                       # '-video_size', '1920x1080',
                       '-framerate', '25',
                       '-i', cameraID,
                       '-frames:v', '1',
                       '-f', 'image2',
                       image_file_path],
        'USB 2.0 Camera': [PATH_TO_FFMPEG, '-y', '-hide_banner',
                        '-f', 'avfoundation',
                        '-pixel_format', 'uyvy422',
                        # '-video_size', '1920x1080',
                        '-framerate', '30',
                        '-i', cameraID,
                        '-frames:v', '1',
                        '-f', 'image2',
                        '-vf', 'scale=1920x1080',
                        image_file_path],
        'Virtual Camera' : ['cp', os.path.join(LOCAL_VIRTUAL_SCAN_DIR_ROOT_PATH, image_file_name),image_file_path],
    }
    for camera_name_prefix_key in ffmpeg_options_dict:
        if camera_name_prefix_key in cameraName:
            return ffmpeg_options_dict[camera_name_prefix_key]
        # else:
        #     print(camera_name_prefix_key,"is not in", cameraID)
    print("ERROR:", "'" + cameraName + "'", " is an Unknown Camera Type.")
    sys.exit(110)


def list_devices():
    """
    list_devices()

    list_devices() is a function that returns an camera_list of (CameraID, CameraName) pairs of Sonacam cameras
    that can be used to take pictures.
    list_devices() CONTAINS OS DEPENDENT CODE for interfacing with USB Cameras.
    """
    tic = time.perf_counter()
    camera_list = []

    # ffmpeg parameters explained:
    # -hide_banner          prevents output of the compile options banner which we don't want to see.
    # -f avfoundation       instructs ffmpeg to connect to Apple's "avfoundation" objects to find cameras.
    # -f l4v2               instructs ffmpeg to connect to linux4video2 objects to find cameras.
    # -f dshow              instructs ffmpeg to connect to DirectShow objects to find cameras.
    # -list_devices true    instructs ffmpeg to list all the devices
    # -i 1                  instructs ffmpeg to access the first device

    if platform.system() == "Darwin":  # MacOS X and iOS Systems only.  Use -f avfoundation to find USB cameras
        run_cmd = subprocess.run([PATH_TO_FFMPEG, '-hide_banner',
                                  '-f', 'avfoundation', '-list_devices', 'true', '-i', '1'],
                                 universal_newlines=True,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE)  # NOTE!!! ffmpeg writes to stderr, not stdout!

    elif platform.system() == "Linux":  # Linux systems
        # TODO: For Linux We might have to have different ffmpeg calls for Android, ChromeOS, etc.
        # Here are ways to do so.
        # if  'ANDROID_STORAGE' in environ:  # Android systems only
        #     print("Error:  Android is not yet supported")
        # elif  'SOMMELIER_VERSION'  in environ:
        #     print("Error:  ChromeOS is not yet supported")
        # else:
        run_cmd = subprocess.run([PATH_TO_FFMPEG, '-hide_banner',
                                  '-f', 'v4l2', '-list_devices', 'true', '-i', '1'],
                                 universal_newlines=True,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE)  # NOTE!!! ffmpeg writes to stderr, not stdout!

    elif platform.system() == "Windows":  # Windows systems only
        # TODO: For Windows, make sure that we use os.path.join() to join directory path elements
        # TODO: For Windows, make sure that the path separators are "\" not "/"
        # TODO: remove all hard coded path strings from the file, and put in CONSTANTS section instead.
        run_cmd = subprocess.run([PATH_TO_FFMPEG, '-hide_banner',
                                  '-f', 'dshow', '-list_devices', 'true', '-i', '1'],
                                 universal_newlines=True,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE)  # Note, ffmpeg writes to stderr, not stdout!

    else:  # Not a known OS that we support
        print("Error: ", platform.system(), "is not yet supported")
        exit(1)

    # if we get here, we've made the proper call for this OS to capture a camera_list in run_cmd.stderr buffer
    stderr_buffer = run_cmd.stderr
    if stderr_buffer == '':
        print("WARNING: ffmpeg did not return a list; using VIRTUAL cameras. ", run_cmd.stderr)
        camera_list = VIRTUAL_CAMERA_LIST

    elif "command not found" in stderr_buffer:
        # This error msg suggests that the ffmpeg shell program wasn't found.  We explain how to install it:
        print("WARNING: ffmpeg program was not found; using VIRTUAL cameras. ")
        camera_list = VIRTUAL_CAMERA_LIST

    else:  # this returned output should include a list of devices that we will need to parse to find
        #    just those devices which are our scanner cameras.   See EXCLUDED CAMERAS note in
        #    CONSTANTS definition section above

        for line in stderr_buffer.splitlines():
            skip = False
            for excluded_camera in EXCLUDED_CAMERAS:
                if excluded_camera.upper() in line.upper():
                    skip = True
                    # print("discarding line:", line)
                    break  # no need to keep looping once any of these are excluded camera matches.
            if skip == False:
                # parse the line as follows:
                # [ discarded data ] [cameraID] camera_name
                if "[" in line:
                    string1 = line.split("[")[2]
                    string2 = line.split("[")[2]
                    cameraID = string2.split("]")[0].strip()
                    camera_name = string1.split("]")[1].strip()
                    camera_tupple = (cameraID, camera_name)
                    camera_list.append(camera_tupple)
            # else case do nothing and just loop again.

    number_of_responding_cameras = len(camera_list)
    toc = time.perf_counter()
    print(f"Captured list of {number_of_responding_cameras} cameras in: {toc - tic:0.0f} seconds")
    return camera_list


async def take_image(camera_id, camera_name, image_file_path,
                     image_counter, number_of_scanner_cameras, window):
    image_capture_tic = time.perf_counter()
    camera_settings = macos_camera_settings(camera_id, camera_name, image_file_path)
    print(camera_settings)
    if "Virtual"  in camera_id:
        print("using virtual camera")
    else:
        try:
            run_cmd = subprocess.run(camera_settings,
                                    # [PATH_TO_FFMPEG, '-y', '-hide_banner',
                                    #  '-f', 'avfoundation',
                                    #  '-pixel_format', 'uyvy422',
                                    #  '-video_size', '1920x1080',
                                    #  '-framerate', '15',
                                    #  '-i', camera_id,
                                    #  '-frames:v', '1',
                                    #  '-f', 'image2',
                                    #  image_file_path],
                                     universal_newlines=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)  # Note, ffmpeg writes to stderr, not stdout!
        except Exception as e:
            print("Error", repr(e))
            print("Unable to capture image for", image_file_path)
            # print(run_cmd.stdout)
            # print(run_cmd.stderr)
            return "NO IMAGE!"
    show_image(image_file_path, window)
    window.FindElement('_PROGRESS_BAR_').update_bar(
        (int(100 * (image_counter) / number_of_scanner_cameras)))
    window.FindElement('_ACTION_STATUS_LINE_1_').Update("Scanning...")
    image_file_basename = basename(image_file_path)
    window.FindElement('_ACTION_STATUS_LINE_2_').Update(image_file_basename)
    window.FindElement('_IMAGE_ELEMENT_').Update()
    images_dir_path = os.path.abspath('images/')
    window.Refresh()
    image_capture_toc = time.perf_counter()
    print(f"Captured {camera_name} image in: {image_capture_toc - image_capture_tic:0.0f} seconds")
    return camera_name



def manifest_maker(full_scan_id, SCANNER_ID, from_email, to_email, LOCAL_SCAN_ID_DIR_PATH):
    # write a manifest.xml file into the scan_dir directory with
    # photoscene_id, scan_originator (from/sender), model_recipient (to/CADaddress) and other fields
    xml_top = Element('SonaScan_Manifest')
    manifest_timestamp = datetime.today().strftime('%Y-%m-%d:%H:%M:%S %Z')
    comment = Comment('Manifest was Generated ' + manifest_timestamp)
    xml_top.append(comment)

    child = SubElement(xml_top, 'scan_id')
    child.text = full_scan_id

    child = SubElement(xml_top, 'scanner_id')
    child.text = SCANNER_ID

    child = SubElement(xml_top, 'from_email')
    child.text = from_email

    child = SubElement(xml_top, 'to_email')
    child.text = to_email

    child = SubElement(xml_top, 'photoscene')
    child.text = "PHOTOSCENE_ID_NOT_YET_ASSIGNED"

    pretty_xml_top = prettify(xml_top)
    print(pretty_xml_top)

    manifest_file_name = os.path.join(LOCAL_SCAN_ID_DIR_PATH, "manifest.xml")
    manifest_file = open(manifest_file_name, "wt")
    n = manifest_file.write(pretty_xml_top)
    manifest_file.close()
    print(manifest_file_name, "saved")
    # ElementTree(pretty_xml_top).write(manifest_file)
    return


    # ************************************ DONE IMAGING **************************************************************
    window.FindElement('_ACTION_STATUS_LINE_1_').Update("Scanning Completed.")
    window.FindElement('_ACTION_STATUS_LINE_2_').Update(f"{image_counter} images.")
    thumbnail = status_ready
    window.FindElement('_IMAGE_ELEMENT_').Update(filename=thumbnail)
    window.Refresh()

    # now create an manifest file for the Scan Directory
    manifest_maker(full_scan_id, SCANNER_ID, from_email, to_email, LOCAL_SCAN_ID_DIR_PATH)

    # now create an index file for the Scan Directory
    scandir_index_maker(LOCAL_SCAN_ID_DIR_PATH, full_scan_id)

    time.sleep(2)
    window.FindElement('_ACTION_STATUS_LINE_1_').Update("Ready")
    window.FindElement('_ACTION_STATUS_LINE_2_').Update("")
    show_image(status_ready, window)
    window.FindElement('_IMAGE_ELEMENT_').Update()
    window.Refresh()
    toc = time.perf_counter()
    print(f"Captured {image_counter} images for {full_scan_id}  in: {toc - tic:0.0f} seconds")
    return LOCAL_SCAN_ID_DIR_PATH, manifest_file_name


async def get_data_async():
    with requests.Sessions() as session:
        loop = asyncio.get_event_loop()

        # Take each URL in the list,
        # make an async task from it that uses
        # 'fetch' to get data from the URL
        # and start the tast running in the event loop.

        tasks = [loop.run_in_executor(None, fetch, session_file)
                 for file in files]

        # Gather all the tasks from the event loop once they finish running
        # (This command blocks.)

        for response in await asyncio.gather(*tasks):
            print(response)


async def main():
    """
        main()

        main() runs all the commands to take a scan and process it (with no GUI)
        """
    tic = time.perf_counter()
    system_Str = """osascript -e \'Tell application \"System Events\" to display dialog \"Beginning SonaScan Test\" with title \"SonaScan Test"\'"""
    retval = os.system(system_Str)
    paramiko.util.log_to_file("../paramiko.log")
    # test_rsync()
    camera_list = list_devices()
    print(camera_list)
    number_of_cameras = len(camera_list)
    print("Number of cameras responding =", number_of_cameras)

    image_counter = 1
    if number_of_cameras <12:
        obj_file = os.path.join(LOCAL_MODEL_ROOT_PATH, "VIRTUAL/Photoscene-Virtual/result.obj")
        syscmd("open -a " + PATH_TO_MODEL_VIEWER_APP + " " + obj_file)
        photoscene_website = "http://cloud1.tri-di.com/scans/VIRTUAL"
        webbrowser.open_new_tab(photoscene_website)
    else:
        # We actually see cameras in our camera_list!!!
        short_scan_id = datetime.today().strftime('%Y%m%d%H%M%S')
        # the full_scan_id is composed of the unique SCANNER_ID (above) and the short_scan_id ensuring a globally unique id
        full_scan_id = SCANNER_ID + short_scan_id
        LOCAL_SCAN_ID_DIR_PATH = os.path.abspath(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, full_scan_id + '/'))

        # now lets take all the images!
        window = sg.Window("SonaScan");
        # sg.Window('SonaScan', layout, font=('Raleway', 40), resizable=True, grab_anywhere=True,
        #                   ttk_theme="default",
        #                   use_ttk_buttons=True, finalize=True, location=(0, 0), size=(window_width, window_height))
        start = default_timer()
        tasks = []

        for camera_pair in camera_list:
            camera_id, camera_name = camera_pair
            image_file_name = 'img' + str(image_counter).zfill(2) \
                              + "-cam" + str(camera_id).zfill(2) \
                              + "-" + urllib.parse.quote_plus(camera_name.replace('#', '')) + '.jpg'
            image_file_path = os.path.join(LOCAL_SCAN_ID_DIR_PATH, image_file_name)
            print(camera_id, camera_name, image_file_path, image_counter)
            # schedule 24 camera captures *concurrently*:
            task = asyncio.create_task(
                take_image(camera_id, camera_name, image_file_path, image_counter),
                name=image_file_name)
            tasks.append(task)
            image_counter = image_counter + 1
        # elapsed = default_timer - start
        # Gather all the tasks from the event loop once they finish running
        # (This command blocks.)
        await asyncio.gather(*tasks)

    toc = time.perf_counter()
    print(f"Captured {image_counter - 1} cameras in: {toc - tic:0.0f} seconds")
    duration_in_min = (toc - tic) / 60
    print(f"Completed Scan  in: {duration_in_min:0.2f} minutes")
    system_Str = """osascript -e \'Tell application \"System Events\" to display dialog \"COMPLETED SonaScan  SCAN Test\" with title \"SonaScan Test"\'"""
    os.system(system_Str)
    return


if __name__ == "__main__":
    # execute only if run as a script
    asyncio.run(main())
