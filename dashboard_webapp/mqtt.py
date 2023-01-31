import paho.mqtt.client as mqtt
import mysql.connector

import cv2
import numpy as np
from base64 import b64decode

import io
from PIL import Image


def db_insert(query, param):
    Connection = mysql.connector.connect(host="localhost", user="root", password="!password")
    Cursor = Connection.cursor(buffered=True)
    Connection.connect()
    Cursor.execute("USE dashboard_webapp")
    try:
        Cursor.execute(query, param)
        Connection.commit()
    except:
        print('fail to insert to db')
    Connection.close()


def db_retrieve(query, param):
    Connection = mysql.connector.connect(host="localhost", user="root", password="!password")
    Cursor = Connection.cursor(buffered=True)
    Connection.connect() 
    Cursor.execute("USE dashboard_webapp")
    try:
        Cursor.execute(query, param)
        returned_rows = Cursor.fetchall()
        Connection.close()
        return returned_rows
    except (mysql.connector.DatabaseError, mysql.connector.OperationalError) as e:
        print('fail to retrieve from db')
        Connection.close()
        return []


def clientconn():   
    global client
    client = mqtt.Client("DESKTOP-8LHT5CI")
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect("192.168.1.12", 1883, 60) 
        print('connected to broker')
    except:
        print('fail to connect to broker')


def on_connect(client, userdata, flags, rc):    
    client.subscribe("raspberry/#")   

rpi_id = 0

def on_message(client, userdata, msg):
    global rpi_id

    if msg.topic == "raspberry/mac":

        # if raspberry id is known, skip
        if rpi_id != 0:
            return

        gdata0 = msg.payload.decode("utf-8")
        rbmac = gdata0
        print("received '{}'".format(msg.topic))

        ReturnedRows = db_retrieve(
            "SELECT `id` FROM dashboard_webapp_raspberry WHERE mac_address=%s", 
            [rbmac]
        )  

        if len(ReturnedRows) == 0:
            print('Raspberry not registered in database')

        if len(ReturnedRows) != 0:
            print('Raspberry verified')
            rpi_id = ReturnedRows[0][0]
            
    if msg.topic == "raspberry/camera/thermal":
        gdata1 = msg.payload.decode("utf-8")

        # if raspberry id unknown, do nothing
        if rpi_id == 0:
            return

        # Extract JPEG-encoded image from base64-encoded string
        JPEG_r = b64decode(gdata1)

        # Decode JPEG back into Numpy array
        img_arr = cv2.imdecode(np.frombuffer(JPEG_r,dtype=np.uint8), cv2.IMREAD_COLOR)
        
        # Get image
        img = Image.fromarray(img_arr)
        
        # Convert image to bytes (transfer to rpi)
        b = io.BytesIO()
        img.save(b, 'jpeg')
        img_blob = b.getvalue()
        
        # Insert image into database
        db_insert(
            "INSERT INTO dashboard_webapp_thermalcaptures VALUES (NULL, %s, NOW(), %s)", 
            [rpi_id, img_blob]
        )

        print("received '{}'".format(msg.topic))

    if msg.topic == "raspberry/camera/rgb":
        gdata2 = msg.payload.decode("utf-8")

        # if raspberry id unknown, do nothing
        if rpi_id == 0: 
            return

        # Extract JPEG-encoded image from base64-encoded string
        JPEG_r = b64decode(gdata2)

        # Decode JPEG back into Numpy array
        img_arr = cv2.imdecode(np.frombuffer(JPEG_r,dtype=np.uint8), cv2.IMREAD_COLOR)
        
        # Get image
        img = Image.fromarray(img_arr) 
        
        # Convert image to bytes
        b = io.BytesIO()
        img.save(b, 'jpeg')
        img_blob = b.getvalue()
        
        # Insert image to database
        db_insert(
            "INSERT INTO dashboard_webapp_rgbcaptures VALUES (NULL, %s, NOW(), %s)", 
            [rpi_id, img_blob]
        )

        print("received '{}'".format(msg.topic))

    if msg.topic == "raspberry/sensor/smoke":
        gdata3 = msg.payload.decode("utf-8")

        # if raspberry id unknown, do nothing
        if rpi_id == 0:
            return

        reading_split = gdata3.split(';')

        if len(reading_split) == 7: 

            co = reading_split[1]
            nh3 = reading_split[2]
            ch2o = reading_split[3]
            hcn = reading_split[4]
            voc = reading_split[5]

            db_insert(
                "INSERT INTO dashboard_webapp_smokereading VALUES (NULL, %s, NOW(), %s, %s, %s, %s, %s, %s)", 
                [rpi_id, 1, co, nh3, ch2o, hcn, voc]
            )

        print("received '{}'".format(msg.topic))

