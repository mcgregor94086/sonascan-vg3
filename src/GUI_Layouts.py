'''
GUI_Layouts.py

GUI_Layouts.py contains all the GUI Layout elements used by Sonascan
'''
import os
from datetime import datetime

import PySimpleGUI as sg  # pip3 install --upgrade PySimpleGUI PySImpleGUI creates our GUI


# LAYOUTS FOR MAIN WINDOW ******************************************************************************************

# window = sg.Window("SonaScan");
# sg.preview_all_look_and_feel_themes()
# sg.set_options(ttk_theme='default')
# sg.ChangeLookAndFeel('DarkTeal7')

from src.CONSTANTS import SCANNER_ID, small_logo, scan_button, thumbnail, igear, iquest, iupload, iwifi_good, LOCAL_SCAN_DIR_ROOT_PATH
from src.last_saved_values import from_email, to_email, consumer_name, consumer_id, order_details
from src.new_scan_id import get_new_scan_id

sg.ChangeLookAndFeel('Default1')

short_scan_id, full_scan_id = get_new_scan_id()
scan_start_time = datetime.now()
dt_string = scan_start_time.strftime("%d-%b-%Y %H:%M:%S")

# Column layout
col1 = [

    [sg.Text(
        'Ready                                                                                                                            ',
        font=('Raleway', 48, 'italic'),  text_color='#fb9004', justification='left',
        key='_ACTION_STATUS_LINE_1_')],
    [sg.Text
        ('Click SCAN to begin                                                                                                          ',
             font=('Raleway', 28), key='_ACTION_STATUS_LINE_2_')],
    [sg.ProgressBar(100, orientation='horizontal' ,bar_color=('#fb9004' ,"#aaaaaa"),
                    key="_PROGRESS_BAR_", size=(95 ,10))],

]

settings = [

    # LINE 1: HEADING
    [sg.Image(filename=small_logo, size=(300, 126)),
     sg.Text('Settings', font=('Raleway', 100, 'bold'), text_color='#fb9004',
                justification='center', size=(13, 1))],

    # LINE 2: SCANNER_ID
    [sg.Text('SCANNER_ID:', size=(16, 1), justification='right', font=('Raleway', 30, 'bold'), text_color='#000000'),
     sg.Text(SCANNER_ID, font=('Raleway', 30), justification='left', key='_SCANNER_ID_')],

    # LINE 3: WHO IS SENDING THIS SCAN?
    [sg.Text('Sender:', size=(16, 1), font=('Raleway', 30, 'bold'), justification='right'),
     sg.InputText(from_email, font=('Raleway', 30), size=(50, 1), key='_SENDER_')],

    # LINE 4: WHO WILL THIS SCAN BE SENT TO FOR CAD AND MANUFACTURING STEPS
    [sg.Text('Send Model To:', size=(16, 1), font=('Raleway', 30, 'bold'), justification='right'),
     sg.InputText(to_email, font=('Raleway', 30), size=(50, 1), key='_RECIPIENT_')],

    # LINE 5: Buttons
    [sg.Button('Cancel', font=('Raleway', 30, 'bold')),
     sg.Button('Save', font=('Raleway', 30, 'bold'))]
]

number_scans_waiting = 0
internet_status = False
route_to_server_status = False

info_panel = [

    # LINE 1: HEADING
    [
        sg.Image(filename=small_logo, size=(300, 126)),
        sg.Text('Info', font=('Raleway', 100, 'bold'), text_color='#fb9004',
                justification='center', size=(13, 1))
    ],

    # INFO PANEL
    [
        sg.Text('Scans to be uploaded =', font=('Raleway', 30, 'bold'), text_color='#000000'),
        sg.Text(number_scans_waiting, font=('Raleway', 30), key='_SCANS_WAITING_'),
        sg.Text('Network:', font=('Raleway', 30, 'bold'), text_color='#000000'),
        sg.Text(internet_status, font=('Raleway', 30, 'italic'), key='_INTERNET_STATUS_'),
        sg.Text('SonaScan Server:', font=('Raleway', 30, 'bold'), text_color='#000000'),
        sg.Text(route_to_server_status, font=('Raleway', 30, 'italic'),  key='_ROUTE_TO_SERVER_STATUS_')
    ],
]


layout = [

    # LINE 1: HEADING
    [
        sg.Image(filename=small_logo, size=(300, 126)),
        sg.Text('SonaScan', font=('Raleway', 100, 'bold'), text_color='#fb9004' ,
                justification='center' ,size=(13 ,1)),
        sg.Text(len(os.listdir(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID))), font=('Raleway', 15), visible=True, key='_UPLOADS_NUMBER_'),
        sg.Image(filename=iupload, size=(32, 32), visible=True, enable_events=True, key='_UPLOADS_ICON_'),
        sg.Image(filename=iwifi_good, size=(32, 32), visible=True, enable_events=True, key='_WIFI_ICON_'),
        sg.Image(filename=igear, size=(32, 32), visible=True, enable_events=True, key='_SETTINGS_ICON_'),
        sg.Image(filename=iquest, size=(32, 32), visible=True, enable_events=True, key='_INFO_ICON_'),

    ],

    # LINE 2: vertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # INVISIBLE LINE 3: WHO IS SENDING THIS SCAN?
    [
        sg.InputText(from_email, font=('Raleway', 15), size=(50, 1), key='_SENDER_', visible=False)
    ],

    # INVISIBLE LINE 4: WHO IS WILL THIS SCAN BE SENT TO FOR CAD AND MANUFACTURING STEPS
    [
        sg.InputText(to_email, font=('Raleway', 15, "italic"), size=(50, 1), key='_RECIPIENT_', visible=False)
    ],

    # LINE 5: CONSUMER NAME FOR IMPRESSION  BEING SCANNED (FOR EARS ON FILE RETRIEVAL)
    [
        sg.Text("Consumer's Name:", size=(16, 1), font=('Raleway', 30, 'bold'),  justification='right'),
        sg.InputText(consumer_name, font=('Raleway', 30, "italic"), size=(50, 1), key='_CONSUMER_NAME_')
    ],

    # LINE 6: CONSUMER EMAIL FOR IMPRESSION  BEING SCANNED (FOR EARS ON FILE RETRIEVAL)
    [
        sg.Text("Consumer's Email:", size=(16, 1), font=('Raleway', 30, 'bold'), justification='right'),
        sg.InputText(consumer_id, font=('Raleway', 30, "italic"), size=(50, 1), key='_CONSUMER_ID_')
    ],

    # LINE 7: WHAT ADDITIONAL ORDER DETAILS DOES SENDER WANT TO PROVIDE TO RECIPIENT
    [
        sg.Text('Order Details:', size=(16, 1), font=('Raleway', 30, 'bold'), justification='right'),
        sg.Multiline(order_details, font=('Raleway', 30, "italic"), size=(49, 1), key='_ORDER_DETAILS_')
    ],

    # LINE 8: vertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # LINE 9: vertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # LINE 10: THE BIG SCAN BUTTON
    [
        sg.Text('', size=(16, 2), font=('Raleway', 30, 'bold')),
        sg.Text('', size=(4, 2), font=('Raleway', 30, 'bold')),
        sg.Button('SCAN', button_color=('#ffffff' ,'#000000'), font=('Raleway', 75), image_filename=scan_button,
                 image_size=(600 ,172))
    ],

    # LINE 11: vertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # LINE 12: ertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # LINE 13: IMAGE AND PROGRESS
    [
        sg.Text('', size=(3, 1), font=('Raleway', 30, 'bold')),
        sg.Image(filename=thumbnail, visible=True, size=[192, 108],
              key='_IMAGE_ELEMENT_'),
        sg.Column(col1)
     ],

    # LINE 14: CALCULATED SCAN SPECIFIC DATA
    [
        sg.Text(dt_string, font=('Raleway', 29), justification='left', key='_DATE_' ,visible=False),
        sg.Text(SCANNER_ID, font=('Raleway', 30), justification='left', key='_SCANNER_ID_' ,visible=False),
        sg.Text('', size=(3, 1), font=('Raleway', 30, 'bold'), justification='right'),
        sg.Text('Scan ID:', size=(16, 1), font=('Raleway', 30, 'bold'), justification='right'),
        sg.Text(full_scan_id, font=('Raleway', 30), justification='right', key='_SCAN_ID_')
    ],

    # LINE 15: vertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # LINE 16: vertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # LINE 17: vertical spacer
    [sg.Text('', font=('Raleway', 15, 'bold'), text_color='#000000')],

    # LINE 18: Info bar
    [sg.StatusBar
        ('                                                                                                                             ',
             font=('Raleway', 18), size=(150,1), key='_ACTION_STATUS_LINE_3_')],
]
# END OF LAYOUT FOR MAIN WINDOW ************************************************************************************

def main():
    scans_awaiting_upload_list = os.listdir(os.path.join(LOCAL_SCAN_DIR_ROOT_PATH, SCANNER_ID))
    number_of_scans_awaiting_upload = len(scans_awaiting_upload_list)

if __name__ == "__main__":
    # execute only if run as a script
    main()
    # main()