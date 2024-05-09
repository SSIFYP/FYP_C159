import serial 
from  time import sleep, strftime
import time
import os 
import paho.mqtt.publish as publish
import threading

MQTT_SERVER = "192.168.1.1"
MQTT_PORT = 1883
MQTT_PATH = "footrest"


COM_PORT = '/dev/ttyUSB0' 
ser = serial.Serial(COM_PORT, baudrate = 115200, timeout=1)

fst = ser.read_until(b"\r\n")

if (len(fst.hex()))==None:
    print("Check if plates are on.")


g = 9.81 
rightoffset = 5
leftoffset = -7
left_kg_value = 0
left_newton_value = 0
right_kg_value =0
right_newton_value =0
counter = 0
while True: 
    ser.flushInput()
    fst = ser.read_until(b"\r\n")
    if len(fst.hex()) == 42:
            break

def serial_read ():
    global left_kg_value , left_newton_value ,right_kg_value , right_newton_value , counter
    start_time = time.time()
    with open("/home/footrest/Desktop/footrest.csv" , "a") as log:
        while True:
            #fst = ser.read_until(b"\r\n")
            #dt_hex = fst.hex()
            #ser.flushInput()
            dt_hex=ser.read(21).hex()
            print(dt_hex)
            # Extract digit 11th to 14th
            right_hex_value = dt_hex[10:14]
            # Convert hex to decimal
            right_decimal_value = int(right_hex_value, 16)
            # Add offset
            right_decimal_value = right_decimal_value + rightoffset
            # 2's complement
            if right_decimal_value > 32767:
                right_decimal_value -= 65536
            # Convert to kg
            right_kg_value = right_decimal_value / 10.0
            # Convert to Newton
            right_newton_value = right_kg_value * g

            # Extract digit 7th to 10th
            left_hex_value = dt_hex[6:10]
            # Convert hex to decimal
            left_decimal_value = int(left_hex_value, 16)
            # Add offset
            left_decimal_value = left_decimal_value + leftoffset
            # 2's complement
            if left_decimal_value > 32767:
                left_decimal_value -= 65536
            # Convert to kg
            left_kg_value = left_decimal_value / 10.0
            # Convert to Newton
            left_newton_value = left_kg_value * g 
            print("Left and Right kg = ", left_kg_value, "kg , ", right_kg_value, "kg")
            print("Left and Right Force = ", left_newton_value, "N , ", right_newton_value, "N") 
            #ser = serial.reset_input_buffer()      
            counter = counter +1
            print(counter/(time.time() - start_time))
            log.write("{0},{1}, {2} \n".format(
            strftime("%Y-%m-%d %H:%M:%S"),
            str(left_newton_value), str(right_newton_value)
                        )) 
            #break;


def MQTT (): 
    global left_newton_value, right_newton_value
    while True:
        message = f" {left_newton_value}, {right_newton_value}" 
        publish.single(MQTT_PATH, message, hostname=MQTT_SERVER , port =MQTT_PORT) 
    '''try:   
        message = f" {left_newton_value}, {right_newton_value}"  
        publish.single(MQTT_PATH, message, hostname=MQTT_SERVER , port =MQTT_PORT)
    except Exception as e:
        print(f"error publishing : {e} ")'''
    #await asyncio.sleep(0.0)

t1 = threading.Thread(target=serial_read)
t2 = threading.Thread(target=MQTT)
t1.start()
t2.start()

t1.join()
t2.join()