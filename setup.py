#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
py2app/py2exe build script for SonaScan (s*).
Will automatically ensure that all build prerequisites are available via ez_setup
Usage (Mac OS X):
build with: python3 setup.py py2app
distribute: package .app into a .dmg for download
install: user should drag s*.app file into /Applications
run with: open s*.app

Usage (Windows):
build with: python3 setup.py py2exe
distribute: package into a .zip file for download
install: unzip and place s*.exe in Program_Files directory
run with: open s*.exe

Usage (Python Wheel):
build with: python3 setup.py bdist-wheel
distribute: via PyPi.org/s*
install with: pip3 install s*.whl:
run with: python3 s*

Usage (Source):
build with: python3 setup.py sdist
distribute: download s*.tar.gz
install: gunzip s*.tar.gz
run with: python3 s*

"""
# import ez_setup, ez_setup.use_setuptools()
import sys
import re
import platform
import socket
import uuid
from setuptools import setup, find_packages

setup_requires = ['py2app'],
mainscript = 'src/main.py'  # app = ['src/main.py'],

if sys.platform == 'darwin':
    extra_options = dict( setup_requires=['py2app'], app=[mainscript]
    # Cross-platform applications generally expect sys.argv to # be used for opening files. options=dict(py2app=dict(argv_emulation=True)),
    )
    ENVIRONMENT = "MacOS X"
    OPERATING_SYSTEM = "MacOS:: MacOS X"
    PLATFORM = "macos64"
    PLATFORM_SYSTEM = 'Darwin'
    EXECUTABLE_EXTENSION = ".app"
elif sys.platform == 'win32':
    extra_options = dict( setup_requires=['py2exe'], app=[mainscript],)
    ENVIRONMENT = "Win64 (MS Windows)"
    OPERATING_SYSTEM = "Microsoft :: Windows :: Windows 10"
    PLATFORM = "win64"
    PLATFORM_SYSTEM = 'Windows'
    EXECUTABLE_EXTENSION = ".exe"
elif sys.platform == 'linux':
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install" # and install the main script as such scripts=[mainscript],
    )
    ENVIRONMENT = "X11 Applications :: Qt"
    OPERATING_SYSTEM = "POSIX :: Linux"
    PLATFORM = "linux64"
    PLATFORM_SYSTEM = 'linux'
    EXECUTABLE_EXTENSION = ""
else:
    extra_options = dict(
    # Normally unix-like platforms will use "setup.py install" # and install the main script as such scripts=[mainscript],
    )
    ENVIRONMENT = "Other Environment"
    # "Environment :: Handhelds/PDA's",
    # 'Environment :: Web Environment',
    OPERATING_SYSTEM = "UNKNOWN"
    # 'Operating System :: iOS',
    # 'Operating System :: PDA Systems',  # Android?
    PLATFORM = "UNKNOWN"
    EXECUTABLE_EXTENSION = ""

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

OPTIONS = {
    'iconfile':'AnyConv.com__orange-icon.icns',
}

HOSTNAME = socket.gethostname()
MAC_ID = ':'.join(re.findall('../..', '%012x' % uuid.getnode()))
UNIQ_ID_FOLDER_NAME = "*/"+HOSTNAME+"/"
SYSTEM_IDENTIFIER = platform.system()

# TODO: make sure permissions on installed pemfile are rw--------
# TODO: make sure latest meshlab binary for target platform is installed
# TODO: make sure latest ffmpeg  binary for target platform  is installed
# TODO: make sure latest ffmpeg  binary for target platform  is installed
# TODO: make sure py2app is creating working apps for MacOS


setup(
    name='sonascan-mcgregor94086',
    **extra_options,
    version='0.0.3.dev3',
    packages=find_packages(exclude=[UNIQ_ID_FOLDER_NAME]),
    # package_dir={"": "src"},   # tell distutils packages are under src
    include_package_data=True,    # include everything in source control
    # ...but exclude */ScottM-MBP-2020/* from all packages
    exclude_package_data={"": [UNIQ_ID_FOLDER_NAME]},
    url='test.pypi.org/sonautics/sonascan',
    license='Copyright (c) 2020 by Sonautics, Inc; All Rights Reserved; For licensing contact information, contact:  steve@sonautics.com',
    author='Scott McGregor',
    author_email='scott@sonautics.com',
    description='Sonascan ia an automated program for creating 3D images on a SonaScanner',
    long_description=LONG_DESCRIPTION,  # use the README file for long description in PyPi
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.8',
        'Environment :: '+ ENVIRONMENT,
        # "Environment :: Handhelds/PDA's",
        # 'Environment :: Other Environment'
        # 'Environment :: Web Environment',
        # 'Environment :: Win32 (MS Windows)',
        # 'Environment :: X11 Applications :: Qt',

        # Specify the Operating Systems supported
        'Operating System :: MacOS :: MacOS X',
        # 'Operating System :: Microsoft :: Windows :: Windows 10',
        # 'Operating System :: POSIX :: Linux',
        # 'Operating System :: iOS',
        # 'Operating System :: PDA Systems',
    ],
    options={'py2app': OPTIONS},
    keywords='3D Scanner',
    project_urls={
        # An arbitrary map of URL names to hyperlinks, allowing more extensible documentation of where
        # various resources can be found than the simple url and download_url options provide.
        # TODO Set the project Documentation, Funding and Thanks! URLs
        # 'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/mcgregor94086',
        'Source': 'https://github.com/sonautics/sonascan',
        'Tracker': 'https://github.com/sonautics/sonascan/issues',
    },


    ################################### THESE ARE USED TO SUPPORT CREATING A STANDALONE APP ON MACOS ##################
    data_files=[('_failed_scans', ['_failed_scans/index.html']),
                ('_models',       ['_models/VIRTUAL',   '_models/index.html']),
                ('_scans',        ['_scans/VIRTUAL',    '_scans/index.html']),
                ('_uploaded',     ['_uploaded/VIRTUAL', '_uploaded/index.html']),
                ('ssh', ['ssh/tridi-mpl.pem']),
                ('', ['AnyConv.com__orange-icon.icns', 'setup.cfg', 'images','external_app_bin']),
               ],
    # data_files=['AnyConv.com__orange-icon.icns', 'ssh/tridi-mpl.pem'],
    # Warning data_files is deprecated. It does not work with wheels, so it should be avoided.
    # A list of strings specifying the data files to install.

    # Using setup_requires is DISCOURAGED in favor of PEP 518
    # A string or list of strings specifying what other distributions need to be present in order for the setup 
    # script to run. setuptools will attempt to obtain these (even going so far as to download them using 
    # EasyInstall) before processing the rest of the setup script or commands. This argument is needed if you are 
    # using distutils extensions as part of your build process; for example, extensions that process setup() 
    # arguments and turn them into EGG-INFO metadata files.
    # (Note: projects listed in setup_requires will NOT be automatically installed on the system where the 
    # setup script is being run. They are simply downloaded to the ./.eggs directory if they’re not locally 
    # available already. If you want them to be installed, as well as being available when the setup script is run, 
    # you should add them to install_requires and setup_requires.)
    ############################### END THESE ARE USED TO SUPPORT CREATING A STANDALONE APP ON MACOS ##################

    ##########################################################################################
    # install_requires= , # A string or list of strings specifying what other distributions need to be installed when this one is. See the section on Declaring Dependencies for details and examples of the format of this argument.
    #
    # TODO: Refactor ffmpeg, and meshconv, meshlab so that they are platform contingent
    #       installs,  using install_requires ?
    install_requires=[
                        'py2app',
    #                   "external_app_bin/macos64/ffmpeg; platform_system='Darwin'",
    #                   "external_app_bin/macos64/meshconv; platform_system='Darwin'",
    #                   "external_app_bin/macos64/meshlab.app; platform_system='Darwin'",
    #                   "external_app_bin/linux64/ffmpeg-4.3-amd64-static/ffmpeg; platform_system='linux'",
    #                   "external_app_bin/linux64/ffmpeg-4.3-arm64-static/ffmpeg; platform_system='linux'",
    #                   "external_app_bin/linux64/ffmpeg-4.3-armel-static/ffmpeg; platform_system='linux'",
    #                   "external_app_bin/linux64/ffmpeg-4.3-armhf-static/ffmpeg; platform_system='linux'",
    #                   "external_app_bin/linux64/ffmpeg-4.3-i686-static/ffmpeg; platform_system='linux'",
    #                   "external_app_bin/linux64/meshconv; platform_system='linux'",
    #                   "external_app_bin/linux64/meshlab; platform_system='linux'",
    #                   "external_app_bin/win64/ffmpeg.exe; platform_system='Windows'",
    #                   "external_app_bin/win64/meshconv.exe; platform_system='Windows'",
    #                   "external_app_bin/win64/meshlab.exe; platform_system='Windows'",
                     ],
    ##########################################################################################

)

