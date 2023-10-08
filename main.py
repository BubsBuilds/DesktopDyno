import math
from nicegui import ui
from matplotlib import pyplot
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
        self._encAngle = 12
        self._rejVel = 20000
        self.pdVlim = 0.8
        self.riseVals = []
        self.fallVals = []

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
        count =0;


        curType = ''
        # Loop continuously monitors serial port for responses from MCU
        while self.datFlag:
            if count == 0:
                self.riseTimes = []
                self.fallTimes = []
                self.riseVels = []
                self.riseAccels = []
                self.riseVelTimes = []
                self.riseAccTimes = []
                self.fallVels = []
                self.fallVelTimes = []
                self.fallAccels = []
                self.fallAccTimes = []
            if self.ser.inWaiting() > 0:
                curRes = self.receive_response()
                for count, key in enumerate(curRes):
                    if count == 0:
                        curType = curRes[key]
                    else:
                        if curType == 'R':
                            self.riseTimes.append(float(curRes[key]))
                        elif curType == 'F':
                            self.fallTimes.append(float(curRes[key]))
            time.sleep(0.005)
            count += 1
        # Calculate velocities and accelerations
        self.riseVals = self._calcDers(self.riseTimes)
        self.fallVals = self._calcDers(self.fallTimes)
        print(self.riseVals)
        print(self.fallVals)

    def _calcDers(self, times):
        velTimes = []
        vels = []
        accTimes = []
        accs = []
        for inc, rec in enumerate(times):
            if inc > 0: #Calc velocities only from the second record.
                dtV =rec-times[inc-1]
                angVel = self._encAngle / (dtV/1000000)
                if angVel < self._rejVel: #simple attempt to reject outliers
                    #velTimes.append(rec)
                    #vels.append(angVel)
                    if inc == 1:
                        velTimes.append(times[inc])
                        vels.append(angVel)
                    if inc > 1: #Beyond the 2nd entry, also calc accel
                        dV = angVel-vels[-1]
                        #additional outlier check using threshold of percent change in velocity between two points.
                        pdV = dV/vels[-1]
                        print(pdV)
                        if pdV < self.pdVlim:
                            dtA = rec - velTimes[-1]
                            angAccel = dV / dtA
                            velTimes.append(times[inc])
                            vels.append(angVel)
                            accTimes.append(times[inc])
                            accs.append(angAccel)
        return velTimes, vels, accTimes, accs

    def close(self):
        self.ser.close()

if __name__ == '__main__':
    enComm = encoderComm(port = '/dev/ttyACM2', baudrate=250000)

    '''
    Start ui implementation
    '''
    async def _runTest():
        runBut.disable()
        stopBut.enable()
        enComm.datFlag = True
        datThread = threading.Thread(target=enComm.contDatColl)
        datThread.start()

    async def _stopTest():
        runBut.enable()
        stopBut.disable()
        enComm.datFlag = False
        time.sleep(0.01)
        #datThread.join()
        #print(enComm.riseTimes[1:])
        #print(enComm.riseVels)
        #print(enComm.fallVels)
        rVelFig.push(x=enComm.riseVals[0], Y=[enComm.riseVals[1]])
        fVelFig.push(x=enComm.fallVals[0], Y=[enComm.fallVals[1]])
        rAccFig.push(x=enComm.riseVals[2], Y=[enComm.riseVals[3]])
        fAccFig.push(x=enComm.fallVals[2], Y=[enComm.fallVals[3]])


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
                ui.label(' ')

                runBut = ui.button('Start Run', on_click=_runTest)
                stopBut = ui.button('Stop Run', on_click=_stopTest)



    '''
    Data Visualization
    '''
    with ui.card().props(add='horizontal'):
        ui.label('-----------Run Results-----------').style('font-size: 200%; font-weight: 400')
        ui.separator()
        plotDat = ui.button('Plot Results', on_click=_runTest)
        with ui.pyplot(figsize(10,4)):
            pyplot.scatter()
        rVelFig = ui.line_plot(n=1, limit=1000, figsize=(10,4), ).with_legend(['Rise Velocities'], ncol=1)
        fVelFig = ui.line_plot(n=1, limit=1000, figsize=(10,4)).with_legend(['Fall Velocities'], ncol=1)
        rAccFig = ui.line_plot(n=1, limit=1000, figsize=(10,4)).with_legend(['Rise Accels'], ncol=1)
        fAccFig = ui.line_plot(n=1, limit=1000, figsize=(10,4)).with_legend(['Fall Accels'], ncol=1)


    ui.dark_mode().enable()
    ui.run(reload=False)




