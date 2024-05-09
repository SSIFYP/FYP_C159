#=================================PYQT5========================================= Start set up 
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout, QLabel , QInputDialog 
from PyQt5.QtGui import QIcon , QPainter, QColor , QPen ,  QTransform , QPolygon, QBrush , QPixmap  , QFont
from PyQt5.QtCore import pyqtSlot , QTimer , Qt ,QPoint
from math import cos, sin, radians
import random
#=================================PYQT5========================================= End Set up


#=================================MQTT=========================================Start Set up 
import paho.mqtt.client as mqtt
from time import sleep, strftime, time
import threading
import time

#IP address of the broker , publisher names 

MQTT_SERVER = "192.168.1.1"
MQTT_PATH1 = "boat_IMU"
MQTT_PATH2 = "boat_GPS"
MQTT_PATH3 = "esp32_left"
MQTT_PATH4 = "esp32_right"
MQTT_PATH5 = "footrest"

#IMU Variables
ax_MQTT= 0.0
ay_MQTT=0.0
az_MQTT=0.0 
gx_MQTT=0.0 
gy_MQTT=0.0 
gz_MQTT=0.0 
roll_MQTT=0.0 
pitch_MQTT=0.0 
yaw_MQTT =0.0

#GPS variables plat = previous latitude , clat = current latitude , dista_travel = distance between prev and current 
plat_MQTT=0.0 
plon_MQTT=0.0 
clat_MQTT=0.0 
clon_MQTT=0.0 
dist_travl_MQTT=0.0  
total_dist_MQTT =0.0

#Left and right forces from paddle 
Paddle_Left_MQTT=0
Paddle_right_MQTT=0

#Left and right forces from footrest
footrest_left_MQTT=0.0 
footrest_right_MQTT = 0.0

#Others
counter_MQTT = 0.0
start_time_MQTT = time.time()
adjust_delay_MQTT = 60.0
#=================================MQTT========================================= End Set up


#=================================PYQT5========================================= Start up 
#Resolution works well in a 16:9 ratio , with minimum size of 
size =100
Resolution_Width = 16*size
Resolution_Height = 9*size
#Resolution_Width = 1920 #Force overwrite 
#Resolution_Height = 1080

#Variables for paddle
Scale_multiplier1 = 180
Scale_multiplier2 = 180

#Variables for footrest
FR_Left_Multiplier = 3
FR_Right_Multiplier = 3
max_fr_x = 0
max_fr_y = 0
min_fr_x = 0
min_fr_y = 0

#Kayak_Oreintation variables
Roll_Angle = 0 
Yaw_Angle = 0
Roll_Arrow_Threshold = 10 


#Line graphs variables
max_value1 =0
min_value1 =0
max_value2 =0
min_value2 = 0
maxdata_speed_Dist_graph= 1000
actual_max1 =0 
actual_min1=0  
actual_max2 =0 
actual_min2=0 


# variables and functions for the Left arrow of dashboard gauge 
rarrow11 = 10
rarrow21  = 0 
rarrow31 = 20 
def Arrowrotation1():
    global rarrow21 , rarrow31 , rarrow11

    rarrow11 = Paddle_Left_MQTT
    if rarrow11 > rarrow21:
        rarrow21 = rarrow11

    return rarrow11 , rarrow21 , rarrow31

# variables and functions for the Right arrow of dashboard gauge 
rarrow12 = 10
rarrow22  = 0 
rarrow32 = 20 
def Arrowrotation2():
    global  rarrow22 , rarrow32 , rarrow12
 
    rarrow12 = Paddle_right_MQTT
    if rarrow12 > rarrow22:
        rarrow22 = rarrow12

    return rarrow12 , rarrow22 , rarrow32

# variables and functions for footrest system
Left = 10
Right = 10
def FootrestHeight():
    global Left , Right

    Left = footrest_left_MQTT
    Right = footrest_right_MQTT

    return Left , Right


# variables and functions for kayak oreintation 
roll_test = 45.0
yaw_test = -90.0

def Kayak_Angles():
    global roll_test,yaw_test

    roll_test = roll_MQTT
    yaw_test = yaw_MQTT

    return roll_test , yaw_test


#variables and functions for line grpahs 
holder_array1= [random.randint(-10, 10)  for _ in range(maxdata_speed_Dist_graph+1)] 
holder_array2= [random.randint(0, 10)  for _ in range(maxdata_speed_Dist_graph+1)] 
speed = 10
distance = 10
total_distance = 0
def speed_dist():
    global maxdata_speed_Dist_graph , speed, distance  , total_distance


    speed = ay_MQTT

    distance = total_dist_MQTT

    for i in range(maxdata_speed_Dist_graph):
        holder_array1[i] = holder_array1[i+1]

    holder_array1[maxdata_speed_Dist_graph] = speed


    for i in range(maxdata_speed_Dist_graph ):
        holder_array2[i] = holder_array2[i+1]
    total_distance += distance 
    holder_array2[maxdata_speed_Dist_graph] = total_distance

    return holder_array1 , holder_array2

#Refresh timer for dashboard gauge
def delayvalue1():
    t = 10 
    return t 
#Refresh timer for footrest
def delayvalue2():
    t = 10 
    return t 
#Refresh timer for kayak oreintation
def delayvalue3():
    t = 10 
    return t 
#Refresh timer for line graphs 
def delayvalue4():
    t = 10 
    return t 

#=================================PYQT5========================================= End start up 

#=================================MQTT========================================= Start Function 
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
#Subscriber to IMU
def on_message1(client1, userdata, msg):
    global ax_MQTT,ay_MQTT,az_MQTT, gx_MQTT,gy_MQTT,gz_MQTT, roll_MQTT, pitch_MQTT, yaw_MQTT 

    message = msg.payload.decode('utf-8')

    ax_MQTT,ay_MQTT,az_MQTT ,gx_MQTT,gy_MQTT,gz_MQTT, roll_MQTT, pitch_MQTT, yaw_MQTT = message.split(',')
    ax_MQTT = float(ax_MQTT)
    ay_MQTT = float(ay_MQTT)
    az_MQTT = float(az_MQTT)
    gx_MQTT = float(gx_MQTT)
    gy_MQTT = float(gy_MQTT)
    gz_MQTT = float(gz_MQTT)
    roll_MQTT = float(roll_MQTT)
    pitch_MQTT = float(pitch_MQTT)
    yaw_MQTT = float(yaw_MQTT)
    #print(f"From Raspberry pi 4  IMU : ax: {ax_MQTT}, ay: {ay_MQTT}, az: {az_MQTT},gx: {gx_MQTT}, gy: {gy_MQTT}, gz: {gz_MQTT}, Roll: {roll_MQTT}, Pitch: {pitch_MQTT}, Yaw: {yaw_MQTT} ")
#Subscriber to GPS
def on_message2(client2, userdata, msg):
    global plat_MQTT, plon_MQTT,clat_MQTT,clon_MQTT ,dist_travl_MQTT, total_dist_MQTT 

    message = msg.payload.decode('utf-8')

    plat_MQTT,plon_MQTT, clat_MQTT, clon_MQTT, dist_travl_MQTT, total_dist_MQTT = message.split(',')
    plat_MQTT = float(plat_MQTT)
    plon_MQTT = float(plon_MQTT)    
    clat_MQTT = float(clat_MQTT)
    clon_MQTT = float(clon_MQTT)
    dist_travl_MQTT = float(dist_travl_MQTT)
    total_dist_MQTT = float(total_dist_MQTT)
    #print(f"From Raspberry pi 4  GPS : clat: {clat_MQTT}, clon: {clon_MQTT}, dist_travl: {dist_travl_MQTT}, total_dist: {total_dist_MQTT} ")
#Subscriber to Left paddle
def on_message3(client3, userdata, msg):
    global Paddle_Left_MQTT ,counter_MQTT

    message = msg.payload.decode('utf-8')

    Paddle_Left_MQTT = message
    
    Paddle_Left_MQTT = float(Paddle_Left_MQTT)

    #print(f"From Esp32 Left : x:  , {counter}, {Paddle_Left_MQTT} ")
#Subscriber to Right paddle
def on_message4(client4, userdata, msg):
    global Paddle_right_MQTT

    message = msg.payload.decode('utf-8')

    Paddle_right_MQTT = message
    
    Paddle_right_MQTT = float(Paddle_right_MQTT)

    #print(f"From Esp32 Right : x: {Paddle_right_MQTT} " )
#Subscriber to Left and right footrest
def on_message5(client5, userdata, msg):
    global footrest_left_MQTT, footrest_right_MQTT

    message = msg.payload.decode('utf-8')

    footrest_left_MQTT , footrest_right_MQTT = message.split(",")

    #print(f"From footrest  : Left, Right :  , {footrest_left_MQTT} , {footrest_right_MQTT}  ")
# Loops function for each subscriber , used for threading 
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
# Records information in excel format
def recorder():
    global counter_MQTT
    start_time = time.time()
    while True: 
        with open("C:/Users/daren/OneDrive/Desktop/Integration_090524.csv" , "a") as log: 
                time.sleep((1.0-(adjust_delay_MQTT/2800.0))/(adjust_delay_MQTT/0.5))
                #time.sleep(1)          
                log.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18}, {19} \n".format(
                strftime("%Y-%m-%d %H:%M:%S"),
                str(ax_MQTT), str(ay_MQTT), str(az_MQTT), str(gx_MQTT), str(gy_MQTT), str(gz_MQTT), str(roll_MQTT), str(pitch_MQTT), str(yaw_MQTT),
                str(plat_MQTT), str(plon_MQTT), str(clat_MQTT), str(clon_MQTT), str(dist_travl_MQTT), str(total_dist_MQTT),
                str(Paddle_Left_MQTT), str(Paddle_right_MQTT), 
                str(footrest_left_MQTT), str(footrest_right_MQTT)
                            ))   
                counter_MQTT = counter_MQTT +1 
                print(counter_MQTT / (time.time()-start_time))
                print(f"From Raspberry pi 4 (Kayak) IMU : ax: {ax_MQTT}, ay: {ay_MQTT}, az: {az_MQTT},gx: {gx_MQTT}, gy: {gy_MQTT}, gz: {gz_MQTT}, Roll: {roll_MQTT}, Pitch: {pitch_MQTT}, Yaw: {yaw_MQTT} ")
                print(f"From Raspberry pi 4 (Kayak) GPS : clat: {clat_MQTT}, clon: {clon_MQTT}, dist_travl: {dist_travl_MQTT}, total_dist: {total_dist_MQTT} ")
                print(f"From Esp32 Left (Paddle) : x:  {Paddle_Left_MQTT} ")
                print(f"From Esp32 Right (Paddle) : x: {Paddle_right_MQTT}" )
                print(f"From Raspberry pi 4 (footrest) : Left, Right :  , {footrest_left_MQTT} N, {footrest_right_MQTT} N  ")    
                print("\n")                
#=================================MQTT========================================= End Functions 

#Main window with 4 tabs 
class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'FYPC159, Kayaking paramters Viusals'
        self.left = 0
        self.top = 0
        self.width = Resolution_Width
        self.height = Resolution_Height
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        self.show()
#Class for a windows with 4 tabs     
class MyTableWidget(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tabs.resize(600,400)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Paddle")
        self.tabs.addTab(self.tab2,"Footrest")
        self.tabs.addTab(self.tab3,"Kayak")
        self.tabs.addTab(self.tab4,"Acceleration and Distances")

        #  first tab
        self.tab1.layout = QVBoxLayout(self)
        self.Dashboard_Gauge = DashboardGauge(self.tab1)
        self.tab1.layout.addWidget(self.Dashboard_Gauge)
        self.tab1.setLayout(self.tab1.layout)

        # Second Tab     
        self.tab2.layout = QVBoxLayout(self)
        self.rectangle_widget = RectangleWidget(self.tab2)
        self.tab2.layout.addWidget(self.rectangle_widget)
        self.tab2.setLayout(self.tab2.layout)        

        # Third Tab     
        self.tab3.layout = QVBoxLayout(self)
        self.Kayak_Orientation = Kayak_Orientation(self.tab3)
        self.tab3.layout.addWidget(self.Kayak_Orientation)
        self.tab3.setLayout(self.tab3.layout) 


        # Fourth Tab     
        self.tab4.layout = QVBoxLayout(self)
        self.Line_Graph = Line_Graph(self.tab4)
        self.tab4.layout.addWidget(self.Line_Graph)
        self.tab4.setLayout(self.tab4.layout) 

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        

    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())




#Dashboard for paddle 
class DashboardGauge(QWidget):
    def __init__(self, parent2):
        super().__init__()
        self.parent2 = parent2
        self.label = QLabel(self)
        self.arrow_rotate_timer = QTimer(self)
        self.arrow_rotate_timer.timeout.connect(self.arrows)
        t = delayvalue2() 
        self.arrow_rotate_timer.start(t)
        self.arrow_rotate_timer.setSingleShot(False)

        self.arrows11 = 0
        self.arrows12 = 0
        self.arrows13 = 0
        self.arrows21 = 0
        self.arrows22 = 0
        self.arrows23 = 0

        #Buttons 
        self.button1 = QPushButton(" Adjust LRed Arrow  ", self)
        self.button1.setGeometry(0.05*Resolution_Width , 0.78*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button1.clicked.connect(self.LeftRedArrow)

        self.button2 = QPushButton(" Adjust RRed Arrow  ", self)
        self.button2.setGeometry(0.17*Resolution_Width , 0.78*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button2.clicked.connect(self.RightRedArrow)

        self.button3 = QPushButton("Reset LYellow Arrow  ", self)
        self.button3.setGeometry(0.29*Resolution_Width , 0.78*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button3.clicked.connect(self.ResetYLArrow)

        self.button4 = QPushButton("Reset RYellow Arrow  ", self)
        self.button4.setGeometry(0.41*Resolution_Width , 0.78*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button4.clicked.connect(self.ResetYRArrow)
        
        self.button5 = QPushButton("Adjust Left Scale ", self)
        self.button5.setGeometry(0.53*Resolution_Width , 0.78*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button5.clicked.connect(self.AdjustLScale)

        self.button6 = QPushButton("Adjust Right Scale", self)
        self.button6.setGeometry(0.65*Resolution_Width , 0.78*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button6.clicked.connect(self.AdjustRScale)

        self.button7 = QPushButton("Reset All", self)
        self.button7.setGeometry(0.77*Resolution_Width , 0.78*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button7.clicked.connect(self.ResetAllDG)

        #Text and variable displays 
        self.label1 = QLabel(self)
        self.label1.setGeometry(0.35*Resolution_Width , 0.56*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label1.setFont(QFont('Arial',0.02*Resolution_Height )) 
        self.label2 = QLabel(self)
        self.label2.setGeometry(0.35*Resolution_Width , 0.6*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label2.setFont(QFont('Arial',0.02*Resolution_Height )) 
        self.label3 = QLabel(self)
        self.label3.setGeometry(0.35*Resolution_Width , 0.64*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label3.setFont(QFont('Arial',0.02*Resolution_Height )) 
        self.label4 = QLabel(self)
        self.label4.setGeometry(0.35*Resolution_Width , 0.68*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label4.setFont(QFont('Arial',0.02*Resolution_Height )) 
        self.labelLeft = QLabel(self)
        self.labelLeft.setGeometry(0.15*Resolution_Width , 0.49*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.labelLeft.setFont(QFont('Arial',0.02*Resolution_Height )) 
        self.labelLeft.setText("Left")
        self.labelRight = QLabel(self)
        self.labelRight.setGeometry(0.81*Resolution_Width , 0.49*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.labelRight.setFont(QFont('Arial',0.02*Resolution_Height )) 
        self.labelRight.setText("Right")

    #Refresh the variables beside the text 
    def update_text(self):
        self.label1.setText("Current Left , Right   : {:.2f}, {:.2f}".format((self.arrows11-180) * (Scale_multiplier1 / 180), (self.arrows21-180)  * (Scale_multiplier2 / 180)))  
        self.label2.setText("Max Left , Right       : {:.2f}, {:.2f}".format((self.arrows12-180) * (Scale_multiplier1 / 180), (self.arrows22-180)  * (Scale_multiplier2 / 180)))  
        self.label3.setText("Target Left , Right    : {:.2f}, {:.2f}".format((self.arrows13-180) * (Scale_multiplier1 / 180), (self.arrows23-180)  * (Scale_multiplier2 / 180)))  
        self.label4.setText("Scale Left , Right     : {:.2f}, {:.2f}".format(Scale_multiplier1, Scale_multiplier2))  
    
    #Draw shapes 
    def paintEvent(self, event):
        painter = QPainter(self)
        #Background blue 
        painter.save()
        painter.translate(0, 0)
        painter.rotate(0)
        painter.setPen(QPen(QColor(120, 120, 120), 10, Qt.SolidLine))
        painter.setBrush(QColor(200, 200, 255))
        painter.drawRect(0, 0, Resolution_Width, Resolution_Height)
        painter.restore()

        #Paddle 
        painter.save()
        painter.translate(0.1*Resolution_Width, 0.5*Resolution_Height)
        painter.setPen(QPen(QColor(0, 0, 0), 3, Qt.SolidLine))
        painter.setBrush(QColor(255, 165, 0))
        points3 = [
            QPoint(0,0),
            QPoint(0.12*Resolution_Width,0),
            QPoint(0.17*Resolution_Width,0.025*Resolution_Height),
            QPoint(0.63*Resolution_Width,0.025*Resolution_Height),
            QPoint(0.68*Resolution_Width,0),
            QPoint(0.8*Resolution_Width,0),
            QPoint(0.8*Resolution_Width,0.075*Resolution_Height),
            QPoint(0.68*Resolution_Width,0.075*Resolution_Height),
            QPoint(0.63*Resolution_Width,0.05*Resolution_Height),
            QPoint(0.17*Resolution_Width,0.05*Resolution_Height),
            QPoint(0.12*Resolution_Width,0.075*Resolution_Height),
            QPoint(0,0.075*Resolution_Height)
        ]
        poly3 = QPolygon(points3)
        painter.drawPolygon(poly3)
        painter.restore()



        #Semicircle of the 2 dashboard gauges 
        painter.setPen(QColor(0, 0, 0))
        pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)
        pen.setWidth(5)
        painter.setPen(pen)
        startAngle = -0 * 16
        spanAngle = 180 * 16  # 16 is used to represent 1 degree
        radius = 0.2*Resolution_Width
        painter.drawArc(0.05*Resolution_Width , 0.1*Resolution_Height, 2 * (radius), 2 * (radius), startAngle, spanAngle)
        painter.drawArc(0.55*Resolution_Width , 0.1*Resolution_Height, 2 * (radius), 2 * (radius), startAngle, spanAngle)
        painter.drawLine(0.05*Resolution_Width, 0.1*Resolution_Height+(radius), 0.45*Resolution_Width,  0.1*Resolution_Height+(radius))
        painter.drawLine(0.55*Resolution_Width,  0.1*Resolution_Height+(radius), 0.95*Resolution_Width,  0.1*Resolution_Height+(radius))

        # Draw tick marks for 180 degrees
        num_ticks = 90  # You can adjust the number of tick marks
        angle_increment = 180 / num_ticks
        scale = 0.01 * radius

        for i in range(num_ticks + 1):
            pen = QPen()
            pen.setWidth(1)  # You can adjust the width as needed
            painter.setPen(pen)  
            angle = -180 + i * angle_increment
            x1 = 0.25*Resolution_Width + (radius - 5) * 0.9 * cos(radians(angle))
            y1 = 0.455*Resolution_Height + (radius - 5) * 0.9 * sin(radians(angle))
            x2 = 0.25*Resolution_Width + radius * cos(radians(angle))
            y2 = 0.455*Resolution_Height + radius * sin(radians(angle))
            x21 = 0.75*Resolution_Width + (radius - 5) * 0.9 * cos(radians(angle))
            y21 = 0.455*Resolution_Height + (radius - 5) * 0.9 * sin(radians(angle))
            x22 = 0.75*Resolution_Width + radius * cos(radians(angle))
            y22 = 0.455*Resolution_Height + radius * sin(radians(angle))
            painter.drawLine(x1, y1, x2, y2)
            painter.drawLine(x21, y21, x22, y22)
            # Check if it's a 5th tick (multiples of 5)
            if i % 5 == 0:
                pen = QPen()
                pen.setWidth(3)  # You can adjust the width as needed
                painter.setPen(pen)
                x1 = 0.25*Resolution_Width + (radius - scale - 5) * 0.9 * cos(radians(angle))
                y1 = 0.455*Resolution_Height + (radius - scale - 5) * 0.9 * sin(radians(angle))
                x2 = 0.25*Resolution_Width + (radius) * cos(radians(angle))
                y2 = 0.455*Resolution_Height + (radius) * sin(radians(angle))
                x21 = 0.75*Resolution_Width + (radius - scale - 5) * 0.9 * cos(radians(angle))
                y21 = 0.455*Resolution_Height + (radius - scale - 5) * 0.9 * sin(radians(angle))
                x22 = 0.75*Resolution_Width + (radius) * cos(radians(angle))
                y22 = 0.455*Resolution_Height + (radius) * sin(radians(angle))
                painter.drawLine(x1, y1, x2, y2)
                painter.drawLine(x21, y21, x22, y22)

        arrow_length = 0.15*Resolution_Width
        center1 = QPoint(0.25 * Resolution_Width, 0.45 * Resolution_Height)
        center2 = QPoint(0.75* Resolution_Width, 0.45 * Resolution_Height)
        #arrow_center = center + QTransform().rotate(self.arrows1).map(QPoint(arrow_length, 0))
        #max_arrow_center = center + QTransform().rotate(self.arrows1).map(QPoint(arrow_length, 0))

        #Arroews for dashboard gauge 
        arrow11 = QPolygon([
            center1 + QTransform().rotate(self.arrows11).map(QPoint(0, 0)),
            center1 + QTransform().rotate(self.arrows11).map(QPoint(arrow_length, 0.03*arrow_length)),
            center1 + QTransform().rotate(self.arrows11).map(QPoint(arrow_length + 0.15*arrow_length, 0)),
            center1 + QTransform().rotate(self.arrows11).map(QPoint(arrow_length, -0.03*arrow_length))
        ])


        arrow12 = QPolygon([
            center1 + QTransform().rotate(self.arrows12).map(QPoint(0, 0)),
            center1 + QTransform().rotate(self.arrows12).map(QPoint(arrow_length, 0.03*arrow_length)),
            center1 + QTransform().rotate(self.arrows12).map(QPoint(arrow_length + 0.15*arrow_length, 0)),
            center1 + QTransform().rotate(self.arrows12).map(QPoint(arrow_length, -0.03*arrow_length))
        ])

        arrow13 = QPolygon([
            center1 + QTransform().rotate(self.arrows13).map(QPoint(0, 0)),
            center1 + QTransform().rotate(self.arrows13).map(QPoint(arrow_length, 0.03*arrow_length)),
            center1 + QTransform().rotate(self.arrows13).map(QPoint(arrow_length + 0.15*arrow_length, 0)),
            center1 + QTransform().rotate(self.arrows13).map(QPoint(arrow_length, -0.03*arrow_length))
        ])

        arrow21 = QPolygon([
            center2 + QTransform().rotate(self.arrows21).map(QPoint(0, 0)),
            center2 + QTransform().rotate(self.arrows21).map(QPoint(arrow_length, 0.03*arrow_length)),
            center2 + QTransform().rotate(self.arrows21).map(QPoint(arrow_length + 0.15*arrow_length, 0)),
            center2 + QTransform().rotate(self.arrows21).map(QPoint(arrow_length, -0.03*arrow_length))
        ])

        arrow22 = QPolygon([
            center2 + QTransform().rotate(self.arrows22).map(QPoint(0, 0)),
            center2 + QTransform().rotate(self.arrows22).map(QPoint(arrow_length, 0.03*arrow_length)),
            center2 + QTransform().rotate(self.arrows22).map(QPoint(arrow_length + 0.15*arrow_length, 0)),
            center2 + QTransform().rotate(self.arrows22).map(QPoint(arrow_length, -0.03*arrow_length))
        ])

        arrow23 = QPolygon([
            center2 + QTransform().rotate(self.arrows23).map(QPoint(0, 0)),
            center2 + QTransform().rotate(self.arrows23).map(QPoint(arrow_length, 0.03*arrow_length)),
            center2 + QTransform().rotate(self.arrows23).map(QPoint(arrow_length + 0.15*arrow_length, 0)),
            center2 + QTransform().rotate(self.arrows23).map(QPoint(arrow_length, -0.03*arrow_length))
        ])

        pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(Qt.green))
        painter.drawPolygon(arrow11)
        painter.drawPolygon(arrow21)

        pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(Qt.yellow))
        painter.drawPolygon(arrow12)
        painter.drawPolygon(arrow22)

        pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(Qt.red))
        painter.drawPolygon(arrow13)
        painter.drawPolygon(arrow23)

    #Update the arrow rotation position 
    def arrows(self):
        global Scale_multiplier1  , Scale_multiplier2
        x,y,z = Arrowrotation1() 
        self.arrows11 = 180+x* (180/Scale_multiplier1) 
        self.arrows12 = 180+y* (180/Scale_multiplier1) 
        self.arrows13 = 180+z* (180/Scale_multiplier1)
        if self.arrows11 < 180 :
            self.arrows11 = 180
        if self.arrows11 > 360 : 
            self.arrows11 = 360 
        if self.arrows12 < 180 :
            self.arrows12 = 180
        if self.arrows12 > 360 : 
            self.arrows12 = 360 
        if self.arrows13 < 180 :
            self.arrows13 = 180
        if self.arrows13 > 360 : 
            self.arrows13 = 360 
        
        x,y,z = Arrowrotation2() 
        self.arrows21 = 180+x* (180/Scale_multiplier2)
        self.arrows22 = 180+y* (180/Scale_multiplier2)
        self.arrows23 = 180+z* (180/Scale_multiplier2)     
        if self.arrows21 < 180 :
            self.arrows21 = 180
        if self.arrows21 > 360 : 
            self.arrows21 = 360 
        if self.arrows22 < 180 :
            self.arrows22 = 180
        if self.arrows22 > 360 : 
            self.arrows22 = 360 
        if self.arrows23 < 180 :
            self.arrows23 = 180
        if self.arrows23 > 360 : 
            self.arrows23 = 360  
        self.update_text()
        self.repaint()

    #The input prompts and functions form the buttons 
    def LeftRedArrow(self):
        global rarrow31 
        inputtarget, done = QInputDialog.getDouble(
            self, 'Adjust your target here ', 'Set your left target as:')
        if done:
            rarrow31 = float(inputtarget)

    def RightRedArrow(self):
        global rarrow32 
        inputtarget, done = QInputDialog.getDouble(
            self, 'Adjust your target here ', 'Set your right target as:')
        if done:
            rarrow32 = float(inputtarget)
    def ResetYLArrow(self):
        global rarrow21 
        rarrow21 = 0.0
    def ResetYRArrow(self):
        global rarrow22 
        rarrow22 = 0.0
    def AdjustLScale(self):
        global Scale_multiplier1 
        inputtarget, done = QInputDialog.getDouble(
            self, 'Adjust your Scale here ', 'Set your left scale as:')
        if done:
            Scale_multiplier1 = float(inputtarget)

    def AdjustRScale(self):
        global Scale_multiplier2 
        inputtarget, done = QInputDialog.getDouble(
            self, 'Adjust your Scale here ', 'Set your right scale as:')
        if done:
            Scale_multiplier2 = float(inputtarget)
    def ResetAllDG(self):
        global rarrow21, rarrow22 , rarrow31, rarrow32, Scale_multiplier1 , Scale_multiplier2
        rarrow21 = 0.0
        rarrow31 = 50
        rarrow22 = 0.0
        rarrow32 = 50        
        Scale_multiplier1 = 180
        Scale_multiplier2 = 180 


#2 bar graph for the footrest 
class RectangleWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.height_change_timer = QTimer(self)
        self.height_change_timer.timeout.connect(self.update_height)
        t= delayvalue1() 
        self.height_change_timer.start(t)
        self.height_change_timer.setSingleShot(False)

        #This set the initial value of the footrest as 0 , left(height change 1 is left) 
        self.height_change1 = 0
        self.height_change2 = 0

        #Buttons with functions 
        self.button1 = QPushButton(" Adjust Height Scale (left) ", self)
        self.button1.setGeometry(0.05*Resolution_Width , 0.2*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button1.clicked.connect(self.Height_Scale_Left)

        self.button2 = QPushButton(" Adjust Height Scale (Right)", self)
        self.button2.setGeometry(0.05*Resolution_Width , 0.3*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button2.clicked.connect(self.Height_Scale_Right)    

        self.button3 = QPushButton(" Adjust Height Scale (Both)", self)
        self.button3.setGeometry(0.05*Resolution_Width , 0.4*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button3.clicked.connect(self.Height_Scale_Both)

        self.button7 = QPushButton("Reset Max/Min", self)
        self.button7.setGeometry(0.05*Resolution_Width , 0.5*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button7.clicked.connect(self.Reset_Min_Max)
        #Text and variables 
        self.label1 = QLabel(self)
        self.label1.setGeometry(0.35*Resolution_Width , 0.03*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label1.setFont(QFont('Arial',0.015*Resolution_Height )) 

        self.label2 = QLabel(self)
        self.label2.setGeometry(0.35*Resolution_Width , 0.07*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label2.setFont(QFont('Arial',0.015*Resolution_Height )) 

        self.label3 = QLabel(self)
        self.label3.setGeometry(0.35*Resolution_Width , 0.11*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label3.setFont(QFont('Arial',0.015*Resolution_Height )) 
    #Refresh text and variable 
    def update_text(self):
        self.label1.setText("Current Left , Right   : {:.2f}, {:.2f}".format(self.height_change1 / FR_Left_Multiplier, self.height_change2 / FR_Right_Multiplier)) 
        self.label2.setText("Max Left , Right       : {:.2f}, {:.2f}".format(max_fr_x, max_fr_y)) 
        self.label3.setText("Max Left , Right       : {:.2f}, {:.2f}".format(min_fr_x, min_fr_y))  
    #Draw the bar graphs
    def paintEvent(self, event):
        painter = QPainter(self)
        #Fake sea or blue background 
        painter.save()
        painter.translate(0, 0)
        painter.rotate(0)
        painter.setPen(QPen(QColor(120, 120, 120), 10, Qt.SolidLine))
        painter.setBrush(QColor(200, 200, 255))
        painter.drawRect(0, 0, Resolution_Width, Resolution_Height)
        painter.restore()
        #Draw rough left footrest shape 
        painter.save()
        painter.translate(0.2 * Resolution_Width, 0.2 * Resolution_Height)
        painter.rotate(0)
        painter.setPen(QPen(QColor(120, 120, 120), 10, Qt.SolidLine))
        painter.setBrush(QColor(200, 200, 200))
        painter.drawRect(0, 0, 0.3*Resolution_Width, 0.6*Resolution_Height)
        painter.restore()
        #Draw rough right footrest shape 
        painter.save()
        painter.translate(0.5 * Resolution_Width, 0.2 * Resolution_Height)
        painter.rotate(0)
        painter.setPen(QPen(QColor(120, 120, 120), 10, Qt.SolidLine))
        painter.setBrush(QColor(200, 200, 200))
        painter.drawRect(0, 0, 0.3*Resolution_Width, 0.6*Resolution_Height)
        painter.restore()
        #Bar graphs inside the footrest 
        painter.translate(0, 0)        
        painter.setPen(QColor(200, 200, 200))
        if(self.height_change1 >= 0.0 ):
            painter.setBrush(QColor(120, 120, 255))
        else:
            painter.setBrush(QColor(120, 120, 150))
        painter.drawRect(0.25 * Resolution_Width, 0.5 * Resolution_Height, 0.2 * Resolution_Width, self.height_change1)
        painter.setPen(QColor(200, 200, 200))
        if(self.height_change2 >= 0.0 ):
            painter.setBrush(QColor(120, 120, 255))
        else:
            painter.setBrush(QColor(120, 120, 150))
        painter.drawRect(0.55 * Resolution_Width, 0.5 * Resolution_Height, 0.2 * Resolution_Width, self.height_change2)
    #Buttons function 
    def Height_Scale_Left(self):
        global FR_Left_Multiplier 
        inputtarget, done = QInputDialog.getDouble(self, 'Adjust your scale here ', 'Set your left scale as:')
        if done:
            FR_Left_Multiplier = float(inputtarget)

    def Height_Scale_Right(self):
        global FR_Right_Multiplier 
        inputtarget, done = QInputDialog.getDouble(self, 'Adjust your scale here ', 'Set your Right scale as:')
        if done:
            FR_Right_Multiplier = float(inputtarget)
    def Height_Scale_Both(self):  
        global FR_Left_Multiplier, FR_Right_Multiplier 
        inputtarget, done = QInputDialog.getDouble(self, 'Adjust your scale here ', 'Set your Both scale as:')
        if done:
            FR_Right_Multiplier = float(inputtarget)
            FR_Left_Multiplier= float(inputtarget)
    def Reset_Min_Max(self):
        global max_fr_x , max_fr_y , min_fr_x , min_fr_y
        max_fr_x =0
        max_fr_y =0
        min_fr_x =0
        min_fr_y =0
    #Update height of bargraphs 
    def update_height(self):
        global max_fr_x , max_fr_y , min_fr_x , min_fr_y
        x,y = FootrestHeight()
        self.height_change1 =x * FR_Left_Multiplier
        self.height_change2 =y * FR_Right_Multiplier
        if max_fr_x < x :
            max_fr_x = x 
        if max_fr_y < y :
            max_fr_y = y 
        if min_fr_x > x :
            min_fr_x = x 
        if min_fr_y > y :
            min_fr_y = y 
        self.update_text()
        self.repaint()


#kayak roll and yaw 
class Kayak_Orientation(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.kayak_timer = QTimer(self)
        self.kayak_timer.timeout.connect(self.kayak_change)
        t= delayvalue3() 
        self.kayak_timer.start(t)
        self.kayak_timer.setSingleShot(False)
        self.roll_angle = 0
        self.yaw_angle = 0

        #text and variable 
        self.label1 = QLabel(self)
        self.label1.setGeometry(0.21*Resolution_Width , 0.5*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label1.setFont(QFont('Arial',0.015*Resolution_Height )) 

        self.label2 = QLabel(self)
        self.label2.setGeometry(0.21*Resolution_Width , 0.54*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label2.setFont(QFont('Arial',0.015*Resolution_Height )) 

        #Buttons for adjusting the arrow display condition
        self.button1 = QPushButton(" Adjust Height Scale (left) ", self)
        self.button1.setGeometry(0.05*Resolution_Width , 0.1*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button1.clicked.connect(self.Arrow_Appearance)
        self.button1.setStyleSheet("background-color:  rgb(200, 200, 255);")
    #Update variable from the text     
    def update_text(self):
        self.label1.setText("Roll: {:.2f}".format(self.roll_angle))
        self.label2.setText("Yaw: {:.2f}".format(self.yaw_angle))
    #Draw the kayak from front and top view 
    def paintEvent(self, event):
        global roll , Roll_Arrow_Threshold

        startAngle = 180 * 16
        spanAngle = 180* 16  # 16 is used to represent 1 degree
        radius = 0.2*Resolution_Width
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        #Fake sea
        painter.save()
        painter.translate(0.25*Resolution_Width, 0.5*Resolution_Height)
        painter.rotate(0)
        painter.setPen(QPen(QColor(0, 10, 120), 10, Qt.SolidLine))
        painter.setBrush(QColor(200, 200, 255))
        painter.drawRect(-0.25*Resolution_Width, 0.5*Resolution_Height, 0.5*Resolution_Width, -0.5*Resolution_Height)
        painter.restore()
        
        #ROll of the boat
        painter.save()
        painter.translate(0.25*Resolution_Width, 0.5*Resolution_Height)
        painter.rotate(self.roll_angle)#self.roll_angle)
        painter.setPen(QPen(QColor(0, 0, 0), 10, Qt.SolidLine))
        painter.setBrush(Qt.black)
        painter.drawArc(-0.0625*Resolution_Width, -0.25*Resolution_Height, 0.125*Resolution_Width, 0.25*Resolution_Height, startAngle, spanAngle)
        painter.drawLine(-0.05*Resolution_Width, -0.1*Resolution_Height , 0.05*Resolution_Width, -0.1*Resolution_Height)
        painter.restore()
        startAngle_arrow = 0
        spanAngle_arrow = 60*16

        if roll < -Roll_Arrow_Threshold:
            painter.save()
            painter.setBrush(QBrush(QColor(20, 0, 100), Qt.SolidPattern))
            painter.translate(0.28*Resolution_Width, 0.3*Resolution_Height)
            points = [
                QPoint(0,0),
                QPoint(-0.03*Resolution_Width,-0.04*Resolution_Height),
                QPoint(0,-0.08*Resolution_Height),
                QPoint(0,-0.06*Resolution_Height),
                QPoint(0.030*Resolution_Width,-0.06*Resolution_Height),
                QPoint(0.045*Resolution_Width,-0.04*Resolution_Height),
                QPoint(0.045*Resolution_Width, 0.04*Resolution_Height),
                QPoint(0.02*Resolution_Width, 0.04*Resolution_Height),
                QPoint(0.02*Resolution_Width,-0.02*Resolution_Height),
                QPoint(0,-0.02*Resolution_Height)
                ]
            poly = QPolygon(points)
            painter.drawPolygon(poly)
            painter.restore()

        if roll > Roll_Arrow_Threshold:
            painter.save()
            painter.setBrush(QBrush(QColor(20, 0, 100), Qt.SolidPattern))
            painter.translate(0.22*Resolution_Width, 0.3*Resolution_Height)
            points = [
                QPoint(0,0),
                QPoint(0.03*Resolution_Width,-0.04*Resolution_Height),
                QPoint(0,-0.08*Resolution_Height),
                QPoint(0,-0.06*Resolution_Height),
                QPoint(-0.030*Resolution_Width,-0.06*Resolution_Height),
                QPoint(-0.045*Resolution_Width,-0.04*Resolution_Height),
                QPoint(-0.045*Resolution_Width, 0.04*Resolution_Height),
                QPoint(-0.02*Resolution_Width, 0.04*Resolution_Height),
                QPoint(-0.02*Resolution_Width,-0.02*Resolution_Height),
                QPoint(0,-0.02*Resolution_Height)
                ]
            poly = QPolygon(points)
            painter.drawPolygon(poly)
            painter.restore()

        #Black line between roll and yaw
        painter.save()
        painter.setPen(QPen(Qt.black, 5))
        painter.translate(0.5*Resolution_Width, 0)
        painter.drawLine(0, 0 , 0, Resolution_Height)
        painter.restore()


        #Yaw of the boat 
        painter.save()
        painter.translate(0.5*Resolution_Width, 0)
        painter.rotate(0)
        painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        painter.setBrush(QColor(200, 200, 255))
        painter.drawRect(0, 0, 0.5*Resolution_Width, Resolution_Height)
        painter.restore()

        painter.save()
        painter.setPen(QPen(Qt.black, 5))
        painter.setBrush(QBrush(QColor(255, 165, 0)))
        painter.translate(0.75*Resolution_Width, 0.5*Resolution_Height)
        painter.rotate(self.yaw_angle)
        points = [
            QPoint(0,-0.35*Resolution_Height),
            QPoint(0.025*Resolution_Width, -0.18*Resolution_Height),
            QPoint(0.025*Resolution_Width, 0.18*Resolution_Height),
            QPoint(0, 0.35*Resolution_Height),
            QPoint(-0.025*Resolution_Width, 0.18*Resolution_Height),
            QPoint(-0.025*Resolution_Width, -0.18*Resolution_Height)
            ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)
        painter.setPen(QPen(QColor(125, 125, 125), 5))        
        painter.setBrush(QBrush(QColor(220, 220, 220)))      
        painter.drawRect(-0.015*Resolution_Width,-0.1*Resolution_Height, 0.03*Resolution_Width ,0.2*Resolution_Height )
        painter.restore()
    #button function
    def Arrow_Appearance(self):
        global Roll_Arrow_Threshold 
        inputtarget, done = QInputDialog.getDouble(self, 'Adjust your Appearance Angle here ', 'Set your Appearance Angle as:')
        if done:
            Roll_Arrow_Threshold = float(inputtarget)        

    #change the roll and yaw position 
    def kayak_change(self):
        global roll
        roll,yaw = Kayak_Angles()
        self.roll_angle =roll
        self.yaw_angle =yaw
        self.update_text()
        self.update()

#Line graphs for speed and distance 
class Line_Graph(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.line_change_timer = QTimer(self)
        self.line_change_timer.timeout.connect(self.line_Update)
        t= delayvalue4() 
        self.line_change_timer.start(t)
        self.line_change_timer.setSingleShot(False)
        #Initial data are set as 0 for the data+1 
        self.data1 =[0 for _ in range(maxdata_speed_Dist_graph+1)] 
        self.data2 =[0  for _ in range(maxdata_speed_Dist_graph+1)] 

        #text and variables 
        self.label1 = QLabel(self)
        self.label1.setGeometry(0.005*Resolution_Width , 0.025*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label1.setFont(QFont('Arial',0.012*Resolution_Height )) 

        self.label2 = QLabel(self)
        self.label2.setGeometry(0.005*Resolution_Width , 0.575*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label2.setFont(QFont('Arial',0.012*Resolution_Height )) 

        self.label3 = QLabel(self)
        self.label3.setGeometry(0.50*Resolution_Width , 0.025*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label3.setFont(QFont('Arial',0.012*Resolution_Height )) 

        self.label4 = QLabel(self)
        self.label4.setGeometry(0.53*Resolution_Width , 0.575*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label4.setFont(QFont('Arial',0.012*Resolution_Height )) 

        self.label5 = QLabel(self)
        self.label5.setGeometry(0.05*Resolution_Width , 0.7*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label5.setFont(QFont('Arial',0.015*Resolution_Height )) 

        self.label6 = QLabel(self)
        self.label6.setGeometry(0.05*Resolution_Width , 0.74*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label6.setFont(QFont('Arial',0.015*Resolution_Height )) 

        self.label7 = QLabel(self)
        self.label7.setGeometry(0.05*Resolution_Width , 0.78*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label7.setFont(QFont('Arial',0.015*Resolution_Height )) 

        self.label8 = QLabel(self)
        self.label8.setGeometry(0.8*Resolution_Width , 0.7*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label8.setFont(QFont('Arial',0.015*Resolution_Height )) 

        self.label9 = QLabel(self)
        self.label9.setGeometry(0.8*Resolution_Width , 0.74*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        self.label9.setFont(QFont('Arial',0.015*Resolution_Height )) 

        #self.label10 = QLabel(self)
        #self.label10.setGeometry(0.8*Resolution_Width , 0.78*Resolution_Height, 0.5*Resolution_Width, 0.1*Resolution_Height)
        #self.label10.setFont(QFont('Arial',0.015*Resolution_Height )) 

        #Buttons to reset max and min
        self.button7 = QPushButton("Reset Max/Min", self)
        self.button7.setGeometry(0.25*Resolution_Width , 0.75*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button7.clicked.connect(self.Reset_Min_Max_Line)
        self.button8 = QPushButton("Reset Data (Left)", self)
        self.button8.setGeometry(0.37*Resolution_Width , 0.75*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button8.clicked.connect(self.Reset_Data_Left)
        self.button9 = QPushButton("Reset Data (Right)", self)
        self.button9.setGeometry(0.49*Resolution_Width , 0.75*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button9.clicked.connect(self.Reset_Data_Right)
        self.button10 = QPushButton("Reset Data (Both)", self)
        self.button10.setGeometry(0.61*Resolution_Width , 0.75*Resolution_Height, 0.12*Resolution_Width, 0.1*Resolution_Height)
        self.button10.clicked.connect(self.Reset_Data_Both)
    #update the variables from the text
    def update_text(self):
        global  maxdata_speed_Dist_graph,  actual_max1 , actual_min1, actual_max2 , actual_min2
        self.label1.setText("{:.2f}".format(max_value1)) 
        self.label2.setText("{:.2f}".format(min_value1)) 
        self.label3.setText("{:.2f}".format(max_value2))  
        self.label4.setText("0")
        self.label5.setText("Current Left    : {:.2f}".format(self.data1[maxdata_speed_Dist_graph]))
        self.label6.setText("Max Left        : {:.2f}".format(actual_max1))
        self.label7.setText("Min Left        : {:.2f}".format(actual_min1))
        self.label8.setText("Current Right   : {:.2f}".format(self.data2[maxdata_speed_Dist_graph]))
        self.label9.setText("Max Right       : {:.2f}".format(actual_max2))
        #self.label10.setText("Min Right       : {:.2f}".format(actual_min2))

    #Draw the axis and lines 
    def paintEvent(self, event):
        global maxdata_speed_Dist_graph , max_value1 , min_value1, max_value2 , min_value2 , actual_max1 , actual_min1, actual_max2 , actual_min2

        painter = QPainter(self)
        #Fake sea background lol
        painter.save()
        painter.translate(0, 0)
        painter.rotate(0)
        painter.setPen(QPen(QColor(120, 120, 120), 10, Qt.SolidLine))
        painter.setBrush(QColor(200, 200, 255))
        painter.drawRect(0, 0, Resolution_Width, Resolution_Height)
        painter.restore()

        #Draw the 1st axis and line, the axis scaling are automatic, it will be based on the absolute max value from the data
        painter.setPen(QPen(Qt.black, 5))
        painter.save()
        painter.translate(0.05*Resolution_Width, 0.35*Resolution_Height)
        painter.drawLine(0, 0.3*Resolution_Height , 0, -0.3*Resolution_Height)
        painter.drawLine(0, 0 ,0.45*Resolution_Width, 0)
        max_value1 = max(abs(x) for x in self.data1)
        min_value1 = - max_value1
        if actual_max1 < max_value1 : 
            actual_max1 = max_value1
        if actual_min1 > min(self.data1):
            actual_min1 = min(self.data1)
        if (max_value1) == 0 :
            max_value1 = 1
        height_y =0.6*Resolution_Height / (2*max_value1)
        for i in range (maxdata_speed_Dist_graph-1):  
            painter.drawLine(i*(0.4*Resolution_Width/maxdata_speed_Dist_graph), -self.data1[i] * height_y ,(i+1)*(0.4*Resolution_Width/maxdata_speed_Dist_graph), -self.data1[i+1]* height_y)
        painter.restore()


        #Draw the 2nd axis and line, the axis scaling are automatic, it will be based on the absolute max value from the data
        painter.save()
        painter.translate(0.55*Resolution_Width, 0.35*Resolution_Height)
        painter.setPen(QPen(Qt.black, 5))
        painter.drawLine(0, 0.3*Resolution_Height , 0, -0.3*Resolution_Height)
        painter.drawLine(0, 0.3*Resolution_Height ,0.45*Resolution_Width, 0.3*Resolution_Height)
        painter.translate(0, 0.3*Resolution_Height)
        max_value2 = max(abs(x) for x in self.data2)
        if (max_value2) == 0 :
            max_value2 = 1
        min_value2 = - max_value2
        if actual_max2 < max_value2 : 
            actual_max2 = max_value2
        if actual_min2 > min(self.data2):
            actual_min2 = min(self.data2)
        height_y =0.6*Resolution_Height / (max_value2)
        for i in range (maxdata_speed_Dist_graph-1):  
            painter.drawLine(i*(0.4*Resolution_Width/maxdata_speed_Dist_graph), -self.data2[i] * height_y ,(i+1)*(0.4*Resolution_Width/maxdata_speed_Dist_graph), -self.data2[i+1]* height_y)
        painter.restore()
        
    #Reset the max and min of both graphs 
    def Reset_Min_Max_Line(self):
        global actual_max1 , actual_min1 , actual_min2 , actual_max2
        actual_max1 =0
        actual_min1 =0
        actual_min2 =0
        actual_max2 =0
    def Reset_Data_Left (self):
        global holder_array1, actual_max1 , actual_min1
        holder_array1 = [0 for _ in range(maxdata_speed_Dist_graph+1)] 
        actual_max1 = 0
        actual_min1 = 0
    def Reset_Data_Right (self):
        global holder_array2, total_distance , actual_min2 , actual_max2
        holder_array2 = [0  for _ in range(maxdata_speed_Dist_graph+1)] 
        total_distance = 0
        actual_min2 =0
        actual_max2 =0
    def Reset_Data_Both (self):
        global holder_array1, holder_array2, total_distance, actual_max1 , actual_min1, actual_min2 , actual_max2
        holder_array1 = [0 for _ in range(maxdata_speed_Dist_graph+1)] 
        holder_array2 = [0  for _ in range(maxdata_speed_Dist_graph+1)] 
        total_distance = 0
        actual_max1 = 0
        actual_min1 = 0
        actual_min2 =0
        actual_max2 =0
    #Update the dataset in the array , these array are used to draw the lines 
    def line_Update(self):
        array1 , array2  = speed_dist()
        self.data1 = array1
        self.data2 = array2 
        self.update_text()
        self.repaint()
#Run Gui , set as function for theading 
def Run_GUI():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
#================================= Threading Call===================================
t1 = threading.Thread(target = MQTT1)
t2 = threading.Thread(target = MQTT2)
t3 = threading.Thread(target = MQTT3)
t4 = threading.Thread(target = MQTT4)
t5 = threading.Thread(target = MQTT5)
t6 = threading.Thread(target = recorder)
t7 = threading.Thread(target = Run_GUI)
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
t7.start()
t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()
t7.join()
#================================= Threading Call===================================


'''#If this is run as main file, it will execute all the functions 
if __name__ == '__main__':
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
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())'''