#%matplotlib qt

from helper import *
from helper import read_press
##TODO
# Your user configurations
ipadresse = "138.232.37.30"    # 138.232.37.30 für T4
user = "Mahdiyeh"                         # Lilli damit T4/T7 erkannt wird
frequency = 50                          # Messfrequenz in Hertz
temperatur_analog_input_idx = [2,3]    # Angeschlossene Inputs Labjack temperatursenosr (ehemalig 4 am T4, 2 for T7)
pt_type = [42,42]                     # 42 für PT1000, 40 für PT100
pressure_analog_input_idx = [0,1]        # Angeschlossene Inputs Labjack Drucksensor
pressure_sensor_range = [[0,100],[0,2]]             # Druckbereich Drucksensor z.b. [0,100] [0,2] bei [0,100] wird tariert
filename = "data/test1"
columnnames = "t/s T1/°C T2/°C p100/bar p2/bar\n"

##END TODO

# Initial checks
assert len(temperatur_analog_input_idx) == len(pt_type), \
    f"every temperature sensor needs to be declared as a certain [42,40,42 ...]"
assert len(pressure_analog_input_idx) == len(pressure_sensor_range), \
    f"for each pressure sensor the pressure range must be stated"

assert len(pressure_analog_input_idx)+len(temperatur_analog_input_idx) == columnnames.count(" "), \
    f"each sensor stores to a list, put in the correct columnnames, temperature is stored first"
# Initialize devicef
try:
    if user == "Mahdiyeh":
        handle = ljm.openS("T4", "ETHERNET", ipadresse) # ehemalig T4
    else:
        handle = ljm.openS("T4", "USB", "ANY")
except:
    raise Exception('Zuerst https://fwauth-innr.uibk.ac.at/ öffnen und einloggen!')

# File name handling
now = datetime.datetime.now()
formatted_time = now.strftime("%Y%m%d_%H-%M-%S")
filename += f"_{formatted_time}.txt"

if pressure_sensor_range[0][-1]==100:
    try:
        voltage0=np.genfromtxt("%s_current0.dat"%now.strftime("%Y%m%d"))
        # maybe add date timestep, as it is necessary to do a measurement 
        # without pressure at the same day
        
    except:
        raise Exception("please run tara_daily_pressure.py ")
else:
    voltage0=0
# Print device info
info = ljm.getHandleInfo(handle)
print(f"Opened LabJack with Device type: {info[0]}, Connection type: {info[1]},\n"
      f"Serial number: {info[2]}, IP address: {ljm.numberToIP(info[3])}, Port: {info[4]},\nMax bytes per MB: {info[5]}")
print(".....................................................\nMeasurements\n")
# Configure sensors
for i in range(len(temperatur_analog_input_idx)):
    configure_temp_ain(handle, temperatur_analog_input_idx[i], pt_type[i], 1)

# Create arrays to store measurements
temperatures = []
pressures = []
t = []

read_press(handle, 0, pressure_sensor_range[0][1])

# Prepare the plot
linestyle = ['b-','r-','k-']
plt.ion()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
linet = []
linep = []
for i in range(len(temperatur_analog_input_idx)):
    linet.append(ax1.plot([], [], linestyle[i], label="AIN %i"%temperatur_analog_input_idx[i])[0])
for i in range(len(pressure_analog_input_idx)):
    linep.append(ax2.plot([], [], linestyle[i], label="AIN %i"%pressure_analog_input_idx[i])[0])   

ax1.set_xlabel('Time / s')
ax1.set_ylabel('Temperature / °C')
ax2.set_xlabel('Time / s')
ax2.set_ylabel('Pressure / bar')
ax1.legend(loc='lower right',title='labjack index')


with open(f"{filename}", "w") as file:
    ljm.startInterval(1, int(1e6 * 1 / frequency))  # Set interval timing
    file.write(f"{columnnames}")
    
    t0 = time.time()

    while True:
        try:
            # Read temperatures
            if temperatur_analog_input_idx:
                temperature = [read_temp(handle, i) for i in temperatur_analog_input_idx]
                print("TEMPERATURE " + " ".join(f"{x:.6f} °C" for x in temperature))
            else:
                temperature=[]
            temperatures.append(temperature)
            
            # Read pressures if applicable
            if pressure_analog_input_idx:
                pressure = [read_press(handle, idx, voltage0,pressure_sensor_range[i]) for i, idx in enumerate(pressure_analog_input_idx)]
                print("PRESSURE " + " ".join(f"{x:.6f} bar" for x in pressure))
            else:
                pressure = []
            pressures.append(pressure)
            print("------------------------------------------------")
            # Manage time data
            ti = time.time() - t0
            t.append(ti)

            # Trim lists to keep recent data only
            temperatures = temperatures[-150:]
            pressures = pressures[-150:]
            t = t[-150:]
            
            # Write to file
            file.write(f"{ti} {' '.join([str(temp) for temp in temperature])} {' '.join([str(p) for p in pressure])} \n")
            file.flush()

            # Update plot data
            for i in range(len(temperatur_analog_input_idx)):
                linet[i].set_xdata(t)
                linet[i].set_ydata(np.array(temperatures)[:, i])  # Assuming first temperature sensor for plot

            for i in range(len(pressure_analog_input_idx)):
                linep[i].set_xdata(t)
                linep[i].set_ydata(np.array(pressures)[:, i])  # Assuming first temperature sensor for plot

            # Set limits
            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            # Redraw canvas
            fig.canvas.draw()
            fig.canvas.flush_events()

            # Pause for animation effect
            plt.pause(0.1)

            # Wait for next interval
            skippedIntervals = ljm.waitForNextInterval(1)
            if skippedIntervals > 0:
                print(f"\nSkippedIntervals: {skippedIntervals}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error:", e)
            break

# Close interval and device
ljm.cleanInterval(1)
ljm.close(handle)
