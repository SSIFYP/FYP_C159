import time
import math 
from time import sleep
import mpu6050
from mpu6050 import mpu6050

sensor  = mpu6050(0x68)  




ax=0
ay=0
az=0
gx=0
gy=0
gz=0

cax=0
cay=0
caz=0
cgx=0
cgy=0
cgz=0


ax_max = 0
ay_max = 0
az_max = 9.81
ax_min = 0
ay_min = 0
az_min = 9.81

gx_max =0
gy_max =0
gz_max =0
gx_min =0
gy_min =0
gz_min =0

ax_OS =0
ay_OS = 0
az_OS = 0
gx_OS =0
gy_OS=0
gz_OS=0


OSCTimes = 500
yaw_deg2 =0
i = 0
q = [1.0, 0.0, 0.0, 0.0]  # Quaternion
Kp = 20.0  # Proportional feedback gain
Ki = 0.0  # Integral feedback gain

# Set the accelerometer range to +16g
sensor.set_accel_range(sensor.ACCEL_RANGE_16G)

# Set the gyroscope range to 2000 dps
sensor.set_gyro_range(sensor.GYRO_RANGE_2000DEG)

def calibration ():
        global x, ay, az, gx, gy, gz
        global cax, cay, caz, cgx, cgy, cgz
        global ax_max, ay_max, az_max, ax_min, ay_min, az_min
        global gx_max, gy_max, gz_max, gx_min, gy_min, gz_min
        global ax_OS, ay_OS, az_OS, gx_OS, gy_OS, gz_OS
        global OSCTimes, yaw_deg2
        for i in range (1, OSCTimes +1) :
                print(f"Off Set Calibrating count :{i}")
                if i < 100:
                        accel_data = sensor.get_accel_data( )
                        gyro_data = sensor.get_gyro_data()
                else :
                        accel_data = sensor.get_accel_data()
                        gyro_data = sensor.get_gyro_data()
                
                        ax_OS += accel_data['x']
                        ay_OS += accel_data['y']
                        az_OS += accel_data['z']
                        gx_OS += gyro_data['x']
                        gy_OS += gyro_data['y']
                        gz_OS += gyro_data['z']


        ax_OS =ax_OS / (OSCTimes - 100)
        ay_OS = ay_OS / (OSCTimes - 100)
        az_OS = az_OS /(OSCTimes - 100) 
        gx_OS =gx_OS /(OSCTimes - 100) 
        gy_OS=gy_OS/(OSCTimes - 100) 
        gz_OS=gz_OS /(OSCTimes - 100)


        ax_max = 0
        ay_max = 0
        az_max = 9.81
        ax_min = 0
        ay_min = 0
        az_min = 9.81

        gx_max =0
        gy_max =0
        gz_max =0
        gx_min =0
        gy_min =0
        gz_min =0

        start_time = time.time()
        # Run the loop for 5 seconds
        while time.time() - start_time < 5:
                print("Calibrating Filter")
                '''while time.time() - start_time < 1:
                        accel_data = sensor.get_accel_data()
                        gyro_data = sensor.get_gyro_data()'''
                accel_data = sensor.get_accel_data()
                gyro_data = sensor.get_gyro_data()

                cax = accel_data['x'] - ax_OS
                cay = accel_data['y'] - ay_OS
                caz = accel_data['z'] - az_OS + 9.81
                cgx = gyro_data['x'] - gx_OS
                cgy = gyro_data['y'] - gy_OS
                cgz = gyro_data['z'] - gz_OS

                if ax_max < cax:
                        ax_max = cax
                if ax_min > cax:
                        ax_min = cax

                if ay_max < cay:
                        ay_max = cay
                if ay_min > cay:
                        ay_min = cay

                if az_max < caz:
                        az_max = caz
                if az_min > caz:
                        az_min = caz

                if gx_max < cgx:
                        gx_max = cgx
                if gx_min > cgx:
                        gx_min = cgx

                if gy_max < cgy:
                        gy_max = cgy
                if gy_min > cgy:
                        gy_min = cgy

                if gz_max < cgz:
                        gz_max = cgz
                if gz_min > cgz:
                        gz_min = cgz
        print("Offeset : ")       
        print ("ax :", ax_OS)
        print ("ay :",ay_OS)
        print ("az :",az_OS)
        print ("gx :",gx_OS)
        print ("gy :",gy_OS)
        print ("gz :",gz_OS)

        print ("min ")
        print(ax_min)
        print(ay_min)
        print(az_min)
        print(gx_min)
        print(gy_min)
        print(gz_min)

        print("Max")
        print(ax_max)
        print(ay_max)
        print(az_max)
        print(gx_max)
        print(gy_max)
        print(gz_max)


        sleep(3)

def Mahony_update(ax, ay, az, gx, gy, gz, deltat):
    global q, Kp, Ki

    recipNorm = 0.0
    vx, vy, vz = 0.0, 0.0, 0.0
    ex, ey, ez = 0.0, 0.0, 0.0
    ix, iy, iz = 0.0, 0.0, 0.0

    # Compute feedback only if accelerometer measurement is valid (avoids NaN in accelerometer normalization)
    tmp = ax * ax + ay * ay + az * az
    if tmp > 0.0:
        # Normalize accelerometer
        recipNorm = 1.0 / math.sqrt(tmp)
        ax *= recipNorm
        ay *= recipNorm
        az *= recipNorm

        # Estimated direction of gravity in the body frame
        vx = q[1] * q[3] - q[0] * q[2]
        vy = q[0] * q[1] + q[2] * q[3]
        vz = q[0] * q[0] - 0.5 + q[3] * q[3]

        # Error is cross product between estimated and measured direction of gravity in body frame
        ex = (ay * vz - az * vy)
        ey = (az * vx - ax * vz)
        ez = (ax * vy - ay * vx)

        # Compute and apply integral feedback to gyro term
        if Ki > 0.0:
            ix += Ki * ex * deltat
            iy += Ki * ey * deltat
            iz += Ki * ez * deltat
            gx += ix
            gy += iy
            gz += iz
        else:
                ix =0
                iy =0
                iz =0

        # Apply proportional feedback to gyro term
        gx += Kp * ex
        gy += Kp * ey
        gz += Kp * ez

    # Integrate rate of change of quaternion
    deltat = 0.5 * deltat
    gx *= deltat
    gy *= deltat
    gz *= deltat
    qa, qb, qc = q[0], q[1], q[2]
    q[0] += (-qb * gx - qc * gy - q[3] * gz)
    q[1] += (qa * gx + qc * gz - q[3] * gy)
    q[2] += (qa * gy - qb * gz + q[3] * gx)
    q[3] += (qa * gz + qb * gy - qc * gx)

    # Renormalize quaternion
    recipNorm = 1.0 / math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
    q[0] *= recipNorm
    q[1] *= recipNorm
    q[2] *= recipNorm
    q[3] *= recipNorm

# Main setup




def RPW():
        last = (time.time())
        while True:


                now = (time.time() )

                deltat = now - last


                accel_data = sensor.get_accel_data()
                gyro_data = sensor.get_gyro_data()
                cax = accel_data['x'] - ax_OS
                cay = accel_data['y'] - ay_OS
                caz = accel_data['z'] - az_OS + 9.81
                cgx = gyro_data['x'] - gx_OS
                cgy = gyro_data['y'] - gy_OS
                cgz = gyro_data['z'] - gz_OS

                if cax > ax_max or cax < ax_min:
                        ax = cax
                else:
                        ax = 0

                if cay > ay_max or cay < ay_min:
                        ay = cay
                else:
                        ay = 0       

                if caz> az_max or caz < az_min:
                        az = caz
                else:
                        az = 9.81

                if cgx > gx_max or cgx < gx_min:
                        gx = cgx 
                else:
                        gx = 0 

                if cgy > gy_max or cgy < gy_min:
                        gy = cgy 
                else:
                        gy = 0   

                if cgz > gz_max or cgz< gz_min:
                        gz = cgz 
                else:
                        gz = 0   
                '''ax = cax
                ay = cay
                az = caz
                gx = cgx
                gy = cgy
                gz = cgz'''

                print(f"Accelerometer X: {ax}")
                print(f"Accelerometer y: {ay}")
                print(f"Accelerometer z: {az}")

                print(f"Gyroscope x: {gx}")
                print(f"Gyroscope y: {gy}")
                print(f"Gyroscope z: {gz}")
                last = now
                Mahony_update(ax, ay, az, gx * math.pi/180, gy * math.pi/180, gz * math.pi/180, deltat)
                roll = math.atan2((q[0] * q[1] + q[2] * q[3]), 0.5 - (q[1] * q[1] + q[2] * q[2]))
                pitch = math.asin(2.0 * (q[0] * q[2] - q[3] * q[1]))
                yaw = math.atan2((q[1] * q[2] + q[0] * q[3]), 0.5- (q[2] * q[2] + q[3] * q[3]))
                '''yaw = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])'''
                roll_deg = roll * 180.0 / math.pi
                pitch_deg = pitch * 180.0 / math.pi
                yaw_deg = yaw * 180.0 / math.pi
                '''yaw_deg2 += gz'''
                if yaw < 0 :
                        yaw += 360
                # Print Euler angles
                print("Roll: {:.2f}°, Pitch: {:.2f}°, Yaw: {:.2f}°".format(roll_deg, pitch_deg, yaw_deg))


def RPW_initial_Time():
        last = (time.time())
        
def Get_RPW():
                global x, ay, az, gx, gy, gz
                global cax, cay, caz, cgx, cgy, cgz
                global ax_max, ay_max, az_max, ax_min, ay_min, az_min
                global gx_max, gy_max, gz_max, gx_min, gy_min, gz_min
                global ax_OS, ay_OS, az_OS, gx_OS, gy_OS, gz_OS
                global OSCTimes, yaw_deg2
                global i , last
                if i <= 0:
                        last = (time.time())
                        i=1



                now = (time.time() )

                deltat = now - last


                accel_data = sensor.get_accel_data()
                gyro_data = sensor.get_gyro_data()
                cax = accel_data['x'] - ax_OS
                cay = accel_data['y'] - ay_OS
                caz = accel_data['z'] - az_OS + 9.81
                cgx = gyro_data['x'] - gx_OS
                cgy = gyro_data['y'] - gy_OS
                cgz = gyro_data['z'] - gz_OS

                if cax > ax_max or cax < ax_min:
                        ax = cax
                else:
                        ax = 0

                if cay > ay_max or cay < ay_min:
                        ay = cay
                else:
                        ay = 0       

                if caz> az_max or caz < az_min:
                        az = caz
                else:
                        az = 9.81

                if cgx > gx_max or cgx < gx_min:
                        gx = cgx 
                else:
                        gx = 0 

                if cgy > gy_max or cgy < gy_min:
                        gy = cgy 
                else:
                        gy = 0   

                if cgz > gz_max or cgz< gz_min:
                        gz = cgz 
                else:
                        gz = 0   
                ax = cax
                ay = cay
                az = caz
                gx = cgx
                gy = cgy
                gz = cgz

                '''print(f"Accelerometer X: {ax}")
                print(f"Accelerometer y: {ay}")
                print(f"Accelerometer z: {az}")

                print(f"Gyroscope x: {gx}")
                print(f"Gyroscope y: {gy}")
                print(f"Gyroscope z: {gz}")'''
                last = now
                Mahony_update(ax, ay, az, gx * math.pi/180, gy * math.pi/180, gz * math.pi/180, deltat)
                roll = math.atan2((q[0] * q[1] + q[2] * q[3]), 0.5 - (q[1] * q[1] + q[2] * q[2]))
                pitch = math.asin(2.0 * (q[0] * q[2] - q[3] * q[1]))
                yaw = math.atan2((q[1] * q[2] + q[0] * q[3]), 0.5- (q[2] * q[2] + q[3] * q[3]))
                '''yaw = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])'''
                roll_deg = roll * 180.0 / math.pi
                pitch_deg = pitch * 180.0 / math.pi
                yaw_deg = yaw * 180.0 / math.pi
                '''yaw_deg2 += gz'''
                if yaw < 0 :
                        yaw += 360
                # Print Euler angles
                #print("Roll: {:.2f}°, Pitch: {:.2f}°, Yaw: {:.2f}°".format(roll_deg, pitch_deg, yaw_deg))  
                return ax, ay, az, gx, gy, gz, roll_deg, pitch_deg, yaw_deg              




