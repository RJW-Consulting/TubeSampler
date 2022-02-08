# -*- coding: utf-8 -*-
"""
Goldstein Lab Sequential Tube Sampler
Low level hardware driver class
Presents member functions to control
pump, MFCs, valves, sensors, and indicator lights
Author: Robin Weber
Start date: 9/21/2021
"""

import time
import sys
#import board
from board import SCL, SDA
import busio
import RPi.GPIO as GPIO
import relay_boards
from relay_boards import AlicatMFC
import relay_modbus
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis
import adafruit_mprls
import adafruit_tca9548a
import adafruit_bme280
import adafruit_ahtx0
import adafruit_ina219
import datetime

class sampler():
    def __init__(self, errLogName='/home/pi/SamplerDev/logs/SamplerErrors.log', nullValue=None):
        print('initilaizing sampler')
        self.errLogName = errLogName
        self.nullValue = nullValue
        self.fatalErrors = ''
        self.nonFatalErrors = ''
        self.currTube = 0
        # set up the power relays (PI relay board)
        self.Relay_Ch1 = 26
        self.Relay_Ch2 = 20
        self.Relay_Ch3 = 21
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Relay_Ch1,GPIO.OUT)
        GPIO.setup(self.Relay_Ch2,GPIO.OUT)
        GPIO.setup(self.Relay_Ch3,GPIO.OUT)
        GPIO.output(self.Relay_Ch1,GPIO.HIGH) # set valve power relay off
        

        # set up the I2C bus
        
        self.i2c = busio.I2C(SCL, SDA)
        # Set up the neotrillis indicator light array
        trelli = [
                [NeoTrellis(self.i2c, False, addr=0x2E), 
                 NeoTrellis(self.i2c, False, addr=0x2F)]]
        self.trellis = MultiTrellis(trelli)
        # some color definitions
        self.colors = {'RED':(255, 0, 0),
                        'ORANGE':(255, 75, 0),
                        'YELLOW':(255, 150, 0),
                        'GREEN':(0, 255, 0),
                        'CYAN':(0, 255, 255),
                        'BLUE':(0, 0, 255),
                        'INDIGO':(60, 0, 255),
                        'PURPLE':(180, 0, 255),
                        'DPURPLE':(255, 0, 255),
                        'OFF':(0, 0, 0)}
        self.trellis_xsize = 8
        self.trellis_ysize = 4
        for y in range(self.trellis_ysize):
            for x in range(self.trellis_xsize):
                self.trellis.color(x, y, self.colors['OFF'])
                #time.sleep(0.05)
        # Set up sensors
        # first, plumbing pressure sensors, which are on I2C multiplexer channels
        # so we need to set those up first
        # Create the TCA9548A object and give it the I2C bus
        self.tca = adafruit_tca9548a.TCA9548A(self.i2c)
        # plumbing pressure sensors are Adafruit MPRLS ported pressure sensors
        # For each mprls sensor, create it using the TCA9548A channel instead of the I2C object
        self.mprls0 = self.initMPRLS(self.tca[0],'0')
        self.mprls1 = self.initMPRLS(self.tca[1],'1')
        self.mprls2 = self.initMPRLS(self.tca[2],'2')
        self.mprls3 = self.initMPRLS(self.tca[3],'3')
        # ambient pressure (plus temperature, humudity) sensors (Adafuit BME280) are mounted on the two
        # manifold modules, with thier I2C wiring on the multiplexed I2C channels for those
        # modules
        self.mod0_i2c = self.tca[4]
        self.mod1_i2c = self.tca[5]
        self.bme280_0 = self.initBME280(self.mod0_i2c,'0')
        self.bme280_1 = self.initBME280(self.mod1_i2c,'1')
        self.hasPowerSensor = False
        if self.hasPowerSensor:
            # a current/voltage sensor to measure the power to the valves
            self.ina219_0 = adafruit_ina219.INA219(self.i2c)
        # Now for the manifold valve relay boards.  Declare the serial port for the MODBUS
        SERIAL_PORT = '/dev/ttyS0'
        # Create MODBUS object
        self._modbus = relay_modbus.Modbus(serial_port=SERIAL_PORT)
        # Open serial port
        try:
            self._modbus.open()
        except relay_modbus.SerialOpenException as err:
            print(err)
            sys.exit(1)
        # Create relay board objects
        self.valveBoard0 = relay_boards.R421A08(self._modbus, address=1)
        self.valveBoard1 = relay_boards.R421A08(self._modbus, address=2)
        # Create MFC objects
        self.mfc_clearing = AlicatMFC.AlicatMFC(self._modbus, address=3)
        self.mfc_sample = AlicatMFC.AlicatMFC(self._modbus, address=4)
        self.NUM_TUBES = 16
        self.TUBES_PER_MODULE = 8
        self.NUM_VALVES = 32
        self.VALVES_PER_MODULE = 16
        self.NUM_MODULES = 2
        self.EXCEPTION_RETRIES = 10

    def logError(self, message, exeption=None):
        exType = ''
        if exeption:
            exType = str(type(exeption))
        logline = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f ,")+exType+' '+message
        lf = open(self.errLogName,'a')
        lf.write(logline+'\n')
        lf.close()
    
    def initMPRLS(self,channel, mprlsID):
        try:
            mprls = adafruit_mprls.MPRLS(channel)
        except ValueError as err:
            errStr = 'MPRLS '+mprlsID+' not responding to I2C'
            self.logError(errStr, exeption=err)
            self.fatalErrors+= errStr+'\n'
            return None
        except Exception as err:
            errStr = 'Uncaught exception initializing MPRLS '+mprlsID+': '+type(err)
            self.logError(errStr, exeption=err)
            self.fatalErrors+= errStr+'\n'
            return None
        return mprls            

    def initBME280(self,channel,bme280ID):
        try:
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(channel)
        except ValueError as err:
            errStr = 'Pressure sensor BME280 '+bme280ID+' not responding to I2C'
            print(err)
            self.logError(errStr, exeption=err)
            self.nonFatalErrors+= errStr+'\n'
            return None
        except Exception as err:
            errStr = 'Uncaught exception initializing pressure sensor BME280 '+bme280ID+': '+type(err)
            self.logError(errStr, exeption=err)
            self.nonFatalErrors+= errStr+'\n'
            return None
        return bme280            
            
        
    def setValveLight(self,module,valve,color):
        vlights = [[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[7,1],[6,1],[5,1],[4,1],[3,1],[2,1],[1,1],[0,1]]
        x = vlights[valve-1][0]
        y = vlights[valve-1][1]
        if module > 0:
            y+=2
        #self.setIndicatorLight(x,y,color)
        try:
            self.trellis.color(x, y, color)
        except Exception as err:
            return
        


    def setValve(self,module, vnum, state, color=None):
        if color == None:
            color = self.colors['BLUE']
        if module == 0:
            rboard = self.valveBoard0
        else:
            rboard = self.valveBoard1
        if state:
            rboard.on(vnum)
            self.setValvePower(True)
            self.setValveLight(module,vnum,color)
        else:
            rboard.off(vnum)
            self.setValvePower(False)
            self.setValveLight(module,vnum,self.colors['OFF'])
            
    def closeAllValves(self):
        for m in range(0,self.NUM_MODULES):
            for v in range(1,self.VALVES_PER_MODULE+1):
                self.setValve(m,v,False)
        

    def setTube(self, tnum, state, color=None, pauseBetween=0):
        tubeValves = [[1,16],[2,15],[3,14],[4,13],[5,12],[6,11],[7,10],[8,9]]
        if tnum > self.TUBES_PER_MODULE:
            module = 1
            t = tnum - self.TUBES_PER_MODULE
        else:
            module = 0
            t = tnum
        self.closeAllValves()
        self.setValve(module,tubeValves[t-1][0],state,color)
        if pauseBetween > 0:
            time.sleep(pauseBetween)
        self.setValve(module,tubeValves[t-1][1],state,color)
        if state:
            self.currTube = tnum
        else:
            self.currTube = 0
    
    def currentTube(self):
        return self.currTube
        
    def setPump(self,state=False):
        if state == True:
            GPIO.output(self.Relay_Ch2,GPIO.LOW) # set valve power relay On 
        else:
            GPIO.output(self.Relay_Ch2,GPIO.HIGH) # set valve power relay off 

    def setValvePower(self,state=True):
        if state == True:
            GPIO.output(self.Relay_Ch1,GPIO.LOW) # set valve power relay On 
        else:
            GPIO.output(self.Relay_Ch1,GPIO.HIGH) # set valve power relay off 

    def setMFCPower(self,state=True):
        if state == True:
            GPIO.output(self.Relay_Ch3,GPIO.LOW) # set valve power relay On 
        else:
            GPIO.output(self.Relay_Ch3,GPIO.HIGH) # set valve power relay off 
            

    def testTrellis(self):
        mycolors = list(self.colors.values())
        print('Testing trellis')
        for y in range(0,self.trellis_ysize):
            for x in range(0,self.trellis_xsize):
                self.trellis.color(x, y, mycolors[x])
                time.sleep(0.05)
        time.sleep(2)
        for y in range(self.trellis_ysize):
            for x in range(self.trellis_xsize):
                self.trellis.color(x, y, self.colors['OFF'])
                time.sleep(0.05)

    def getPressure(self,sensor=0):
        ret = -99999
        try:
            if sensor == 0:
                ret = self.mprls0.pressure
            if sensor == 1:
                ret = self.mprls1.pressure
            if sensor == 2:
                ret = self.mprls2.pressure
            if sensor == 3:
                ret = self.mprls3.pressure
            if sensor == 4:
                ret = self.bme280_0.pressure
            if sensor == 5:
                ret = self.bme280_1.pressure
        except Exception as err:
            if sensor == 0:
                message = 'Error getting raw vacuum pressure '
            if sensor == 1:
                message = 'Error getting regulated vacuum pressure'
            if sensor == 2:
                message = 'Error getting clearing line presure '
            if sensor == 3:
                message = 'Error getting sample line pressure '
            if sensor == 4:
                message = 'Error getting module 0 ambient pressure '
            if sensor == 5:
                message = 'Error getting module 1 ambient pressure '
            self.logError(message+str(err))                
            ret = -99999
        return ret
                

    def getTemperature(self,sensor=4):
        ret = -99999
        #for retry in range(1,self.EXCEPTION_RETRIES+1):
        try:
            if sensor == 4:
                ret = self.bme280_0.temperature
            if sensor == 5:
                ret = self.bme280_1.temperature
            if sensor == 6:
                #ret = self.aht20_0.temperature
                ret = -99
            if sensor == 7:
                #ret = self.aht20_1.temperature
                ret = -99
        except Exception as err:
            message = ''
            if sensor == 4:
                message = 'Error getting module 0 upper temperature '
            elif sensor == 5:
                message = 'Error getting module 1 upper temperature '
            elif sensor == 6:
                message = 'Error getting module 0 lower temperature '
            elif sensor == 7:
                message = 'Error getting module 1 lower temperature '
            self.logError(message+str(err))                
            ret = -99999
            print('Returning from temperature sensor error')
           #self.logError('Retry #'+str(retry))
        #self.logError('getTemperature giving up.')
        return ret
                
                

    def getHumidity(self,sensor=4):        
        if sensor == 4:
            return self.bme280_0.humidity
        if sensor == 5:
            return self.bme280_1.humidity
        if sensor == 6:
            return self.aht20_0.relative_humidity
        if sensor == 7:
            return self.aht20_1.relative_humidity
        
    def getAltitude(self,sensor=4):
        if sensor == 4:
            return self.bme280_0.altitude
        if sensor == 5:
            return self.bme280_1.altitude
        
    def getPressures(self):
        d = {}
        d['p_vac'] = self.getPressure(0)
        d['p_reg'] = self.getPressure(1)
        d['p_clear'] = self.getPressure(2)
        d['p_samp'] = self.getPressure(3)
        d['p_mod0'] = self.getPressure(4)
        d['p_mod1'] = self.getPressure(5)
        return d

    def getAltitudes(self):
        d = {}
        d['alt_mod0'] = self.getAltitude(4)
        d['alt_mod1'] = self.getAltitude(5)
        return d
        
    def getTemperatures(self):
        d = {}
        d['t_mod0_u'] = self.getTemperature(4)
        d['t_mod1_u'] = self.getTemperature(5)
        d['t_mod0_l'] = self.getTemperature(6)
        d['t_mod1_l'] = self.getTemperature(7)
        return d

    def getHumidities(self):
        d = {}
        d['rh_mod0_u'] = self.getHumidity(4)
        d['rh_mod1_u'] = self.getHumidity(5)
        d['rh_mod0_l'] = self.getHumidity(6)
        d['rh_mod1_l'] = self.getHumidity(7)
        return d

    def getValvePower(self):
        d = {}
        if self.hasPowerSensor:
            d['valve_I'] = self.ina219_0.current
            d['valve_Vbus'] = self.ina219_0.bus_voltage
            d['valve_Vshunt'] = self.ina219_0.shunt_voltage
        else:
            d['valve_I'] = -99999
            d['valve_Vbus'] = -99999
            d['valve_Vshunt'] = -99999
        return d
        
        
    def setClearingFlow(self, flow_lpm):
        trying = True
        retry = 0
        while trying:
            try:
                self.mfc_clearing.setpoint(flow_lpm)
            except Exception as err:
                self.logError('Error setting clearing flow, '+str(err))                
                retry += 1
                if retry > self.EXCEPTION_RETRIES:
                    trying = False
                    self.logError('Giving up.')
                else:
                    self.logError('Retry #'+str(retry))
            else:
                trying = False
        
    def getClearingFlow(self):
        trying = True
        retry = 0
        ret = None
        while trying:
            try:
                ret = self.mfc_clearing.readMassFlow()
            except Exception as err:
                self.logError('Error getting clearing flow, '+str(err))                
                retry += 1
                if retry > self.EXCEPTION_RETRIES:
                    trying = False
                    self.logError('Giving up.')
                else:
                    self.logError('Retry #'+str(retry))
            else:
                trying = False
        return ret
                
    
    def getClearingMFCStatus(self):
        trying = True
        retry = 0
        ret = None
        while trying:
            try:
                ret = self.mfc_clearing.readback()
            except Exception as err:
                self.logError('Error getting clearing MFC registers, '+str(err))                
                retry += 1
                if retry > self.EXCEPTION_RETRIES:
                    trying = False
                    self.logError('Giving up.')
                else:
                    self.logError('Retry #'+str(retry))
            else:
                trying = False
        return ret
    
    def setSampleFlow(self, flow_lpm):
        trying = True
        retry = 0
        while trying:
            try:
                self.mfc_sample.setpoint(flow_lpm)
            except Exception as err:
                self.logError('Error setting sample MFC flow, '+str(err))                
                retry += 1
                if retry > self.EXCEPTION_RETRIES:
                    trying = False
                    self.logError('Giving up.')
                else:
                    self.logError('Retry #'+str(retry))
            else:
                trying = False

        
    def getSampleFlow(self):
        trying = True
        retry = 0
        ret = None
        while trying:
            try:
                ret = self.mfc_sample.readMassFlow()
            except Exception as err:
                self.logError('Error getting sample flow, '+str(err))                
                retry += 1
                if retry > self.EXCEPTION_RETRIES:
                    trying = False
                    self.logError('Giving up.')
                else:
                    self.logError('Retry #'+str(retry))
            else:
                trying = False
        return ret
    
    def getSampleMFCStatus(self):
        trying = True
        retry = 0
        ret = None
        while trying:
            try:
                ret = self.mfc_sample.readback()
            except Exception as err:
                self.logError('Error getting sample MFC registers, '+str(err))                
                retry += 1
                if retry > self.EXCEPTION_RETRIES:
                    trying = False
                    self.logError('Giving up.')
                else:
                    self.logError('Retry #'+str(retry))
            else:
                trying = False
        return ret
     
                