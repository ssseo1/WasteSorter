import serial
import BoW_predict
import time

arduino = serial.Serial(port='/dev/cu.usbmodem11301', baudrate=115200, timeout=.1) 

recycle_items = ['bottle','can','paper','soda','sugarbox','tproll']
trash_items = ['banana','napkin','plasticbag','sock','styrofoam','wrapper']

# wait for the string prompt from Arduino
while(1):
    try:
        msg = arduino.readline().decode('utf-8').strip()
    except:
        msg = arduino.readline()
    if(msg != ''):
        print(msg)
    if(msg == 'IDENTIFY OBJECT'):
        # take picture and identify
        image = BoW_predict.takeSinglePicture()
        objectName = BoW_predict.identifyObject(image)

        # keep reading until there is an object found, not just background
        while(objectName == 'bg'):
            image = BoW_predict.takeSinglePicture()
            objectName = BoW_predict.identifyObject(image)
            time.sleep(0.5)

        # object was detected, "debounce" the reading to ensure a proper reading
        # wait for object to be placed and hand removed from the scene
        # take 10 captures to average out the reading
        time.sleep(1)
        print('Object detected. Taking multi pic')
        images = BoW_predict.takeMultiPic(10)
        names = []
        for image in images:
            objectName = BoW_predict.identifyObject(image)
            names.append(objectName)
        # find the most common reading
        objectName = max(set(names), key=names.count)
        # print(names)
        print(f"Object Detected: {objectName}")

        if objectName == 'bg':
            objectID = '0'
        elif objectName in trash_items:
            objectID = '1'
        else: # recyclable
            objectID = '2'
        arduino.write(bytes(objectID, 'utf-8'))