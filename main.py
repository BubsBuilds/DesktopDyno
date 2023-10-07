from nicegui import ui
import serial
import threading
import time
import json

from pymongo import MongoClient

class dbComm:
    def __init__(self, host='DESKTOP-M8400H1', port=27017, db_name='pf'):
        # Initialize MongoDB client
        self.client = MongoClient(host, port)
        self.db = self.client['DynoDB']
        self.resColl = 'RawResuilts'

    def insert_one(self, collection_name, data):
        """Insert one record into a MongoDB collection."""
        collection = self.db[collection_name]
        collection.insert_one(data)

    def insert_many(self, collection_name, data_list):
        """Insert multiple records into a MongoDB collection."""
        collection = self.db[collection_name]
        collection.insert_many(data_list)

    def find(self, collection_name, query=None, projection=None):
        """Query data from a MongoDB collection."""
        collection = self.db[collection_name]
        return collection.find(query, projection)

    def update_one(self, collection_name, filter_query, update_data):
        """Update one record in a MongoDB collection."""
        collection = self.db[collection_name]
        collection.update_one(filter_query, {'$set': update_data})

    def delete_one(self, collection_name, query):
        """Delete one record from a MongoDB collection."""
        collection = self.db[collection_name]
        collection.delete_one(query)

    def close(self):
        """Close MongoDB connection."""
        self.client.close()

class driverComm:
    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(port, baudrate)

    def startDC(self, volts):
        #Do some stuff
        pass

class encoderComm:
    def __init__(self, port, baudrate=250000):
        self.ser = serial.Serial(port, baudrate)
        time.sleep(2)  # Give some time for the connection to be established
        self.datFlag = False


    def send(self, command, data=None):
        msg = {"command": command, "data": data}
        encoded_msg = json.dumps(msg).encode()
        self.ser.write(encoded_msg)
        return self.receive_response()

    def receive_response(self):
        raw_data = self.ser.readline().decode().strip()
        response = json.loads(raw_data)
        return response

    def contDatColl(self):
        riseTimes = []
        riseDeltas = []
        fallTimes = []
        fallDeltas = []
        curType = ''
        while self.datFlag:
            if enComm.ser.inWaiting() > 0:
                curRes = enComm.receive_response()
                for count, key in enumerate(curRes):
                    if count == 0:
                        curType = curRes[key]
                    else:
                        if curType == 'R':
                            riseTimes.append(float(key))
                            riseDeltas.append(float(curRes[key]))
                        elif curType == 'F':
                            fallTimes.append(float(key))
                            fallDeltas.append(float(curRes[key]))

            time.sleep(0.005)

    def close(self):
        self.ser.close()

if __name__ == '__main__':
    enComm = encoderComm(port = '/dev/ttyACM0', baudrate=250000)

    '''
    Start ui implementation
    '''
    async def _runTest():
        runBut.disable()
        stopBut.enable()
        enComm.datFlag = True
        datThread = threading.Thread(target=enComm.contDatColl, args=(1,))
        datThread.start()

    async def _stopTest():
        runBut.enable()
        stopBut.disable()

    '''
    Test Configuration
    '''
    with ui.card().props(add='horizontal'):
        ui.label('-----------Test Settings-----------').style('font-size: 200%; font-weight: 400')
        ui.separator()
        with ui.card_section():
            with ui.grid(columns=2):
                ui.label('Drive Voltage: ')
                slider = ui.slider(min=0, max=24, value=12, step=0.5).props(add='snap label-always')

                ui.input(label='Run Name', placeholder='<ENTER NAME>')

                runBut = ui.button('Start Run', on_click=_runTest)
                stopBut = ui.button('Stop Run', on_click=_stopTest)



    '''
    Data Visualization
    '''
    with ui.card().props(add='horizontal'):
        ui.label('-----------Run Results-----------').style('font-size: 200%; font-weight: 400')
        ui.separator()
        with ui.card_section():
            with ui.grid(columns=2):
                ui.label('Drive Voltage')
                slider = ui.slider(min=0, max=24, value=12, step=0.5).props(add='snap label-always')
        #ui.label('Drive Voltage')
        #slider = ui.slider(min=0, max=24, value=12, step=0.5)
        #slider.props(add='snap')
        runBut = ui.button('Start Run', on_click=_runTest)
    ui.dark_mode().enable()
    ui.run(reload=False)




