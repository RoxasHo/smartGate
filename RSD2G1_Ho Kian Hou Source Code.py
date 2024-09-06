
# Tues 4:00p.m. - 6:00p.m.
# Title : Smart Gate
# Team Members :
# 1. Ho Kian Hou 22WMR04120
# 2. 
# 3.

# +===========================================================+
# |                     List Imports Here                     |
# +===========================================================+
from time import *
from grovepi import *
from grove_rgb_lcd import *
from pyrebase import pyrebase
from serial import *
from collections import OrderedDict
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# +===========================================================+
# |                   Setup Modules & Ports                   |
# +===========================================================+
buzzer = 2
ultrasonic = 3
gled = 4
rled = 6
button = 8

pinMode(buzzer, "OUTPUT")
pinMode(ultrasonic, "INPUT")
pinMode(gled,"OUTPUT")
pinMode(rled,"OUTPUT")
pinMode(button, "INPUT")

rpiser1 = Serial('/dev/ttyS0', baudrate = 9600, timeout = 1,
                 bytesize = EIGHTBITS, parity = PARITY_NONE,
                 stopbits = STOPBITS_ONE,
                 xonxoff = False, rtscts = False, dsrdtr = False)
rpiser1.flushInput()
rpiser1.flushOutput()

GPIO.setup(32, GPIO.OUT)
p = GPIO.PWM(32, 50)
s = rpiser1.read(14)
p.start(0)

config = {
    "apiKey": "AIzaSyDV2PmmVH8vCyZK3uhLZ8GVkrOPKo-JHjc",
    "authDomain": "smart-gate-3412f.firebaseapp.com",
    "databaseURL": "https://smart-gate-3412f-default-rtdb.asia-southeast1.firebasedatabase.app",
    "storageBucket": "smart-gate-3412f.appspot.com"
    }

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("123callmenewb@gmail.com", "123callmenewb123")
db = firebase.database()

# +===========================================================+
# |                         Functions                         |
# +===========================================================+
def activateSuccessBuzzer():
    digitalWrite(buzzer, 1)
    sleep(0.1)
    digitalWrite(buzzer, 0)
    sleep(0.08)
    
def activateFailedBuzzer():
    digitalWrite(buzzer, 1)
    sleep(0.1)
    digitalWrite(buzzer, 0)
    sleep(0.08)

def activateGLED():
    digitalWrite(gled,1)
    sleep(0.2)
    digitalWrite(rled,0)
    sleep(0.2)

def activateRLED():
    digitalWrite(rled,1)
    sleep(0.2)
    digitalWrite(gled,0)
    sleep(0.2)

def readCard(s):
    if len(s) != 0:
        key = s.hex()
        print("Card Input : " + key)
        
def openGate():
    now = datetime.now()
    print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Gate Opened.")
    p.ChangeDutyCycle(6)      # Changes the pulse width to 9.5 (so moves the servo by 180 degrees)
    sleep(2)                    # Wait 2 seconds 

def closeGate():
    now = datetime.now()
    print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Gate Closed.")
    p.ChangeDutyCycle(3)      # Changes the pulse width to 1.8 (so moves the servo back to the original position)
    sleep(2)                    # Wait 1 second  
    
def findRegisteredRfid(rfid):
    try:
        registerKeys = db.child("Gate01").child("Register").shallow().get().val()
        
        for key in registerKeys:
            data = db.child("Gate01").child("Register").child(key).get().val()
            registeredRFID = data['RFID']
            if (registeredRFID == rfid):
                return True
        return False
    except Exception as e:
        return False

def getRegisteredCarPlate(rfid):
    try:
        registerKeys = db.child("Gate01").child("Register").shallow().get().val()
        
        for key in registerKeys:
            data = db.child("Gate01").child("Register").child(key).get().val()
            registeredRFID = data['RFID']
            if (registeredRFID == rfid):
                return data['car_plate']
    except Exception as e:
        return ("What?")

def getRegisteredDate(rfid):
    try:
        registerKeys = db.child("Gate01").child("Register").shallow().get().val()
        
        for key in registerKeys:
            data = db.child("Gate01").child("Register").child(key).get().val()
            registeredRFID = data['RFID']
            if (registeredRFID == rfid):
                return data['register_date']
    except Exception as e:
        return ("What?")
    
def getExpiryDate(rfid):
    try:
        registerKeys = db.child("Gate01").child("Register").shallow().get().val()
        
        for key in registerKeys:
            data = db.child("Gate01").child("Register").child(key).get().val()
            registeredRFID = data['RFID']
            if (registeredRFID == rfid):
                return data['expired_date']
    except Exception as e:
        return ("What?")

def getRegisteredUserName(rfid):
    try:
        registerKeys = db.child("Gate01").child("Register").shallow().get().val()
        
        for key in registerKeys:
            data = db.child("Gate01").child("Register").child(key).get().val()
            registeredRFID = data['RFID']
            if (registeredRFID == rfid):
                return data['username']
    except Exception as e:
        return ("What?")

def getCurrentTime():
    now = datetime.now()
    utc_offset = now.astimezone().strftime('%z')
    formatted_datetime = now.strftime("%a %b %d %Y %H:%M:%S ") + "GMT" + utc_offset + " (Malaysia Time)"
    return formatted_datetime

def getActionNow(rfid):
    currentAction = ""
    try:
        recordKeys = db.child("Gate01").child("Record").shallow().get().val()
        latestRecord = ""
        for key in recordKeys:
            data = db.child("Gate01").child("Record").child(key).get().val()
            recordedRFID = data['RFID']
            if rfid == recordedRFID:
                latestRecord = data['action']
        if latestRecord == "enter":
            currentAction = "exit"
            return currentAction
        elif latestRecord == "exit":
            currentAction = "enter"
            return currentAction
        currentAction = "enter"
        return currentAction
    except Exception as e:
        currentAction = "enter"
        return currentAction

# +===========================================================+
# |                       Program Start                       |
# +===========================================================+
now = datetime.now()
digitalWrite(rled, 1)
digitalWrite(gled, 0)
print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Program Started.")
setRGB(0,255,255)
setText("Program Started!")
sleep(1.0)
while True:
    try:
        bStatus = digitalRead(button)
        if bStatus:
            digitalWrite(buzzer, 0)
            now = datetime.now()
            print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Buzzer forcibly shut.")
        setRGB(0,255,255)
        setText("Awaiting Sensors......")
        sleep(3.0)
        distance = ultrasonicRead(ultrasonic)
        now = datetime.now()
        print ("[DEBUG] ", now.strftime("%H:%M:%S"), " - Distance Recorded: ", distance)
        if (distance >=1 and distance <=10):
            now = datetime.now()
            print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Vehicle Detected, Distance Ok.")
            scanCard = True
            sleep(1.0)
            
            print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Waiting For Input.")
            setRGB(0,255,0)
            setText("Place Your Card   On The Scanner.")
            sleep(1.0)
            if (scanCard == True):
                sleep(1.5)
                s = rpiser1.read(14)
                if len(s) != 0:
                    rfid = s.hex()
                    now = datetime.now()
                    print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Card Input : " + rfid)
                    if (findRegisteredRfid(rfid)):
                        now = datetime.now()
                        print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Card Identified Successfully.")
                        digitalWrite(buzzer, 1)
                        sleep(0.1)
                        digitalWrite(buzzer, 0)
                        sleep(0.08)
                        carPlate = getRegisteredCarPlate(rfid)
                        registerDate = getRegisteredDate(rfid)
                        expiryDate = getExpiryDate(rfid)
                        userName = getRegisteredUserName(rfid)
                        
                        now = datetime.now()
                        print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Car Plate: ", carPlate)
                        now = datetime.now()
                        print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Register Date: ", registerDate)
                        now = datetime.now()
                        print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Expiry Date: ", expiryDate)
                        now = datetime.now()
                        print("[DEBUG] ", now.strftime("%H:%M:%S"), " - User Name: ", userName)

                        setText("Welcome, "+ userName + "!PlateNo.: " + carPlate)
                        sleep(2.0)
                        setText("Expiry Date:    " + expiryDate)
                        sleep(2.0)
                        setText("Thanks And Have A Nice Day!")
                        activateGLED()
                        openGate()
                        now = getCurrentTime()
                        action = getActionNow(rfid)
                        new_data = {
                            'RFID': rfid,
                            'car_plate': carPlate,
                            'datetime': now
                        }

                        distance = ultrasonicRead(ultrasonic)
                        
                        while (distance <= 5):
                            distance = ultrasonicRead(ultrasonic)
                            now = datetime.now()
                            print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Awaiting Vehicle...")
                            sleep(1)
                            
                        closeGate()
                        newRecordRef = db.child("Gate01").child("Record").push(new_data)
                        # Clear all data after done process
                        rfid = " "
                        s = " "
                        print(rfid)
                    else:
                        digitalWrite(buzzer, 1)
                        sleep(0.1)
                        digitalWrite(buzzer, 0)
                        sleep(0.08)
                        now = datetime.now()
                        print("[DEBUG] ", now.strftime("%H:%M:%S"), " - Card Not Found.")
                        setRGB(255, 0, 0)
                        setText("Card Not Found!")
                        sleep(2.0)
                        newRfidRef = db.child("Gate01").push({ 'newRFID': rfid })
                        # Clear all data after done process
                        rfid = " "
                        s = " "

        elif (distance == 0):
            now = datetime.now()
            print("[ERROR] ", now.strftime("%H:%M:%S"), " - 0 value recorded and ignored.")
            setRGB(255, 0, 0)
            activateRLED()
            scanCard = False
        else:
            now = datetime.now()
            print("[DEBUG] ", now.strftime("%H:%M:%S"), " - No Vehicle Detected.")
            setText("No Vehicle      Detected")
            setRGB(255, 0, 0)
            activateRLED()
            scanCard = False
            sleep(1.0)
            
                   # Resets the GPIO pins back to defaults 
#             results = db.child("PI_001").child("Test").push(key)
#              a = db.child("PI_001").child("Test").get()
#              print("Output : " + a.val())
#             a = db.child("users").child("-NwJuxxSvHmzv4rHy9hf").order_by_child("rfid").equal_to(123456789).get()
#             b = str(a.val())
#             print("Output : " + b)
                #newRfid = db.child("Gate01").child("newRFID").push(key)
            
    except KeyboardInterrupt:
        setText("--------------------------------")
        break
#    except TypeError:
#         print("Type Error")
    except IOError:
        print("IOError")
p.stop() 
GPIO.cleanup()
        



