# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 08:28:18 2024

@author: grube
"""

"""
Relevant Documentation:
 
For the pressure Measurement
https://support.labjack.com/docs/ljtick-currentshunt-datasheet
https://support.labjack.com/docs/measuring-current-app-note#MeasuringCurrent(AppNote)-LJTick-CurrentShunt 
    
LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Single Value Functions(such as eReadName):
        https://labjack.com/support/software/api/ljm/function-reference/single-value-functions
    Multiple Value Functions(such as eWriteNames):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions
    Timing Functions(such as StartInterval):
        https://labjack.com/support/software/api/ljm/function-reference/timing-functions
 
T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    DAC:
        https://labjack.com/support/datasheets/t-series/dac

"""
from labjack import ljm
import matplotlib.pyplot as plt

import datetime
import time
from matplotlib.animation import FuncAnimation
from helper import *
import numpy as np


ipadresse ="138.232.37.30" # 138.232.37.30 für T4
# INITIALIZE DEVICE
## Connect to device
# handle = ljm.openS("T4", "ANY", "ANY")
try:
    handle = ljm.openS("T4", "ETHERNET", ipadresse)  # T4/T7 device, Any connection, Any identifier
except:
    print('Zuerst https://fwauth-innr.uibk.ac.at/ öffnen und einloggen! ')
## print info 
info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))



ain_IDX = [0]
numFrames = len(ain_IDX)
aNames = ["AIN%i"%ain_IDX[i] for i in range(numFrames)]

intervalHandle = 1
ljm.startInterval(intervalHandle, 1000000)
i  = 0
curr_array = list([])
while i<1000:
        aValues = ljm.eReadNames(handle, numFrames, aNames)[0]
        curr_array.append(aValues)
        i+=1



# Close interval and device handles
ljm.cleanInterval(intervalHandle)
ljm.close(handle)


meancurr = np.nanmean(curr_array)
print(meancurr)
now = datetime.datetime.now()
np.savetxt("%s_current0.dat"%now.strftime("%Y%m%d"),[meancurr])
plt.plot(curr_array)
plt.show()