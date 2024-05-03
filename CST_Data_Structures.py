from CST_Supports import Parameters


class DualTaskData(Parameters):
    def __init__(self, init_file=None, values_dict=None):
        self.trial_num = 0
        self.timestamp = 0
        self.stim_onset = 0
        self.stim_offset = 0
        self.stim_type = 0
        self.space_rt = 0
        self.secondary_rt = 0
        self.secondary_key = "x"
        self.score = 0
        self.lambda_val = 0
        self.has_space = False
        self.secondary_trial_num = 0
        self.response_code = 0  # 0=error, 1=correct, -1=fa, -2=miss?

        self.secondary_response_complete = False

        if init_file is not None:
            self.load_parameters(init_file)

        if values_dict is not None:
            self.__dict__.update(values_dict)


class AccelValues(Parameters):
    def __init__(self, init_file=None, values_dict=None):
        """
        Parameters subclass to hold all accelerometry state data.
        Values:
            .init_time = device timestamp when initialized

            .g* = gyroscope in rads/sec
            .a* = accelerometry in g
            .m* = magnetometer; typically disabled in orient calcs

            .o* = orientation in Euler angles

            .button_value = button value at time of polling
            .button_rt = time between last clock reset and button event
            .button_timestamp = abs clock value at time of button event
        Methods:
            .update_*() = takes list *in correct order* for each of the
                        accel, orient, and button vec/vals and stores
                        them in object's dictionary
            .get_these_values() takes list of parameter names and returns
                        a list containing the corresponding parameter values
                        in that order. Passing["ox","button_value","button_rt"]
                        returns just those values
            .as_dict() returns all stored values including param_desc
                        string as a dictionary.
            .print_values() Writes formatted values dictionary to stdio
        """
        self.param_desc = "accelerometry values"
        self.init_time = 0

        self.gx = 0
        self.gy = 0
        self.gz = 0
        self.ax = 0
        self.ay = 0
        self.az = 0
        self.mx = 0
        self.my = 0
        self.mz = 0

        self.ox = 0
        self.oy = 0
        self.oz = 0

        self.button_value = 0
        self.button_rt = 0
        self.button_timestamp = 0

        self.__stored_gyro = ["gx", "gy", "gz"]

        self.__stored_accel = ["ax", "ay", "az"]

        self.__stored_compass = ["mx", "my", "mz"]

        self.__stored_orient = ["timestamp", "ox", "oy", "oz"]

        self.__stored_button = ["button_value", "button_rt", "button_timestamp"]

        if init_file is not None:
            self.load_parameters(init_file)

        if values_dict is not None:
            self.__dict__.update(values_dict)

    def update_accel_vec(self, vals):
        d = dict(zip(self.__stored_accel, vals))
        self.__dict__.update(d)

    def update_gyro_vec(self, vals):
        d = dict(zip(self.__stored_gyro, vals))
        self.__dict__.update(d)

    def update_orient_vec(self, vals):
        d = dict(zip(self.__stored_orient, vals))
        self.__dict__.update(d)

    def update_button_vals(self, vals):
        d = dict(zip(self.__stored_button, vals))
        self.__dict__.update(d)

    def vals_as_string(self):
        v = self.as_dict().values()
        val_str = ",".join([str(c) for c in list(v)[1:]])
        return val_str


class TaskParameters(Parameters):
    def __init__(self, init_file=None, values_dict=None):
        """
        Modified subclass to allow arguments for an initialization file
        (input from JSON dictionary stored on disk), as well as
        setting values from from a passed dictionary.
        Order of variable assignment:
            1. defaults coded into object
            2. values in 'init_file' JSON dictionary
            3. values passed in 'values_dict'
        * Note that the last value assigned will the the value returned
        In steps 2 and 3, variables explicitly assigned will overwrite
        previous values. All other variables will remain untouched.
        This allows relatvively fine and flexible control of the task
        at runtime while relying largely on preset and saved values.
        """
        # TODO: Make this part of the parent class?
        # Set some basic params to reasonable values.
        self.param_desc = "Task Parameters"
        self.OUTPUT_STEM = ""
        self.SUBID = ""
        self.TASK_LOOP_RATE = 1 / 30
        self.TASK_SAMPLE_HZ = 30
        self.LAMBDA_INIT = 0.125
        self.NOISE_LEVEL = 0.0075
        self.LAMBDA_SLOPE_INIT = 20

        self.MAX_BOUNDS = 0.8
        self.TRACKING_DIMS = 1

        self.TASK_MODE = "CALIBRATE"

        self.XY_INPUT_MODE = "MOUSE"
        self.PRESS_INPUT_MODE = "KB"
        self.MOVING_TARGET = False
        self.TARGET_TRAJECTORY = "STATIC"

        self.NUM_TEST_TRIALS = 10

        self.MAX_SECONDS = 600  # 10 mins
        self.USE_TIME_OFF_TARGET = False

        self.CPT_PROP_OF_MAX = 0.5

        self.SHOW_FIXATION = True
        self.SHOW_SCORE = True

        self.SWAP_AXES = False
        self.REVERSE_COORDS = False

        self.ONSETS = []
        self.SCALE_VALS = [
            0.5,
            0.5,
            0.4,
            0.4,
            0.3,
            0.3,
            0.2,
            0.2,
            0.2,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
        ]
        if init_file is not None:
            self.load_parameters(init_file)

        if values_dict is not None:
            self.__dict__.update(values_dict)


class StateValues(Parameters):
    """
    Subclassed params to hold/pass state info.
    The only value that really needs to be initialized
    might lambda_val (to set the value the system starts with)
    and max_lambda (to cap the value, e.g. during CPT)
    """

    def __init__(self, init_file=None, values_dict=None):
        self.param_desc = "State Parameters"
        self.current_ts = 0.0
        self.current_trial = 0
        self.current_letter = 0
        self.current_block = 0
        self.current_alpha = 0
        self.user_id = "rs2_12345"
        self.stim_pos = 0.0  # The moving disk thingy
        self.user_pos = 0.0  # The mouse/joystick, etc. position
        self.target_pos = [0.0, 0.0]  # Where we are trying to get the stimulus
        self.stim_to_center_dist = 0.0

        self.is_OOB = False

        self.max_lambda = 10  # or some unrealistic value
        self.lambda_val = 0.125
        self.current_score = 0
        self.bonus_mult = 1
        self.last_crash_time = 0
        self.lambda_intercept = 0
        self.lambda_slope = 15

        self.change_rate_x = 0
        self.is_off_target = False

        self.crash_count = 0

        self.expected_time = 0.0
        self.flip_time = 0.0

        self.stop_run = False
        self.did_crash = False

        self.response_value = 0

        if init_file is not None:
            self.load_parameters(init_file)

        if values_dict is not None:
            self.__dict__.update(values_dict)
