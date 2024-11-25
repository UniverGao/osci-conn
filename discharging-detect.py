"""An example of adding devices via Python code."""

import time
import csv
import numpy as np
from tm_devices import DeviceManager
from tm_devices.drivers import MDO3
from tm_devices.helpers import (
    DMConfigOptions,
    PYVISA_PY_BACKEND,
    SerialConfig,
    SYSTEM_DEFAULT_VISA_BACKEND,
)

# Specific config options can optionally be passed in when creating
# the DeviceManager via a dataclass, they are used to update any existing
# configuration options from a config file.
CONFIG_OPTIONS = DMConfigOptions(
    setup_cleanup=False,  # update the value for this option, all other options will remain untouched
    teardown_cleanup=False,
    verbose_mode=False,
    verbose_visa=False
)


# Create the DeviceManager, turning on verbosity and passing in some specific configuration values.
with DeviceManager(
    verbose=True,  # optional argument
    config_options=CONFIG_OPTIONS,  # optional argument
) as device_manager:
    # Explicitly specify to use the system VISA backend, this is the default,
    # **this code is not required** to use the system default.
    device_manager.visa_library = SYSTEM_DEFAULT_VISA_BACKEND

    # Enable resetting the devices when connecting and closing
    device_manager.setup_cleanup_enabled = True
    device_manager.teardown_cleanup_enabled = True

    # Note: USB and GPIB connections are not supported with PyVISA-py backend
    scope = device_manager.add_scope("MDO3K-C049750", connection_type="USB")
    
    #ch1 config - batt voltage
    res = scope.query("CH1:SCAle?")
    res = scope.write("CH1:SCAle 5")
    res = scope.write("CH1:POSition -3")

    #ch2 config - batt current
    scope.write("SELect:CH2 ON")
    res = scope.write("CH2:YUNits \"A\"")
    res = scope.write("CH2:INVert ON")
    res = scope.write("CH2:PRObe:GAIN 0.01")
    res = scope.write("CH2:SCAle 10")
    res = scope.write("CH2:POSition -3")

    #ch3 config - output voltage
    scope.write("SELect:CH3 ON")
    res = scope.write("CH3:PRObe:GAIN 0.001")
    res = scope.write("CH3:SCAle 100")
    res = scope.write("CH3:POSition 0")

    #ch4 config - output current
    scope.write("SELect:CH4 ON")
    res = scope.write("CH4:YUNits \"A\"")
    res = scope.write("CH4:PRObe:GAIN 0.1")
    res = scope.write("CH4:SCAle 1.5")
    res = scope.write("CH4:POSition 0")

    # time
    scope.write("HORizontal:SCAle 20e-3")



    time.sleep(2)

    with open("file.csv", "w", encoding="utf-8", newline="") as file:

        name = ['batt_volt','batt_curr', 'output_volt', 'output_curr', 'pwr_in', 'pwr_out', 'time_stamp']
        data = np.zeros(7)
        data_math = np.zeros(2)
        csv_writer = csv.writer(file)
        csv_writer.writerow(name)

        flag = 1
        time_start = time.time()
        time_pre = time_start
        time_pre_0_5 = time_start

        
        scope.write("MEASUrement:MEAS1:SOUrce1 MATH")
        scope.write("MEASUrement:MEAS1:TYPE MEAN")
        scope.write("MEASUrement:MEAS1:STATE ON")

        scope.write("SELect:MATH1 ON")
        scope.write("MATH1:AUTOSCale OFF")
        scope.write("MATH1:VERTical:POSition -3")

        scope.write("MATH1:DEFINE \"CH1 * CH2\"")
        scope.write("MATH1:VERTical:SCAle 200")


        load_start_time = time.time()
        math_cnt = 0

        while flag:
            if time.time() - time_pre > 1.0:
                time_pre += 1.0
                # ch1
                scope.write("MEASUrement:IMMed:SOUrce1 CH1")
                scope.write("MEASUrement:IMMed:TYPE MEAN")
                res = scope.query("MEASUrement:IMMed:VALue?")
                print(res)
                data[0] = res
                # res = scope.query("MEASUrement:MEAS1:VALue?")
                # print(res)

                # ch2
                scope.write("MEASUrement:IMMed:SOUrce1 CH2")
                scope.write("MEASUrement:IMMed:TYPE MEAN")
                res = scope.query("MEASUrement:IMMed:VALue?")
                print(res)
                data[1] = res
                # ch3
                scope.write("MEASUrement:IMMed:SOUrce1 CH3")
                scope.write("MEASUrement:IMMed:TYPE RMS")
                res = scope.query("MEASUrement:IMMed:VALue?")
                print(res)
                data[2] = res
                # ch4
                scope.write("MEASUrement:IMMed:SOUrce1 CH4")
                scope.write("MEASUrement:IMMed:TYPE RMS")
                res = scope.query("MEASUrement:IMMed:VALue?")               
                print(res)
                data[3] = res

                res = scope.query("MEASUrement:MEAS1:VALue?")
                if math_cnt == 0:
                    data_math[0] = res
                    scope.write("MATH1:DEFINE \"CH3 * CH4\"")
                    scope.write("MATH1:VERTical:SCAle 200")
                    math_cnt = 1
                else:
                    data_math[1] = res
                    scope.write("MATH1:DEFINE \"CH1 * CH2\"")
                    scope.write("MATH1:VERTical:SCAle 150")
                    math_cnt = 0

                data[4:6] = data_math[0:]
                data[6] = time.time() - time_start
                csv_writer.writerow(data)

                print("data print:\n", data)

                if(data[1] > 5):
                    load_flag = True
                else:
                    load_flag = False

                if load_flag == False:
                    load_start_time = time.time()
                else:
                    print(time.time() - load_start_time)



                
            time.sleep(0.1)

        
        file.close()

