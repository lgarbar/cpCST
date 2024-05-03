import numpy as np

import warnings

from psychopy import event, parallel
from psychopy.hardware import joystick
from pygaze.eyetracker import EyeTracker

from CST_Accelerometer_01 import AccelerometerBase


class CST_User_Input(object):
    """
    Abstract class to create and poll devices for CST task input
    from available options. E.g. keyboard, mouse/trackpad, joystick,
    trackball, motion capture / accellerometer, etc. are all
    conceivable use cases for CST inputs.

    Given a string description, it attempts to create the requested
    input object and passes the object-specific polling function to
    the appropriate self.get_xy_position or self.get_press_response
    method(s), which can then be called without worrying about the
    implemetation details.

    Inputs:
        None: Configure object through the 'connect_*' methods
              after instantiation.

    Parameters/properties:
        xy_input_mode     : string name of xy input object mode
                            (e.g. "ACCEL" or "MOUSE")
        press_input_mode  : string name of button-press input object mode
                            (e.g. "KB" or "BUTTON_PAD")

        Note: Retreive XY and response values through 'get_*' methods

    Methods:
        connect_press_object(str, window)
            str = string name of device
            window = psychopy window instance from cst_view
        connect_xy_object(str, window, reverse_coords, swap_axes)
            str = string name of device
            window = psychopy window instance (e.g. from cst_view)
            reverse_coords = make L=R and U=D (Default =False)
            swap_axes = swap X and Y inputs (Default = False)
        get_xy_position()
        get_press_response()

    """

    def __init__(self):
        """
        Functions that the CST controller must support. Initialize here
        with placeholder null values. On connect methods, below, we will
        assign functions appropriate to the device hardware we are conecting.
        """
        self.xy_input_mode = None
        self.press_input_mode = None

        self.__xy_input_object = None
        self.__press_input_object = None

        self.get_xy_position = None
        self.get_press_response = None

        self.reset_xy_position = None

        self.shutdown = None

    def connect_press_object(self, press_input, window):
        # python 3.10 will have switch/case statements; yay...
        self.press_input_mode = press_input.upper()
        if self.press_input_mode == "KB":
            self.__press_input_object = event.getKeys
            # self.__press_object = event.getKeys #keyboard.Keyboard()
            self.get_press_response = self.__get_kb_response  # passing func
        elif self.press_input_mode == "BUTTON_PAD":
            # self.press_object = "Get the BUTTON_PAD object"
            self.get_press_response = self.__get_pad_response  # passing func
        elif self.press_input_mode == "JOYSTICK":
            self.get_press_response = self.__get_joystick_response  # passing func

        # else:
        #     raise ValueError(f"Device {press_input} not supported.")

    def connect_xy_object(
        self, xy_input, window, reverse_coords=False, swap_axes=False
    ):
        """
        General function to configure XY inputs
        Assigns function pointers to the dataio object, abstracting
        implementation details away from the rest of the code. Your
        ViewModel shouldn't have to care if you are using a joystick,
        trackball, mouse, accelerometer, etc.
        """
        # python 3.10 will have switch/case statements; yay...
        print(f"received reverse_coords={reverse_coords}\n")
        self.xy_input_mode = xy_input.upper()
        if self.xy_input_mode == "MOUSE":
            self.__xy_input_object = event.Mouse(visible=True, win=window)
            if reverse_coords is True:
                self.get_xy_position = self.__get_mouse_position_rev
            else:
                self.get_xy_position = self.__get_mouse_position
            self.reset_xy_position = self.__reset_mouse_position

        elif self.xy_input_mode == "ACCEL":
            accel = AccelerometerBase()
            accel.connect_to_wired(mount_point="search")
            self.poll_and_update = accel.poll_and_update
            self.poll_and_update()
            self.get_these_values = accel.getPos()
            #self.shutdown = accel.shutdown()
            x, y = accel.getPos()
            self.__xy_input_object = accel
            if reverse_coords is True:
                if swap_axes is True:
                    self.get_xy_position = self.__get_acc_position_rev_swapaxes
                else:
                    self.get_xy_position = self.__get_acc_position_rev
            else:
                if swap_axes is True:
                    self.get_xy_position = self.__get_acc_position_swapaxes
                else:
                    self.get_xy_position = self.__get_acc_position

            self.reset_xy_position = self.__reset_acc_position  # func

        elif self.xy_input_mode == "BUTTON_PAD":
            # self.__xy_input_object = ButtonXY()
            self.get_xy_position = self.__get_button_xy
            self.reset_xy_position = self.__reset_button_xy

        elif self.xy_input_mode == "JOYSTICK":
            # self.__xy_input_object = PST_Joystick()
            self.get_xy_position = self.__get_joystick_xy  # passing func
            self.reset_xy_position = self.__pass_function  # func

    def set_joystick(self):
        nJoys = joystick.getNumJoysticks()  # to check if we have any
        joystick_id = nJoys - 1
        joy = joystick.Joystick(joystick_id)
        return joy

    def __get_joystick_xy(self):
        """Returns current X,Y position as list."""
        [x, y] = self.__xy_input_object.get_xy_position()
        return [x, y]

    def __get_joystick_response(self):
        state = self.__xy_input_object.get_button_state()
        return state

    def __get_kb_response(self):
        """Returns psychopy keyboard events."""
        return self.__press_input_object()

    def __get_pad_response(self):
        print("got a value from thparallele RESPONSE PAD")

    def __get_mouse_position(self):
        """Returns current X,Y position as list."""
        pos = self.__xy_input_object.getPos()
        x, y = (np.array(pos) / 1000) + 0.864
        return [x, y]

    def __get_mouse_position_rev(self):
        """Returns current X,Y position as tuple."""
        pos = self.__xy_input_object.getPos()
        pos = (np.array(pos) / 1000) + 0.864
        return pos * -1

    def __reset_mouse_position(self, newPos=0):
        self.__xy_input_object.setPos(newPos=newPos)

    def __get_acc_position(self):
        """Returns current X,Y position as tuple."""
        return self.__xy_input_object.getPos()

    def __get_acc_position_rev(self):
        """Returns current X,Y position as tuple."""
        pos = self.__xy_input_object.getPos()
        pos = np.array(pos) * -1
        return pos

    def __get_acc_position_swapaxes(self):
        """Returns current X,Y position as tuple."""
        pos = self.__xy_input_object.getPos()
        pos = np.flip(np.array(pos))
        return pos

    def __get_acc_position_rev_swapaxes(self):
        """Returns current X,Y position as tuple."""
        pos = self.__xy_input_object.getPos()
        pos = np.flip(np.array(pos) * -1)
        return pos

    def __reset_acc_position(self, newPos=(0, 0)):
        self.__xy_input_object.setPos(newPos=(newPos))

    def __get_button_xy(self):
        x, y = self.__xy_input_object.get_xy_position()
        return np.array([x, y])

    def __reset_button_xy(self, reset_loc=(0, 0)):
        self.__xy_input_object.reset_state(reset_loc)

    def __pass_function(self):
        pass


class null_dev(object):
    """Null object to take args meant for MoBI devices that
    are not available or necessary (e.g. testing outside MoBI)
    but still allows the code to run, while warning the user."""

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            print(f"{name}() was called, but no device was available")

        return wrapper


class MoBI_Devices(object):
    """Writing single object for all MoBI devices we will connect."""

    def __init__(
        self,
        params_dict={
            "withEEG": True,
            "eeg_portAddress": "/dev/parport0",
            "withEyetracker": False,
            "display": None,
            "num_channels": 6,
            "sample_hz": 30,
            "UID": "rs2_12345",
        },
    ):
        # create a default null device.
        # handles all missing device calls
        self.null_dev = null_dev()
        try:
            # if lsltools available grab the reference
            import stimlsltools as slt
            from pylsl import StreamInfo, StreamOutlet

            self.slt = slt
            info = StreamInfo(
                "cpCST",
                "task_params",
                params_dict["num_channels"],
                params_dict["sample_hz"],
                "float32",
                params_dict["UID"],
            )

            chns = info.desc().append_child("channels")
            for c in params_dict["channel_info"].keys():
                ch = chns.append_child("channel")
                ch.append_child_value("label", c)
                ch.append_child_value("unit", params_dict["channel_info"][c])
                ch.append_child_value("type", "crCPT")

            info.desc().append_child_value("manufacturer", "SJC")
            info.desc().append_child_value("system", "NKI_MoBI")

            self.lsl_outlet = StreamOutlet(info)

        except ModuleNotFoundError:
            # if not, pass a null function so that
            # the code can run.
            self.hasLSL = False
            self.slt = self.null_dev
            self.lsl_outlet = self.null_dev
            warnings.warn(
                "Error Loading LSL. Lab Streaming Layer will not be available."
            )

        if params_dict["withEEG"] is True:
            try:
                print(params_dict["eeg_portAddress"])
                self.eeg = parallel.ParallelPort(address=params_dict["eeg_portAddress"])
            except ValueError:
                self.eeg = self.null_dev
                warnings.warn(
                    f"EEG not connected!\nData will not be sent to EEG port {params_dict['eeg_portAddress']}."
                )
        else:
            self.eeg = self.null_dev

        if params_dict["withEyetracker"] is True:
            try:
                self.eyetracker = EyeTracker(
                    params_dict["display"],
                    trackertype="eyelink",
                    logfile=params_dict["UID"],
                )
            except:
                self.eyetracker = self.null_dev
                warnings.warn(
                    f"Eyetracker not connected!\nData will not be sent to eyetracker on {params_dict['display']}."
                )
        else:
            self.eyetracker = self.null_dev

        self.is_configured = True


class CST_Device_IO(object):
    """
    Abstract class to link CST task with external devices, e.g.
    TMS, tDCS, MRI Scanner, EEG system, tactors, audio, etc.

    Separate from User Input objects as a conceptual distinction.
    Could easily wrap both into a single object. But even in the
    case of tactile or aural feedback to the subect, I think that
    the separation makes sense.

    Given a string description, it attempts to connect to the
    external device and sets the object-specific interface to
    the appropriate self.send_* or self.get_* method(s).

    Inputs:
        None: Configure object through the 'connect_*' methods
              after instantiation.

    Parameters/properties:
        device_name: string name of the external device

    Methods:
        connect_device(str)
        send_message(msg, **kwargs)
        get_data(**kwargs)

    Note: might make sense, if the device interfaces get to be
    very many, and/or large and complicated, to split out the
    device interfaces and import them selectively.
    """

    def __init__(self):

        self.device_name = None
        self.__device_object = None

        self.send_message = None
        self.get_data = None

    def connect_device(self, device_name, **kwargs):
        # Match device_name string to object methods
        # and send any kwargs for configuration.
        pass

    def send_message(self, msg, **kwargs):
        # send msg and kwargs to connected device (whatever it is)
        pass

    def get_data(self, **kwargs):
        # get data from connected device (whatever it is); kwargs to
        # send options (#bytes, etc, etc.)
        pass

