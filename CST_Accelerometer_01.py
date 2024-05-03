import time
import numpy as np
import serial
from CST_Utility_Functions import SerialConstants2


class AccelerometerBase(object):
    def __init__(self):
        self.ser = None
        self.consts = SerialConstants2()
        self.orient = []
    def connect_to_wired(
        self, mount_point="search", baud_rate=19200, timeout=1, include_timestamp=True
    ):
        if mount_point == "search":
            import glob
            import platform

            os_type = platform.system()
            if "Linux" in os_type:
                match_str = "/dev/ttyACM*"
            elif "Darwin" in os_type:
                match_str = "/dev/tty.usbmodem*"
            else:
                try:
                    raise ValueError(
                        f"Mount point 'search' not currently supported under {os_type}.\nPlease specify device address manually."
                    )
                except ValueError as err:
                    print(err.args)

            matches = glob.glob(match_str)

            for m in matches:
                try:
                    self.ser = serial.Serial(m, baud_rate, timeout=timeout)
                    print(f"dev: {m} connected")
                    break
                except:
                    print(f"dev: {m} did not connect")
        else:
            self.ser = serial.Serial(mount_point, baud_rate, timeout=timeout)

        # if include_timestamp is True:
        #     time.sleep(0.1)  # give it a bit to collect itself
        #     self.ser.write(str.encode(":221,2\n"))
        #     self.reset_state()

    def send_and_return(self, request, astype=int):
        self.ser.write(request)
        self.ser.flush()  # make sure write is done
        val = self.ser.readline().decode().split("\r")[0]
        return np.array(val.split(",")).astype(astype)

    def setPos(self, newPos=0.0):
        self.ser.write(self.consts.tare)

    def re_center(self):
        self.ser.write(self.consts.tare)

    def reset_state(self):
        self.reset_timestamp_value = self.send_and_return(
            self.consts.get_button_state, astype=int
        )[0]
        self.re_center()

    def get_xy_position(self):
        return self.getPos()

    def getPos(self):
        return self.send_and_return(self.consts.get_tared_as_euler, astype=float)[0:3:2]

    def poll_and_update(self):
        """basic update for tared orientation. Can override/extend in subclass"""
        self.orient = self.send_and_return(
            self.consts.get_tared_as_euler_w_ts, astype=float
        )

    def shutdown(self):
        try:
            self.ser.write(self.consts.set_light_to_green)
            self.ser.close()
        except:
            print("Accel object (probably) already closed")

