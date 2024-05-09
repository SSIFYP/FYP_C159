======================================V1.1====================================================================================================================
Old version*
*kayak motion sensor system*
*For IMU* 
1) Standalone IMU with Auto calibration , Get output data, local recording, MQTT publishing 
2) IMU calculation library header file

*For GPS* 
3) Standalone GPS with Get output data, local recording, MQTT publishing


*New Version*
*For IMU*
*Quality of life improvement* : Added a separate IMU calibration file that performs calibration only and store inside a text file, the main IMU file will be changed to reading calibration data form the text file and perform the usual performance  

1) Standalone IMU auto calibration file, the calibration data will be stored in a txt file inside the repository of Raspberry pi 4 
2) Standalone IMU with *reading calibration data from txt file*, Get output data, local recording, MQTT publishing 
3) IMU calculation library header file

*For GPS*  (NO changes) 
4) Standalone GPS with Get output data, local recording, MQTT publishing

* Added a new file 5) that performs both 2) and 4) 

*Visual Bug fix for PYQT5(Dummy variable) and PYQT5(MQTT)* 
* Fix a visual error for the line graph where the max variables are not reset to 0 after pressing the reset all button.

======================================V1.0====================================================================================================================

This GitHub consists of the codes for my Nanyang Technological University MAE's final project codes FYPC159 Academic year 23/24 onto GitHub. This project is in collaboration with Singapore Sports Institute(SSI) for the project titled "DEVELOPMENT OF A LIVE FEEDBACK SYSTEM FOR KAYAK BOAT MOVEMENT" 
Due to the size of the codes, I've uploaded it here for easier access and reference. 


The code here consists of the following, the codes are to run on different devices 

PYQT5V2_MQTT_Record V3.py  ==> PC or any communication device that can run on the version Python 3.9.2.

Footrest_MQTT_pub.py === > This code is used to run on the re-adapted footrest system version from SSI 

left_Paddle_publisher.ino === > This code is used to run on the left side of the re-adapted paddle  system version from SSI 

right_paddle_publisher.ino === > This code is used to run on the right side of the re-adapted paddle  system version from SSI 

Kayak_IMU_PublisherV2.py=== > This code is used to run on the kayak system from SSI 

Kayak_GPS_PublisherV2.py === > This code is used to run on the kayak system from SSI 

Extra : 
PYQT5V3.py === > This code is used to represent the kayaking parameters using visuals, this code runs with some dummy variables to simulate the visuals. Does not require anything other than PYQT5 source code and Python 3.9.2.

Sub_Test.py === > This code is used to subscribe the information from MQTT using threading, this code does not consist of the PYQT5 GUI. 


MPU6050AGT_Working_merge.py ===> This code consist of functions of IMU 
