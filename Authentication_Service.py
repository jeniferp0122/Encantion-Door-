
from authy.api import AuthyApiClient
from datetime import datetime, timedelta
import serial
import time
import sys
import io
import os
import RPi.GPIO as GPIO

def load_user_ids(file_path):
    user_ids = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                user_tag, user_id = line.strip().split(',')
                user_ids[" " + user_tag] = int(user_id)
    return user_ids

authy_api = AuthyApiClient('jtJEfq9PPAdHOALNrt8FsVescO1C6RrZ')
USER_IDS = load_user_ids('user_ids.txt')
TIME_LIMIT = 10

def authenticate_user(user_tag):
    user_id = USER_IDS.get(user_tag)
    if user_id is None:
        print("Unknown user tag")
        return
    response = authy_api.one_touch.send_request(
        user_id,
        "Requesting login for Encation",
        seconds_to_expire=120)
    if response.ok():
        print(response.get_uuid())
    else:
        print(response.errors())

    start_time = time.time()
    approval_status = None
    while approval_status != "approved" and time.time() - start_time < TIME_LIMIT:
        time.sleep(1)
        status = authy_api.one_touch.get_approval_status(response.get_uuid())
        approval_status = status.content["approval_request"]["status"]

    if approval_status == "approved":
        print('yes')
    else:
        print('no')
    return approval_status == "approved"

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
arduino = serial.Serial('/dev/ttyACM0', 9600)
data = []
while True:
    b = arduino.readline()
    string_n = b.decode()
    string = string_n.rstrip()
    s = str(string)
    if s.startswith("Card failed") or s.startswith("Error opening"):
        print(s)
        break
    if s and s not in data:
        print(s)
        data.append(s)
        if s in USER_IDS:
            is_approved = authenticate_user(s)
            if is_approved:
                GPIO.output(17, True)
                GPIO.output(27, True)
                time.sleep(5)
                GPIO.output(17, False)
                GPIO.output(27, False)
