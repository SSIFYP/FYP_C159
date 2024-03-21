import MPU6050AGT_Working_merge 
from time import sleep, strftime, time
import time
import paho.mqtt.publish as publish
MPU6050AGT_Working_merge.calibration()
import threading
ax=ay=az=gx=gy=gz=roll=pitch=yaw=0.0
MQTT_SERVER= "192.168.1.1"
MQTT_PORT = 1883
MQTT_PATH = "boat_IMU"
counter = 0.0
def IMUR():

    global ax, ay, az, gx, gy, gz, roll, pitch, yaw ,counter
    with open("/home/ssi/230224_gps_Near_River_Test.csv", "a") as log:
        start_time = time.time()
        while True: 
                ax, ay, az, gx, gy, gz, roll, pitch, yaw = MPU6050AGT_Working_merge.Get_RPW()
                log.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(
                            strftime("%Y-%m-%d %H:%M:%S"),
                            str(ax), str(ay),
                            str(az), str(gx),
                            str(gy), str(gz),
                            str(roll),
                            str(pitch), str(yaw)))
                print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")
                counter = counter +1.0
                print(counter / (time.time()-start_time))

def MQTT():
    global ax, ay, az, gx, gy, gz, roll, pitch, yaw 
    while True: 
        message = f"{ax}, {ay},{az},{gx},{gy},{gz},{roll},{pitch},{yaw}"
        publish.single(MQTT_PATH , message , hostname = MQTT_SERVER, port = MQTT_PORT)

t1 = threading.Thread(target = IMUR)
t2 = threading.Thread(target = MQTT)
t1.start()
t2.start()
t1.join()
t2.join()
