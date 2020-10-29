"""
forge.py

forge.py contains all the data needed to get autodesk forge tokens and run autodesk forge reality capture API jobs
"""


# Global includes
import json
import os
from io import StringIO

import paramiko
import requests
import time
import uuid
import zipfile


# local includes
from src.CONSTANTS import  LOCAL_UPLOAD_DIR_ROOT_PATH
# from debugging import get_line_number, FILENAME
# from ffmpeg import syscmd
from src.index_maker import scandir_index_maker

# Autodesk Forge (2D images to 3D modeling service) constants
FORGE_URL = 'https://developer.api.autodesk.com'
WAIT_TIME = 10
CLIENT_ID = 'HAqDtKO7VbuRgH0nL0MFJ0B02ElBEK3l'
CLIENT_SECRET = 'oHihWQG1XJ1G9aNV'

# SERVER RELATED CONNECTION CONSTANTS
uniq_id = uuid.uuid1()  # Generates a UUID from a host ID, sequence number, and the current time
remote_userid = 'scansteruser'
server_hostname = 'cloud1.tri-di.com'
PEM_KEY_FILE = os.path.abspath("ssh/tridi-mpl.pem")
print(PEM_KEY_FILE)

my_key = """\
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAz3Bmkhnh42llhxTRyazdB91GLjuxhW1F07VK+1DFMBVhoMzt
AHnQozZoLWXCE11k6rRnBAsH395s7kocqujCyFQKQfqIHHWGDDvJYAVlZqMZOp4B
5qjKCiVIrSIlfFFxNK6xu4x2bJmIXkyuqEbWcJLbwxlISdSnIw1Mpp97y/J8KZV4
VI+V/sFAZOGqS88oi07Z1MncmaGl5cESydAJAYsfdG0JCbHa+JYl/72YEmf23tcp
KpiNNSxifAfSLb9cJiBJMf+SGlZYq324DHIh9d45qDtzMVReXVs5Mk7Tb8AhQCjR
TERrr0nU2BCxIcEa1rLTKkKRtgAAhjSgkQ8nUQIDAQABAoIBAQCvsr9d3ghCyuGQ
kWTDUeQApj2sKSlKHuy2zWZOCPKLsIB5ZzkSXxsFMq74TKkeJ8uzM8vRU9p+lnFj
P2iapf1dGjl5+s5QdIZuVDFTYB6r2VckG/L2QF6oSz4MTtC7RGwDODgX53fisgQc
Aw0oQJ+ex/TVgdOFnVVXTgtvUcPUT+4xHoKCTrzX4nfIUv5Ec6d0UYU4dPw3DEQ/
cRVQasTAwXMzU+Rz+nR3A1iLQr8595+sn44ZLfQb6D32pOR0v9oDAoA7NLy+PI5o
GHzzOT8LnudLVJ4XOmZnQaX7YjWsOXjn/iTbxQsh+OCWvV5NKY/vXhd8/e8clGJ/
IiAbQrLFAoGBAPQIopr5A3DV+H1it5Fk7exD4Y43Mw5Y/AyiFE27wSuwqogWlPvR
gUx5Ax6462DaqpkawWsh99ZD9QFElFqaRsl3TSfbKkwffap1VQhPFY2aRWulNKGD
0MYo1Xvuz4o8x+JeTrMkI4iSByYCJ6eNdgT9ayRApgVn5gMOfkLs73pLAoGBANmc
ZCgnVwnxG71t1rPrHlV5SAPjKah+usU4rI8IqWvQxcmNzWPYQQvvLX7jHaw7NWHq
XfE9jtQXAknfMvXiAnbXewYogKCfH8+aYmwVwHGP2E5O5sTuah/65G8CZ4s2Gbon
vW/y1Y6y2wFx8Gler4R5T8S9eCtQsOwY0gR1ruNTAoGAFIJ1SBkNlPomvEMDspCM
/oJl/pHdFKOd62Hj2vSgs49RhcaAFvnwqACzpm1cOvOlyuBYySw9rCBiAw1Eeqjk
siH4thTRZTxwT1c1IlGjOhdxJi7oUXrGnSDpcFUN1ExvcDME4kFzSxMazrL3qjlV
Ze32h0F3spSc3Dznl7BaICkCgYBgFwHXBUAW4MO6CuVyvxC+93YIWWfMwmEgs1zn
MBD3zdF4pcgbHaPjbDLvw8QXiHGTEhV3cBJArwRQsGFlV+50ocPuPTZHNtyqJGbv
iU9YFgeS1J5sOUbdZkE2j54/R51mqSOqalVI1MuGQNTDAo+IdLT3kB6fKdtl9bPP
SlP2hwKBgDZHeJbL+o6Zw8oSEvRet3GYfaEL1ZrCwDw+xBjmOHUdM6+sCu4JYwVk
/DEgggFLoRVfMC+y33J0SQP+XKSMFFw1ICSTM27xPK9Gw8FCc9Tar83IohKesWQP
u279mz5fwlDWqXhAwzIDLXWrpAb3XAj3c+z24u6HqWUWZfMIssZf
-----END RSA PRIVATE KEY-----"""

# PEM_KEY = paramiko.RSAKey.from_private_key(StringIO(my_key))
PEM_KEY = paramiko.RSAKey.from_private_key_file(PEM_KEY_FILE)
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=server_hostname, username=remote_userid, pkey=PEM_KEY)

# max_wait_time_for_Forge_server = 180  # time in seconds

def get_forge_token():
    """
    get_forge_token() gets Forge token

    get_forge_token() gets Forge token
    """
    tic = time.perf_counter()
    url = FORGE_URL + '/authentication/v1/authenticate'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'data:read data:write'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # request a forge_token
    r = requests.post(url, data=data, headers=headers)
    content = eval(r.content)

    if 200 != r.status_code:
        print(r.status_code)
        print(r.headers['content-type'])
        print(type(r.content))
        print(content)
        # -- example results --
        # 200
        # application/json
        # {"token_type":"Bearer","expires_in":1799,"access_token":"ESzsFt7OZ90tSUBGh6JrPoBjpdEp"}
        print("Authentication returned status code %s." % r.status_code)
        # raise SystemExit(6)
        toc = time.perf_counter()
        print(f"No Forge token received - in: {toc - tic:0.0f} seconds")
        return ""
    else:
        access_token = content['access_token']
        toc = time.perf_counter()
        print(f"Got Forge token in: {toc - tic:0.0f} seconds")
        return access_token



async def process_scan(scan_ID, from_email, to_email):
    """
    process_scan(scan_ID, from_email, to_email) launches the 3D modeling on the Sonautics Cloud server

    process_scan(scan_ID, from_email, to_email) launches the 3D modeling on the Sonautics Cloud server
    """
    tic = time.perf_counter()
    uniq_id = uuid.uuid1()  # Generates a UUID from a host ID, sequence number, and the current time
    remote_userid = 'scansteruser'
    server_hostname = 'cloud1.tri-di.com'
    pem_key = os.path.normpath(PEM_KEY_FILE)
    submit_to_Forge_cmd = "/bin/bash /home/scansteruser/cloud1.tri-di.com/sh/sonascan_submit_file_to_Forge.sh '" \
          + scan_ID + "' '" + from_email + "' '" + to_email + "' '" + str(uniq_id) + "'"

    private_key = paramiko.RSAKey.from_private_key_file(pem_key)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=server_hostname, username=remote_userid, pkey=private_key)

    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(submit_to_Forge_cmd)
    except Exception as e:
        print("Error", repr(e) )
        print("Unable to begin processing scan", scan_ID, "will try again later.")
        return ''
    access_token = ''
    photoscene_id = ''
    for line in ssh_stdout:
        print(line)
        if line.startswith("forge_access_token: "):
            access_token = line[20:].rstrip()
            print("access_token:", access_token)
        if line.startswith("Created Photoscene: "):
            photoscene_id = line[20:].rstrip()
            print("photoscene_id:", photoscene_id)
    for line in ssh_stderr:
        print("stderr:", line)

    if photoscene_id != '':
        # TODO: We should probably update the GUI with the photoscene_id,

        manifest_file_name = os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, scan_ID, "manifest.xml")
        with open(manifest_file_name) as manifest_file:
            manifest_string = manifest_file.read().replace("PHOTOSCENE_ID_NOT_YET_ASSIGNED", photoscene_id)
        # Save a directory with the photoscene name inside the LOCAL uploaded scanDir
        photoscene_dir_path = os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, scan_ID,
                                           "photoscene-" + photoscene_id)
        if not os.path.exists(photoscene_dir_path):
            os.makedirs(photoscene_dir_path)

        toc = time.perf_counter()
        print(f"Started processing {scan_ID} in: {toc - tic:0.0f} seconds")
        return photoscene_id, access_token
    else:
        print("Server Connection Error:")
        # print("Unable to upload local scan directory", source_dir, "to ", dest_dir, "on server. Will try again later.")
        print("Unable to get a photoscene_id for scan ", scan_ID, " - will try again later.")
        toc = time.perf_counter()
        print(f"Failed processing for {scan_ID} in: {toc - tic:0.0f} seconds")
        return photoscene_id, access_token
    # this line is unreachable.


def monitor_scan_dir(scan_id, photoscene_id, access_token, window):
    """
    monitor_scan_dir(scan_id, photoscene_id, access_token) monitors photoscene processing on Autodesk Forge until it completes.

    monitor_scan_dir(scan_id, photoscene_id, access_token)  monitors photoscene processing on Autodesk Forge until it completes.
    """
    tic = time.perf_counter()
    print("Processing photoscene:", photoscene_id)

    url = FORGE_URL + '/photo-to-3d/v1/photoscene/' + photoscene_id + '/progress'
    headers = {
        'Content-Type': 'text/xml',
        'Authorization': 'Bearer ' + access_token,
    }
    # poll for progress
    errcode = 0
    progressmsg = 'CREATED'
    while (progressmsg != "DONE") and (progressmsg != "ERROR"):

        r = requests.get(url, headers=headers)
        # print("status code=", r.status_code)
        responseXml = json.loads(r.text)

        # if (r.status_code == 200):

        if 'Photoscene' in responseXml:
            progressmsg = responseXml['Photoscene']['progressmsg']
            progress = responseXml['Photoscene']['progress']
            beat = time.perf_counter()
            msg = str(f"{beat - tic:0.0f}") +" seconds: modeling status=' " + progressmsg + "': " + progress + "% complete."
            print(msg)
            window.FindElement('_ACTION_STATUS_LINE_3_').Update(msg)
            window.Refresh()
            errorcode = 0

        if 'Error' in responseXml:
            errorcode = responseXml['Error']['code']
            errormsg = responseXml['Error']['msg']
            print("Error:", errorcode, errormsg)
            toc = time.perf_counter()
            print("HTTP return code =", r.status_code)
            print(f"Failed to complete Model in: {toc - tic:0.0f} seconds")
            raise SystemExit(6) # return progressmsg

        if r.status_code != 200:
            toc = time.perf_counter()
            print("HTTP return code =", r.status_code)
            print(f"Failed to complete Model in: {toc - tic:0.0f} seconds")
            raise SystemExit(6)  # return progressmsg

        time.sleep(WAIT_TIME)  # Wait 10 seconds

    toc = time.perf_counter()
    print(f"Completed Modeling of {scan_id}/photoscene-{photoscene_id}  in: {toc - tic:0.0f} seconds")
    return progressmsg


def get_obj(scan_id, photoscene_id, access_token, from_email, to_email, consumer_id, order_details, window):
    """
    get_obj(scan_id, photoscene_id, access_token) retreives an OBJ model from Autodesk Forge.

    get_obj(scan_id, photoscene_id, access_token) retreives an OBJ model from Autodesk Forge.
    """
    tic = time.perf_counter()
    print("Retrieving OBJ for photoscene:", photoscene_id)

    url = FORGE_URL + "/photo-to-3d/v1/photoscene/" + photoscene_id
    print(url)
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + access_token,
               }
    print(headers)
    data = {'format': 'obj'}
    print(data)
    response = requests.get(url,
                            # auth=BearerAuth(access_token),
                            headers=headers,
                            data=data
                            )
    json_object = response.json()
    json_string = json.dumps(json_object)
    print(json_string)
    # filesize = json_object['Photoscene']['filesize']
    # print(filesize)
    # resultmsg = json_object['Photoscene']['resultmsg']
    # print(resultmsg)

    scenelink = json_object['Photoscene']['scenelink']
    obj_dir = os.path.join(LOCAL_UPLOAD_DIR_ROOT_PATH, scan_id, "photoscene-" + photoscene_id)
    obj_zip = os.path.join(obj_dir, "model.obj.zip")
    # print("scenelink=", scenelink)

    # curl_cmd = "curl -o obj_zip scenelink";
    r = requests.get(scenelink, stream=True)

    with open(obj_zip, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            fd.write(chunk)

    if os.path.exists(obj_zip):
        with zipfile.ZipFile(obj_zip, 'r') as zip_ref:
            zip_ref.extractall(obj_dir)
            # obj_file = os.path.join(obj_dir, 'result.obj')
            # if os.path.exists(obj_file):
            #    open_3D_model_Request = "open -a " + PATH_TO_MODEL_VIEWER_APP + " " + obj_file + "&"
            #    print(open_3D_model_Request)
            #    syscmd(open_3D_model_Request)
            # else:
            #    print("ERROR: Could not find", obj_file)
    else:
        print("ERROR: could not unzip", obj_zip)

    # TODO: IMPORTANT!!! Trim walls and floors from OBJ
    #                    and convert Trimmed model to STL
    command = "/bin/bash /home/scansteruser/cloud1.tri-di.com/sh/sonascan_get_obj.sh " \
              + " '" + scan_id + "' " \
              + " '" + photoscene_id + "' " \
              + " '" + from_email + "' " \
              + " '" + to_email + "' " \
              + " '" + consumer_id + "' " \
              + " '" + order_details + "' "
    print()
    print("Executing {}".format(command))
    print()
    stdin, stdout, stderr = ssh_client.exec_command(command)
    print(stdout.read())
    print("Errors")
    print(stderr.read())
    # window.FindElement('_ACTION_STATUS_LINE_1_').Update("Modeling Complete")
    # window.FindElement('_ACTION_STATUS_LINE_2_').Update("Ready for next scan")
    window.FindElement('_ACTION_STATUS_LINE_3_').Update( "Modeling Complete")
    window.Refresh()
    # Update the local version of index.html in the UPLOADS directory
    scandir_index_maker(LOCAL_UPLOAD_DIR_ROOT_PATH, scan_id)

    # TODO: Update the SERVER SIDE version of index.html
    # scandir_index_maker(http://cloud1.tri-di.com/scans/", scan_ID)

    # Open directory index.html  file in a new page (“tab”) of the default browser, if possible


    # TODO: Move UPLOADED DIRECTORY to MODELS directory

    toc = time.perf_counter()
    print(f"Completed Modeling of {scan_id}/photoscene-{photoscene_id}  in: {toc - tic:0.0f} seconds")
    return scenelink


def main():
    get_forge_token()


    if __name__ == "__main__":
        # execute only if run as a script
        main()
