"""
main.py

main.py is the main program of SonaScan and contains most of the GUI functions.
"""

# Global includes
import asyncio
import shutil
import time
import urllib
import webbrowser
from datetime import datetime
from os.path import basename


from src.forge import process_scan, monitor_scan_dir, get_obj, get_forge_token
from glob import glob
import os
import PySimpleGUI as sg  # pip3 install --upgrade PySimpleGUI PySImpleGUI creates our GUI
import tkinter as tk
from tkinter import filedialog

from src.CONSTANTS import syscmd, images_dir_path, SCANNER_ID, last_saved_value_file, LOCAL_UPLOAD_DIR_ROOT_PATH, \
    SERVER_SCAN_DIR_ROOT_PATH, LOCAL_SCAN_DIR_ROOT_PATH, LOCAL_MODEL_ROOT_PATH, LOCAL_FAILED_ROOT_PATH, status_ready, \
    PATH_TO_MODEL_VIEWER_APP, LOCAL_VIRTUAL_SCAN_DIR_ROOT_PATH, LOCAL_SCAN_ID_DIR_PATH, SERVER_UPLOADED_DIR_ROOT_PATH
from src.new_scan_id import get_new_scan_id, create_scan_dirs
# print(get_new_scan_id())
# create_scan_dirs()


print(sg)
print(sg.version)

import re
import subprocess

# local includes
# from debugging import get_line_number
from src.capture_images import list_devices, take_image, manifest_maker, VIRTUAL_CAMERA_LIST, show_image
from src.index_maker import scandir_index_maker
from src.new_scan_id import get_new_scan_id

from src.last_saved_values import from_email
from src.last_saved_values import to_email
from src.last_saved_values import consumer_id
from src.last_saved_values import order_details
from src.upload import scandir_upload, move_scandir_to_upload_dir_on_server, scan_root_sync

short_scan_id, full_scan_id = get_new_scan_id()
create_scan_dirs()
from src.GUI_Layouts import settings, info_panel, layout

def show_splashscreen(seconds_to_display):
    sg.popup_non_blocking("SonaScan", font=('Raleway', 100), button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
                          background_color='#ffffff', auto_close=True, auto_close_duration=seconds_to_display,
                          title="SONASCAN is starting...")
    return True


def get_screen_width_and_height():
    results = str(
        subprocess.Popen(['system_profiler SPDisplaysDataType'], stdout=subprocess.PIPE, shell=True).communicate()[
            0])
    res = re.search('Resolution: \d* x \d*', results).group(0).split(' ')
    width, height = int(res[1]), int(res[3])
    return width, height

def is_internet_available():
    ping_output = syscmd("ping -c 1 8.8.8.8 | grep '0.0% packet loss' ")
    if (ping_output == ""):
        print("Internet isn't present ", ping_output)
        return False
    else:
        # print("Internet is present")
        return True


def is_server_reachable():
    ping_output = syscmd("ping -c 1 cloud1.tri-di.com | grep '0.0% packet loss' ")
    if (ping_output == ""):
        print("There is NO route to Sonautics server: cloud1.tri-di.com")
        return False
    else:
        # print("There is a route to Sonautics server: cloud1.tri-di.com")
        return True



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




# window = sg.Window("SonaScan");
# sg.preview_all_look_and_feel_themes()
# sg.set_options(ttk_theme='default')
# sg.ChangeLookAndFeel('DarkTeal7')
sg.ChangeLookAndFeel('Default1')

# short_scan_id, full_scan_id = get_new_scan_id()
scan_start_time = datetime.now()
dt_string = scan_start_time.strftime("%d-%b-%Y %H:%M:%S")

number_scans_waiting = 0
internet_status = False
route_to_server_status = False


async def scan_with_GUI(camera_list):

    from src.last_saved_values import consumer_id
    from src.last_saved_values import consumer_name
    from src.last_saved_values import order_details

    tic = time.perf_counter()
    upload_tasks = []
    process_tasks = []
    # seconds_to_display = 5
    # show_splashscreen(seconds_to_display)
    width, height = get_screen_width_and_height()
    window_width = int(width / 2)
    window_height = int(height / 2)

    # short_scan_id, full_scan_id = get_new_scan_id()
    scan_start_time = datetime.now()
    dt_string = scan_start_time.strftime("%d-%b-%Y %H:%M:%S")
    settings_window = sg.Window('Settings', settings, font=('Raleway', 30), resizable=True, grab_anywhere=True,
                                ttk_theme="default", use_ttk_buttons=True, finalize=True, location=(0, 0))

    info_window = sg.Window('Info', info_panel, font=('Raleway', 30), resizable=True, grab_anywhere=True,
                                ttk_theme="default", use_ttk_buttons=True, finalize=True, location=(0, 0))


    window = sg.Window('SonaScan', layout, font=('Raleway', 40), resizable=True, grab_anywhere=True,
                       ttk_theme="default",
                       use_ttk_buttons=True, finalize=True, location=(0, 0), size=(window_width, window_height))
    # no_titlebar=True,
    # window.Maximize()
    settings_window.Hide()
    info_window.Hide()
    scans_awaiting_upload_list = glob(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID, "*/"))
    number_of_scans_awaiting_upload = len(scans_awaiting_upload_list)
    uploaded_scans_list = glob(os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, "*/"))
    number_of_uploaded_scans = len(uploaded_scans_list)
    modeled_scans_list = glob(os.path.join(LOCAL_MODEL_ROOT_PATH, SCANNER_ID, "*/"))
    number_of_modeled_scans = len(modeled_scans_list)
    failed_scans_list = glob(os.path.join(LOCAL_FAILED_ROOT_PATH, SCANNER_ID, "*/"))
    number_of_failed_scans = len(failed_scans_list)
    window.FindElement('_UPLOADS_NUMBER_').Update(number_of_scans_awaiting_upload)
    print(scans_awaiting_upload_list)

    while True:  # Event Loop

        if is_internet_available():
            internet_status = "Online"
        else:
            internet_status = "Offline"
        # window.FindElement('_INTERNET_STATUS_').Update(internet_status)

        if is_server_reachable():
            route_to_server_status = "Available"
        else:
            route_to_server_status = "Unavailable"
        # window.FindElement('_ROUTE_TO_SERVER_STATUS_').Update(route_to_server_status)

        # RESET VARIABLES IN FORM FOR NEXT DISPLAY
        print("******************************************** NEW SCAN *************************************************")
        from src.last_saved_values import from_email
        from src.last_saved_values import to_email
        short_scan_id, full_scan_id = get_new_scan_id()
        window.FindElement('_DATE_').Update(dt_string)
        window.FindElement('_SCAN_ID_').Update(full_scan_id)

        # ************************** THIS IS WHAT REPAINTS THE MAIN WINDOW!!! **************************************
        event, values = window.Read()  # check return status from latest window event
        print("event=",event, "values=", values)


        # number_scans_waiting = len(scans_waiting(scan_dir_root_path))
        # window.FindElement('_SCANS_WAITING_').Update(number_scans_waiting)

        # we may need this to make sure that the window is full size on the small screen
        # w_size, h_size = sg.Window.get_screen_size(window)
        # print("screen size = ",  w_size, h_size)
        # w_dimension, h_dimension = sg.Window.get_screen_dimensions(window)
        # print("screen w_dimension = ", w_dimension, h_dimension)

        # event finds out which button was pressed.

        if event is None or event == 'Exit':  # If event = None, the close box was clicked.
            return ()  # THIS EXITS THE ENTIRE MAIN PROGRAM!

        if event == '_SETTINGS_ICON_':  # *****************  Settings Button pressed!  ******************************
            settings_window.UnHide()
            settings_event, settings_values = settings_window.Read()
            if settings_event == 'Save':
                save_last_form_values(last_saved_value_file, from_email, to_email, consumer_id, consumer_name,
                                      order_details)
                settings_window.UnHide()


        if event == '_INFO_ICON_':  # ***************** Info Button pressed!  ********************************************
            info_window.UnHide()

        if event == '_UPLOADS_ICON_':  # ***************** Uploads Icon Button pressed!  ********************************************

            initial_folder_path = os.path.abspath(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID))
            print(f"view of scan directory: {initial_folder_path} requested")

            selected_scan = tk.filedialog.askdirectory(initialdir=initial_folder_path)
            # selected_scan = sg.popup_get_folder('', no_window=True, initial_folder=initial_folder_path)
            print(f'selected_scan ={selected_scan}')
            if selected_scan:
                webbrowser.open_new_tab("file://"+os.path.join(selected_scan,"index.html"))


        elif event == 'SCAN':  # ***************** SCAN Button pressed!  ********************************************

            window.FindElement('_ACTION_STATUS_LINE_1_').Update("Scanning...")
            window.FindElement('_ACTION_STATUS_LINE_2_').Update(" ")
            last_image_captured_time = scan_start_time

            consumer_id = values['_CONSUMER_ID_']
            consumer_name = values['_CONSUMER_NAME_']
            order_details = values['_ORDER_DETAILS_']
            # monitor_scanning_flag = values['_MONITOR_SCANNING_CB_']
            # monitor_scanning_flag = False
            # monitor_upload_flag = values['_MONITOR_UPLOADS_CB_']
            # monitor_upload_flag = False
            # monitor_modeling_flag = values['_MONITOR_PROCESSING_CB_']
            # monitor_modeling_flag = False

            # ***************** capturing images  ********************************************
            LOCAL_SCAN_ID_DIR_PATH = os.path.abspath(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, full_scan_id))
            if not os.path.isdir(LOCAL_SCAN_ID_DIR_PATH):
                os.makedirs(LOCAL_SCAN_ID_DIR_PATH)

            image_counter = 1
            tasks = []
            number_of_scanner_cameras = len(camera_list)
            if number_of_scanner_cameras  < 12:
                # Not enough images!  Use Virtual Cameras instead
                print(number_of_scanner_cameras, " camera responded. Using Virtual Scanner Instead!")
                number_of_scanner_cameras =len(VIRTUAL_CAMERA_LIST)
                for camera_pair in VIRTUAL_CAMERA_LIST:
                    camera_id, camera_name = camera_pair
                    image_file_name = 'img' + str(image_counter).zfill(2) \
                                      + "-cam" + str(camera_id).zfill(2) \
                                      + "-" + urllib.parse.quote_plus(camera_name.replace('#', '')) + '.jpg'
                    image_file_path = os.path.join(LOCAL_SCAN_ID_DIR_PATH, image_file_name)
                    print(camera_id, camera_name, image_file_path, image_counter)
                    virtual_file_path = os.path.join(LOCAL_VIRTUAL_SCAN_DIR_ROOT_PATH, image_file_name)
                    shutil.copyfile(virtual_file_path, image_file_path)
                    task = asyncio.create_task(
                        take_image(camera_id, camera_name, image_file_path,
                                   image_counter, number_of_scanner_cameras, window),
                        name=image_file_name)
                    tasks.append(task)
                    image_counter = image_counter + 1
                number_of_scanner_cameras = 0
                await asyncio.gather(*tasks)
            else:
                tic = time.perf_counter()
                for camera_pair in camera_list:
                    camera_id, camera_name = camera_pair
                    image_file_name = 'img' + str(image_counter).zfill(2) \
                                      + "-cam" + str(camera_id).zfill(2) \
                                      + "-" + urllib.parse.quote_plus(camera_name.replace('#', '')) + '.jpg'
                    image_file_path = os.path.join(LOCAL_SCAN_ID_DIR_PATH, image_file_name)
                    print(camera_id, camera_name, image_file_path, image_counter)
                    # schedule up to 24 camera captures *concurrently*:
                    task = asyncio.create_task(
                        take_image(camera_id, camera_name, image_file_path,
                                   image_counter, number_of_scanner_cameras, window),
                        name=image_file_name)
                    tasks.append(task)
                    image_counter = image_counter + 1
                # elapsed = default_timer - start
                # Gather all the tasks from the event loop once they finish running
                # (This command blocks.)
                await asyncio.gather(*tasks)



            # ************************************ DONE IMAGING ****************************************************

            window.FindElement('_ACTION_STATUS_LINE_1_').Update("Scanning Completed.")
            window.FindElement('_ACTION_STATUS_LINE_2_').Update(f"{image_counter-1} images.")
            thumbnail = os.path.join(images_dir_path, status_ready)
            window.FindElement('_IMAGE_ELEMENT_').Update(filename=thumbnail)
            window.Refresh()

            # Make a manifest.xml file for this scan containing all the auxilary information'
            # other than images that we need.
            manifest_maker(full_scan_id, SCANNER_ID, from_email, to_email, LOCAL_SCAN_ID_DIR_PATH)

            the_png_files = glob(os.path.join(LOCAL_SCAN_ID_DIR_PATH, "img*.png"))
            for filename in the_png_files:
                os.remove(filename)

            # Make an index file that displays the images nicely
            scandir_index_maker(LOCAL_SCAN_ID_DIR_PATH, full_scan_id)

            window.FindElement('_ACTION_STATUS_LINE_1_').Update("Ready")
            window.FindElement('_ACTION_STATUS_LINE_2_').Update("")
            show_image(os.path.join(images_dir_path, status_ready), window)
            # window.FindElement('_IMAGE_ELEMENT_').Update()
            window.Refresh()

            # Update number of scans waiting for upload, and list of waiting scanIDs
            scans_awaiting_upload_list = glob(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_scans_awaiting_upload = len(scans_awaiting_upload_list)
            uploaded_scans_list = glob(os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_uploaded_scans = len(uploaded_scans_list)
            modeled_scans_list = glob(os.path.join(LOCAL_MODEL_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_modeled_scans = len(modeled_scans_list)
            failed_scans_list = glob(os.path.join(LOCAL_FAILED_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_failed_scans = len(failed_scans_list)
            print(number_of_scans_awaiting_upload, "scans waiting", number_of_uploaded_scans, "uploaded",
                  number_of_modeled_scans, "modeled", number_of_failed_scans, "failed." )
            window.FindElement('_UPLOADS_NUMBER_').Update(number_of_uploaded_scans)
            window.Refresh()

            toc = time.perf_counter()
            print(f"Captured {image_counter - 1} cameras in: {toc - tic:0.0f} seconds")
            duration_in_min = (toc - tic) / 60
            print(f"Completed Scan  in: {duration_in_min:0.2f} minutes")
            window.FindElement('_ACTION_STATUS_LINE_3_').Update(
                f"Completed Scan  in: {duration_in_min:0.2f} minutes")
            window.Refresh()

            # Spawn off async task  to upload asynchronously
            SERVER_SCAN_DIR_PATH = SERVER_SCAN_DIR_ROOT_PATH + SCANNER_ID
            upload_task = asyncio.create_task(
                async_upload(LOCAL_SCAN_ID_DIR_PATH, SERVER_SCAN_DIR_PATH, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID,
                             short_scan_id, full_scan_id, window), name= full_scan_id)
            upload_tasks.append(upload_task)
            window.FindElement('_ACTION_STATUS_LINE_3_').Update(f"Uploading {short_scan_id}")
            window.Refresh()
            # await asyncio.gather(*upload_tasks)
            await upload_task

            # Update number of scans waiting for upload, and list of waiting scanIDs
            scans_awaiting_upload_list = glob(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_scans_awaiting_upload = len(scans_awaiting_upload_list)
            uploaded_scans_list = glob(os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_uploaded_scans = len(uploaded_scans_list)
            modeled_scans_list = glob(os.path.join(LOCAL_MODEL_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_modeled_scans = len(modeled_scans_list)
            failed_scans_list = glob(os.path.join(LOCAL_FAILED_ROOT_PATH, SCANNER_ID, "*/"))
            number_of_failed_scans = len(failed_scans_list)
            print(number_of_scans_awaiting_upload, "scans waiting", number_of_uploaded_scans, "uploaded",
                  number_of_modeled_scans, "modeled", number_of_failed_scans, "failed." )
            window.FindElement('_ACTION_STATUS_LINE_3_').Update(
                f"Upload Completed for {short_scan_id}")
            window.FindElement('_UPLOADS_NUMBER_').Update(number_of_uploaded_scans)
            window.Refresh()
    # return

async def async_upload(LOCAL_SCAN_ID_DIR_PATH,SERVER_SCAN_DIR_PATH, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, short_scan_id, full_scan_id, window):

    tic = time.perf_counter()
    process_tasks =[]
    uploaded_dest_dir = scandir_upload(LOCAL_SCAN_ID_DIR_PATH, SERVER_SCAN_DIR_PATH, LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, window)
    if uploaded_dest_dir != False:
        print(uploaded_dest_dir, 'was successfully uploaded.')
        move_scandir_to_upload_dir_on_server(full_scan_id)

        access_token = get_forge_token()
        # Spawn off an async task to submit models to Forge
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"Submitting {short_scan_id} for processing on SonaServer")
        window.Refresh()
        print("Submitting " + short_scan_id)

        photoscene_website = SERVER_UPLOADED_DIR_ROOT_PATH + full_scan_id
        # photoscene_website = os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, full_scan_id,  "index.html")
        # TODO: Why isn't this browser window openning/!
        webbrowser.open_new_tab(photoscene_website)

        process_task = asyncio.create_task(process_scan(full_scan_id, from_email, to_email),
                                           name=full_scan_id)
        process_tasks.append(process_task)
        # await asyncio.gather(*process_tasks)
        await process_task
        photoscene_path = os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, full_scan_id, "photoscene-*")
        print(photoscene_path)
        photoscene_dir = glob( photoscene_path)
        print(photoscene_dir[0])
        photoscene_basename = basename(photoscene_dir[0])
        print(photoscene_basename)
        photoscene_split = photoscene_basename.split('-')
        print(photoscene_split)
        photoscene_id = photoscene_split[1]
        print(photoscene_id)
        uploaded_scans_list = glob(os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, SCANNER_ID, "*/"))
        number_of_uploaded_scans = len(uploaded_scans_list)
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f" {short_scan_id} started processing on SonaServer")
        window.FindElement('_UPLOADS_NUMBER_').Update(number_of_uploaded_scans)
        window.Refresh()



        # check the photoscene_id that is in the directory

        # TODO: Spawn off async task to check for model completion?
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"Processing {full_scan_id}, photoscene: {photoscene_id}")
        window.Refresh()
        monitor_scan_dir(full_scan_id, photoscene_id, access_token, window)


        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"Retrieving 3D models (OBJ, STL) for {full_scan_id}, photoscene: {photoscene_id}")
        window.Refresh()
        get_obj(full_scan_id, photoscene_id, access_token,from_email, to_email, consumer_id, order_details , window)
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"Completed downloading 3D models for {full_scan_id}, photoscene: {photoscene_id}")
        window.Refresh()

        destination = shutil.copytree(os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH,full_scan_id,photoscene_basename),
                                      os.path.join(LOCAL_MODEL_ROOT_PATH,full_scan_id))
        window.FindElement('_ACTION_STATUS_LINE_3_').Update(
            f"saved 3D models for {full_scan_id}, at: {destination}")
        shutil.rmtree(os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH,full_scan_id))

        obj_file = os.path.join(LOCAL_MODEL_ROOT_PATH,full_scan_id,'result.obj')
        if os.path.exists(obj_file):
            open_3D_model_Request = "open -a " + PATH_TO_MODEL_VIEWER_APP + " " + obj_file + "&"
            print(open_3D_model_Request)
            syscmd(open_3D_model_Request)
        else:
            print("ERROR: Could not find", obj_file)

    else:
        # There is no directory_path, and thus no images to process
        return

    # Now that we have uploaded the current scan, we will attempt to finish uploading any previous _scans that
    # did not complete earlier (probably due to no connection to server at the earlier time)
    scan_root_sync(window)
    return


def main():
    short_scan_id, full_scan_id = get_new_scan_id()
    create_scan_dirs()
    LOCAL_SCAN_ID_DIR_PATH = os.path.abspath( os.path.join('_scans', full_scan_id ) )
    window = sg.Window("SonaScan")
    camera_list= list_devices()
    asyncio.run(scan_with_GUI(camera_list))
    # elapsed = default_timer - start



if __name__ == "__main__":
    # execute only if run as a script
    main()
    # main()
