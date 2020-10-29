"""
scandir_index_maker(scan_dir)

scandir_index_maker(scan_dir) takes a scan_dir directory and
generates a pretty index.php page in HTML and places it in the scan_dir

Copyright (c) Sonautics, Inc 2020.
Author: Scott L. McGregor
"""

import os
from pathlib import Path

from src.CONSTANTS import SERVER_UPLOADED_DIR_ROOT_PATH, LOCAL_SCAN_DIR_ROOT_PATH, LOCAL_UPLOAD_DIR_ROOT_PATH


PREAMBLE1 =  """ 
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>"""

PREAMBLE2 =  """</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://cloud1.tri-di.com/css/bootstrap.css" rel="stylesheet" type="text/css" media="all" />
    <link href="http://cloud1.tri-di.com/css/interface-icons.css" rel="stylesheet" type="text/css" media="all" />
    <link href="http://cloud1.tri-di.com/css/theme.css" rel="stylesheet" type="text/css" media="all" />
    <link href="http://cloud1.tri-di.com/css/custom.css" rel="stylesheet" type="text/css" media="all" />
    <link href='https://fonts.googleapis.com/css?family=Lora:400,400italic,700|Montserrat:400,700' rel='stylesheet' type='text/css'>
</head>
<body style="background-color:white">
    <div>
        <img src="http://cloud1.tri-di.com/images/logo-small.png"/>
        <h4 class="text-center">"""

PREAMBLE3 = """</h4>
    </div>
    <div>
        <section>
"""

POSTAMBLE = """     
        </section>
    </div>
    <script src="http://cloud1.tri-di.com/js/jquery-2.1.4.min.js"></script>
    <script src="http://cloud1.tri-di.com/js/isotope.min.js"></script>
    <script src="http://cloud1.tri-di.com/js/scrollreveal.min.js"></script>
    <script src="http://cloud1.tri-di.com/js/parallax.js"></script>
    <script src="http://cloud1.tri-di.com/js/scripts.js"></script>
</body>
</html>
"""


def scandir_index_maker(LOCAL_SCAN_ID_DIR_PATH, full_scan_id):
    index_file_name = "index.html"
    index_file_path = os.path.join(LOCAL_SCAN_ID_DIR_PATH,index_file_name)
    scandir_link="<a href='" + SERVER_UPLOADED_DIR_ROOT_PATH + full_scan_id +"/index.html'>" + full_scan_id + "</a>"
    with open(index_file_path, 'w') as f:
        f.write(PREAMBLE1+full_scan_id+PREAMBLE2+scandir_link+PREAMBLE3)

        for (root, dirs, files) in os.walk(LOCAL_SCAN_ID_DIR_PATH):
            path = root.split(os.sep)
            for filename in sorted(files):
                if filename != "index.html" and filename != ".DS_Store": # don't bother to create an entry because this file will be index.html
                    f.write('            <div class ="col-md-3 col-sm-4 col-xs-6" >\n')
                    f.write('                <a href="' + filename + '">\n')
                    ext = Path(filename).suffix
                    if os.path.isdir(filename):
                        f.write('                <img height = "150px" src="http://cloud1.tri-di.com/images/folder-icon.png" /><br />'
                                + filename)
                    elif ext == '.jpg':
                        f.write('                <img height="150px" src="' + filename + '" /><br /><p>'
                                + filename)
                    elif ext == '.xml':
                        f.write('                <img height = "150px" src="http://cloud1.tri-di.com/images/xml_file_icon.png" /><br /><p>'
                                + filename)
                        # TODO: Need elif's and icons for .zip, photoscene-folder, .obj, .mtl and .stl files
                        # TODO: The Photoscene directory is not showing, but files inside it are. We should indicate
                        #       that these files are inside this directory, when laying out this page.
                        # TODO: The files in the Photoscene directory don't have the right URLs when you click.
                        # TODO: Result01.JPG is not showing an image

                    else:
                        f.write('                <img height = "150px" src="http://cloud1.tri-di.com/images/unknown_file_icon.png" /><br /><p>'
                                + filename)
                    f.write('</p></a>\n')
                    f.write('            </div>\n')
        f.write(POSTAMBLE)
    log = open(index_file_path, "r").read()
    print(index_file_path, "saved")
    # print (log)
    return(log)


def main():
    scan_root = LOCAL_UPLOAD_DIR_ROOT_PATH
    full_scan_id = "VG1.3/20200703210928"
    LOCAL_SCAN_ID_DIR_PATH = os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, full_scan_id)
    scandir_index_maker(LOCAL_SCAN_DIR_ROOT_PATH,full_scan_id)

if __name__ == "__main__":
    # execute only if run as a script
    main()