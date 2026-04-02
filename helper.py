from labjack import ljm
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime

def p(voltage,prange):
    # see for instance https://oceancontrols.com.au/LAJ-034.html
    return (voltage-0.47)*(prange[1]-prange[0])/(2.36-0.47)

def convert_voltage_pressure(voltage,voltage0,prange=[0,100]):

    # resisitors in current shunt lead to a resistance of 118 Ohm,
    # I=U/R, 1 bar is 0.004A and (for instance) 100 bar is 0.020 A
    # measurement range = 16mA, hence /0.016

    return (voltage-voltage0)*(prange[1]-prange[0])/118/0.016+1

def configure_ain(handle, channel, property,value):
    """ function to configure analog input

    Args:
        handle (ljm attribute): 
            labjack module class
        channel (int): 
            channel index; from 0 to 11
        property (str): 
            property which should be set: "RANGE","RESOLUTION_INDEX", etc
        value (int,float):
            value that should be set; 
                * 0 to 5 for RESOLUTION_INDEX;
                * 
    """
    # Construct the name of the range parameter for the given channel
    property_name = f"AIN{channel}_{property}"
    # Write the desired range value
    ljm.eWriteName(handle, property_name, value)

def configure_temp_ain(handle,channel,PT_index=40,T_unit=0):
    """Function to configure the channel according to the built-in temperature read method (convert volts to temperatur)
     for the specified parameters in the comments below.

    Args:
        handle (labjack class): labjack device
        channel (int, optional): Number of the input channel. Defaults to 5.
    """
    
    configure_ain(handle,channel,"RESOLUTION_INDEX",5) # highest resolution for the T4 is index 5, 8 for T7
    configure_ain(handle,channel,"EF_INDEX",PT_index) #PT1000; für Pt100 40 statt 42
    configure_ain(handle,channel,"EF_CONFIG_A",T_unit) #Set result units to 0 Kelvin; 1 °C
    configure_ain(handle,channel,"EF_CONFIG_B",4) #Set excitation circuit to 4.
    configure_ain(handle,channel,"EF_CONFIG_D",2.5) #Vref on the LJTR is 2.50 volts.
    configure_ain(handle,channel,"EF_CONFIG_E",1000) #We are using the 1k version of the LJTR.

def read_temp(handle,channel=3): # 3 for T4, 5 for T7
    """Read the temperature using the built-in temperature sensor read method

    Args:
        handle (labjack class): labjack device
        channel (int, optional): Number of the input channel. Defaults to 5.

    Returns:
        _type_: _description_
    """
    aName = "AIN%i_EF_READ_A"%channel # channels
    temp = ljm.eReadName(handle,  aName)
    return temp


def read_press(handle,channel,voltage0,prange=[0,100]):
    """read the pressure using a 4-20mA sensor

    Args:
        handle (labjack class): labjack device
        channel (int, optional): Number of the input channel. Defaults to 5.
        prange (tuple,)

    Returns:
        _type_: _description_
    """
    
    aName = "AIN%s"%channel # channels
    voltage = ljm.eReadName(handle,  aName)
    # press = convert_voltage_pressure(voltage,voltage0,prange)
    press = p(voltage,prange)
    return press


def set_DACvoltage(handle,state=0,channel=0):
    """Set the voltage of the DAC channels to controll between 0 and 3 Volts as I/O signal for the Crydom CN024D05 Relay

    Args:
        handle (labjack class): labjack device
        state (int, optional): state 0 to turn off relay, 1 for on. Defaults to 0.
        channel (int, optional): Number of DAC channel; 0 or 1. Defaults to 0.
    """
     # Output state = low (0 = low, 1 = high)
    if state == 0:
        volts = 0
    elif state == 1:
        volts = 3
    else:
         print("Invalid state; only 0 for off or 1 for on")
    print("Set voltage output of DAC{channel} to {volts} volt")
    ljm.eWriteName(handle, "DAC{channel}", volts)
