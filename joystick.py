import time
import serial
import serial.tools.list_ports

def findArduinoUnoPort():
        portList = list(serial.tools.list_ports.comports())
        for port in portList:
            if ("VID:PID=2341:0043" in port[0] or
                "VID:PID=2341:0043" in port[1] or
               "VID:PID=2341:0043" in port[2]):
                    return port[0]


def connect_btn():
    unoPort = findArduinoUnoPort()

     if unoPort:
        try:
            arduino = serial.Serial(port='COM5', baudrate=9600,timeout=0.1)
            print("Success")
            return arduino

        except Exception:
            print("Error")



def write_read(data, arduino):
        arduino.write(bytes(data, 'utf-8'))



arduino = connect_btn()
time.sleep(2)
if arduino:
    write_read("1", arduino)
    
while True:
    try:
        a = arduino.readline()
        print(a)
    except Exception:
        print("Error")




        
