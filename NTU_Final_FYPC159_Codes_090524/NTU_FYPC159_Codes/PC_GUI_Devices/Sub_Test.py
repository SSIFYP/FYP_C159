import paho.mqtt.client as mqtt
from time import sleep, strftime, time
import threading
import time
MQTT_SERVER = "192.168.1.1"
MQTT_PATH1 = "boat_IMU"
MQTT_PATH2 = "boat_GPS"
MQTT_PATH3 = "esp32_left"
MQTT_PATH4 = "esp32_right"
MQTT_PATH5 = "footrest"

ax= 0.0
ay=0.0
az=0.0 
gx=0.0 
gy=0.0 
gz=0.0 
roll=0.0 
pitch=0.0 
yaw =0.0

plat=0.0 
plon=0.0 
clat=0.0 
clon=0.0 
dist_travl=0.0  
total_dist =0.0

Paddle_Left=0.0 
Paddle_right=0.0

footrest_left=0.0 
footrest_right = 0.0
counter = 0.0
start_time = time.time()
adjust_delay = 60.0

def on_connect1(client1, userdata, flags, rc):
    #print("Connected with result code " + str(rc))
    client1.subscribe(MQTT_PATH1)
def on_connect2(client2, userdata, flags, rc):
    #print("Connected with result code " + str(rc))
    client2.subscribe(MQTT_PATH2)
def on_connect3(client3, userdata, flags, rc):
    #print("Connected with result code " + str(rc))
    client3.subscribe(MQTT_PATH3)
def on_connect4(client4, userdata, flags, rc):
    #print("Connected with result code " + str(rc))
    client4.subscribe(MQTT_PATH4)       
def on_connect5(client5, userdata, flags, rc):
    #print("Connected with result code " + str(rc))
    client5.subscribe(MQTT_PATH5)    

def on_message1(client1, userdata, msg):
    global ax,ay,az, gx,gy,gz, roll, pitch, yaw 

    message = msg.payload.decode('utf-8')

    ax,ay,az ,gx,gy,gz, roll, pitch, yaw = message.split(',')
    ax = float(ax)
    ay = float(ay)
    az = float(az)
    gx = float(gx)
    gy = float(gy)
    gz = float(gz)
    roll = float(roll)
    pitch = float(pitch)
    yaw = float(yaw)
    #print(f"From Raspberry pi 4  IMU : ax: {ax}, ay: {ay}, az: {az},gx: {gx}, gy: {gy}, gz: {gz}, Roll: {roll}, Pitch: {pitch}, Yaw: {yaw} ")

def on_message2(client2, userdata, msg):
    global plat, plon,clat,clon ,dist_travl, total_dist 

    message = msg.payload.decode('utf-8')

    plat,plon, clat, clon, dist_travl, total_dist = message.split(',')
    plat = float(plat)
    plon = float(plon)    
    clat = float(clat)
    clon = float(clon)
    dist_travl = float(dist_travl)
    total_dist = float(total_dist)
    #print(f"From Raspberry pi 4  GPS : clat: {clat}, clon: {clon}, dist_travl: {dist_travl}, total_dist: {total_dist} ")

def on_message3(client3, userdata, msg):
    global Paddle_Left ,counter

    message = msg.payload.decode('utf-8')

    Paddle_Left = message
    
    Paddle_Left = float(Paddle_Left)

    #print(f"From Esp32 Left : x:  , {counter}, {Paddle_Left} ")

def on_message4(client4, userdata, msg):
    global Paddle_right

    message = msg.payload.decode('utf-8')

    Paddle_right = message
    
    Paddle_right = float(Paddle_right)

    #print(f"From Esp32 Right : x: {Paddle_right} " )

def on_message5(client5, userdata, msg):
    global footrest_left, footrest_right

    message = msg.payload.decode('utf-8')

    footrest_left , footrest_right = message.split(",")

    #print(f"From footrest  : Left, Right :  , {footrest_left} , {footrest_right}  ")

def MQTT1 ():
    client1 = mqtt.Client()
    client1.on_connect = on_connect1
    client1.on_message = on_message1
    client1.connect(MQTT_SERVER, 1883, keepalive=60)
    client1.loop_start()
def MQTT2 ():
    client2 = mqtt.Client()
    client2.on_connect = on_connect2
    client2.on_message = on_message2
    client2.connect(MQTT_SERVER, 1883, keepalive=120)
    client2.loop_start()
def MQTT3 ():
    client3 = mqtt.Client()
    client3.on_connect = on_connect3
    client3.on_message = on_message3
    client3.connect(MQTT_SERVER, 1883, keepalive=120)
    client3.loop_start()
def MQTT4 ():
    client4 = mqtt.Client()
    client4.on_connect = on_connect4
    client4.on_message = on_message4
    client4.connect(MQTT_SERVER, 1883, keepalive=120)
    client4.loop_start()
def MQTT5 ():
    client5 = mqtt.Client()
    client5.on_connect = on_connect5
    client5.on_message = on_message5
    client5.connect(MQTT_SERVER, 1883, 60)
    client5.loop_start()

def recorder():
    global counter
    start_time = time.time()
    while True: 
        with open("C:/Users/daren/OneDrive/Desktop/FYP_Merge_180224/FYP_CSV_Log_Location/Integratuib070324.csv" , "a") as log: 
                time.sleep((1.0-(adjust_delay/2800.0))/(adjust_delay/0.5))
                #time.sleep(1)          
                log.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18}, {19} \n".format(
                strftime("%Y-%m-%d %H:%M:%S"),
                str(ax), str(ay), str(az), str(gx), str(gy), str(gz), str(roll), str(pitch), str(yaw),
                str(plat), str(plon), str(clat), str(clon), str(dist_travl), str(total_dist),
                str(Paddle_Left), str(Paddle_right), 
                str(footrest_left), str(footrest_right)
                            ))   
                counter = counter +1 
                print(counter / (time.time()-start_time))
                print(f"From Raspberry pi 4 (Kayak) IMU : ax: {ax}, ay: {ay}, az: {az},gx: {gx}, gy: {gy}, gz: {gz}, Roll: {roll}, Pitch: {pitch}, Yaw: {yaw} ")
                print(f"From Raspberry pi 4 (Kayak) GPS : clat: {clat}, clon: {clon}, dist_travl: {dist_travl}, total_dist: {total_dist} ")
                print(f"From Esp32 Left (Paddle) : x:  {Paddle_Left} ")
                print(f"From Esp32 Right (Paddle) : x: {Paddle_right}" )
                print(f"From Raspberry pi 4 (footrest) : Left, Right :  , {footrest_left} N, {footrest_right} N  ")    
                print("\n")                

t1 = threading.Thread(target = MQTT1)
t2 = threading.Thread(target = MQTT2)
t3 = threading.Thread(target = MQTT3)
t4 = threading.Thread(target = MQTT4)
t5 = threading.Thread(target = MQTT5)
t6 = threading.Thread(target = recorder)
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()
'''client1.connect(MQTT_SERVER, 1883, 60)
client1.loop_start()

client2.connect(MQTT_SERVER, 1883, 60)
client2.loop_start()

client3.connect(MQTT_SERVER, 1883, 60)
client3.loop_start()

client4.connect(MQTT_SERVER, 1883, 60)
client4.loop_start()'''


