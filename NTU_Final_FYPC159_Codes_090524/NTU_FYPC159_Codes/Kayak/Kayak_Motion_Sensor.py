import serial
import math
from ublox_gps import UbloxGps
import time
from time import sleep, strftime
import paho.mqtt.publish as publish
import sys
import threading

import MPU6050AGT_Working_mergeV2 

port = serial.Serial('/dev/serial0', baudrate=38400, timeout=1)
gps = UbloxGps(port)
c_lat = 0.0
c_lon = 0.0
p_lat = 0.0
p_lon = 0.0
Distancebtwn2 = 0.00
dist_all = 150.00
t_dist2 = 0.000
ax=ay=az=gx=gy=gz=roll=pitch=yaw=0.0

MQTT_SERVER= "192.168.1.1"
MQTT_PORT = 1883
MQTT_PATH1 = "boat_IMU"
MQTT_PATH2 = "boat_GPS"
counter = 0.0 

def IMUR():

    global ax, ay, az, gx, gy, gz, roll, pitch, yaw ,counter
    ax, ay, az, gx, gy, gz, roll, pitch, yaw = MPU6050AGT_Working_mergeV2.Get_RPW()    


def MQTT1():
    global ax, ay, az, gx, gy, gz, roll, pitch, yaw 
    while True: 
        message = f"{ax}, {ay},{az},{gx},{gy},{gz},{roll},{pitch},{yaw}"
        publish.single(MQTT_PATH1 , message , hostname = MQTT_SERVER, port = MQTT_PORT)


def haversine(plat, plon, clat, clon):
    E_radius = 6378 * 1000 * 100
    plat_rad = math.radians(plat)
    plon_rad = math.radians(plon)
    clat_rad = math.radians(clat)
    clon_rad = math.radians(clon)
    dlat = clat_rad  - plat_rad
    dlon = clon_rad - plon_rad
    hvs = math.sin(dlat * 0.5)*math.sin(dlat * 0.5) +math.sin(dlon * 0.5)*math.sin(dlon* 0.5)*math.cos(plat_rad) *math.cos(clat_rad);
    haversine_dist = math.asin(math.sqrt(hvs))*E_radius*2.0
    return haversine_dist    
    '''
    #Eculidean, is not as good as i've imagined 
    E_radius = 6378 * (1000) * (100)
    plat_rad = math.radians(plat)
    plon_rad = math.radians(plon)
    clat_rad = math.radians(clat)
    clon_rad = math.radians(clon)
    x1 = E_radius * math.sin(plat_rad) * math.cos(plon_rad)
    y1 = E_radius * math.cos(plat_rad) * math.sin(plon_rad)
    x2 = E_radius * math.sin(clat_rad) * math.cos(clon_rad)
    y2 = E_radius * math.cos(clat_rad) * math.sin(clon_rad)
    distanceEcu = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distanceEcu'''

def GPSR():
    global c_lat, c_lon , p_lat, p_lon, t_dist2 , Distancebtwn2 , counter
    while True:
        try:
            print("Listening for UBX Messages")

            geo = gps.geo_coords()
            #print("Longitude: ", geo.lon)
            #print("Latitude: ", geo.lat)
            #print("Heading of Motion: ", geo.headMot)
            #print("Total Distance : ", t_dist2)
            if geo.lat != 0 and geo.lon != 0:
                if p_lat is not None and p_lon is not None:
                    c_lat = geo.lat
                    c_lon = geo.lon
                    Distancebtwn2 = haversine(p_lat, p_lon, c_lat, c_lon)

                    if Distancebtwn2 > dist_all:
                        p_lat = c_lat
                        p_lon = c_lon
                        t_dist2 += Distancebtwn2

                else:
                    p_lat = geo.lat
                    p_lon = geo.lon
        except (ValueError, IOError) as err:
            print(err)
            sleep(1)  # Sleep for a while before retrying

        except Exception as e:
            print("An unexpected error occurred:", str(e))
            sleep(1)  # Sleep for a while before retrying

def MQTT2():
        global p_lat, p_lon ,c_lat ,c_lon, Distancebtwn2 , t_dist2
        while True:
            #print("GPS running")
            message = f"{p_lat},{p_lon},{c_lat},{c_lon},{Distancebtwn2} , {t_dist2}"
            publish.single(MQTT_PATH2 , message , hostname = MQTT_SERVER, port = MQTT_PORT)

def IMU_GPS_R():
    global c_lat, c_lon , p_lat, p_lon, t_dist2 , Distancebtwn2 , counter
    global ax, ay, az, gx, gy, gz, roll, pitch, yaw ,counter
    with open("/home/ssi/230224_gps_Near_River_Test.csv", "a") as log:
        start_time = time.time()
        while True: 
                ax, ay, az, gx, gy, gz, roll, pitch, yaw = MPU6050AGT_Working_mergeV2.Get_RPW()
                log.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15}\n".format(
                            strftime("%Y-%m-%d %H:%M:%S"),
                            str(ax), str(ay),
                            str(az), str(gx),
                            str(gy), str(gz),
                            str(roll),
                            str(pitch), str(yaw),                            
                            str(p_lat), str(p_lon),
                            str(c_lat), str(c_lon),
                            str(Distancebtwn2), str(t_dist2)))
                print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw} , Lat : {c_lat} , Lon : {c_lat} , TDis : {t_dist2}")
                counter = counter +1.0
                print(counter / (time.time()-start_time))


t1 = threading.Thread(target = IMUR)
t2 = threading.Thread(target = GPSR) 
t3 = threading.Thread(target = IMU_GPS_R)
t4 = threading.Thread(target = MQTT1)
t5 = threading.Thread(target = MQTT2)
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t1.join()
t2.join()
t3.join()
t4.join()
t5.join()