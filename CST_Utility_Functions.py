import argparse
import random
from datetime import datetime
from pathlib import Path

import numpy as np

from CST_Calculations import compute_timeseries
from CST_Data_Structures import StateValues, TaskParameters

try:
    import serial
except:
    print("serial not found. Accelerometry will not be available.")


class cst_parser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Run the crCPT")
        self.parser.add_argument(
            "--subid",
            dest="subid",
            required=True,
            help="String representing the current participant.",
        )
        self.parser.add_argument(
            "--num_cal_trials",
            dest="NUM_TEST_TRIALS",
            required=False,
            type=int,
            default=10,
            help="Number of CPT trials to calibrate Lambda_c; default=10",
        )
        self.parser.add_argument(
            "--cpt_secs_dur",
            dest="MAX_SECONDS",
            required=False,
            type=int,
            default=600,
            help="Total number of seconds (mins * 60) to run the CPT; default=420",
        )
        self.parser.add_argument(
            "--input_mode",
            dest="XY_INPUT_MODE",
            required=False,
            default="ACCEL",
            help="How are we getting X position; default='ACCEL'; options MOUSE",
        )
        self.parser.add_argument(
            "--lambda_init_value",
            dest="LAMBDA_INIT",
            required=False,
            type=float,
            default=0.100,
            help="Initial Lambda value for CST calibration; default=0.100",
        )
        self.parser.add_argument(
            "--cpt_prop_of_max",
            dest="CPT_PROP_OF_MAX",
            required=False,
            type=float,
            default=0.3,
            help="Proportion of max lambda at which to cap the CPT; default=0.3",
        )
        self.parser.add_argument(
            "--portAddress",
            dest="portAddress",
            required=False,
            type=int,
            default=0,
            help="EEG Port Address",
        )
        self.parser.add_argument(
            "--task_refresh_hz",
            dest="loop_hz",
            required=False,
            type=float,
            default=30,
            help="Rate in Hz at which to refresh the task. Defaut=30",
        )
        self.parser.add_argument(
            "--reverse_x",
            dest="REVERSE_COORDS",
            action="store_true",
            help="Reverse standard CST mapping.",
        )
        self.parser.set_defaults(REVERSE_COORDS=False)
        self.parser.add_argument(
            "--show_score",
            dest="SHOW_SCORE",
            action="store_true",
            help="Show score during task.",
        )
        self.parser.set_defaults(SHOW_SCORE=True)
        self.parser.add_argument(
            "--eeg",
            dest="withEEG",
            action="store_true",
            help="Send EEG Markers? Default=False.",
        )
        self.parser.set_defaults(withEEG=False)
        
        self.parser.add_argument(
            "--tracker",
            dest="withEyetracker",
            action="store_true",
            help="Send Tracking? default=False.",
        )
        self.parser.set_defaults(withEyetracker=False)
        
        self.parser.add_argument(
            "--visit",
            dest="visit",
            required=True,
            type=str,
            help="Visit Name/Num",
        )
        
        self.parser.add_argument(
            "--run",
            dest="run",
            required=True,
            type=str,
            help="Run Num",
        )

    def args(self):
        arg_vals = self.parser.parse_args()
        return arg_vals


class SerialConstants2(object):
    def __init__(self):
        self.tare = str.encode(":96\n")
        self.mouse_on = str.encode(":241,1\n")
        self.mouse_off = str.encode(":241,0\n")
        self.magnetometer_off = str.encode(":109,0\n")
        self.magnetometer_on = str.encode(":109,1\n")
        self.set_light_to_red = str.encode(":238,1.0,0.25,0.25\n")
        self.set_light_to_dark_red = str.encode(":238,1.0,0.0,0.0\n")
        self.set_light_to_green = str.encode(":238,0.25,1.0,25.0\n")
        self.set_light_to_dark_green = str.encode(":238,0.0,1.0,0.0\n")
        self.set_light_to_blue = str.encode(":238,0.25,0.25,1.0\n")
        self.set_light_to_dark_blue = str.encode(":238,0.0,0.0,1.0\n")
        self.set_light_to_white = str.encode(":238,1.0,1.0,1.0\n")
        self.get_norm_all = str.encode(":32\n")
        self.get_norm_all_w_ts = str.encode(";32\n")
        self.get_norm_gyro = str.encode(":33\n")
        self.get_norm_gyro_w_ts = str.encode(";33\n")
        self.get_corr_gyro = str.encode(":38\n")
        self.get_corr_gyro_w_ts = str.encode(";38\n")

        self.get_norm_acc = str.encode(":34\n")
        self.get_norm_acc_w_ts = str.encode(";34\n")
        self.get_corr_acc = str.encode(":39\n")
        self.get_corr_acc_w_ts = str.encode(";39\n")

        self.wireless_all_corrected = str.encode(">0,37\n")
        self.wireless_norm_all = str.encode(">0,32\n")

        self.get_tared_as_quat = str.encode(":00\n")
        self.get_tared_as_euler = str.encode(":01\n")
        self.get_tared_as_rotmat = str.encode(":02\n")
        self.get_tared_as_axisangle = str.encode(":03\n")
        self.get_tared_as_twovec = str.encode(":04\n")
        self.get_tared_as_diffquat = str.encode(":05\n")
        self.get_button_state = str.encode(";250\n")
        self.get_tared_as_euler_w_ts = str.encode(";01\n")

        self.include_timestamp = str.encode(":221,2\n")

        self.set_oversample_2 = str.encode(":106,2\n")
        self.set_oversample_5 = str.encode(":106,5\n")
        self.set_oversample_10 = str.encode(":106,10\n")


def get_session_params(command_line_args, task_init_path=None, state_init_path=None):

    d = {arg: getattr(command_line_args, arg) for arg in vars(command_line_args)}
    d["XY_INPUT_MODE"] = d["XY_INPUT_MODE"].upper()
    now = datetime.now()  # current date and time
    date_time = now.strftime("%m-%d-%Y_%H-%M")
    cal_output_stem = f"/home/nkirs/Desktop/MOBI/Output/sub-{d['subid']}/ses-{d['visit']}/raw/sub-{d['subid']}_ses-{d['visit']}_task-CPTCalibrate_run-{d['run']}_events"
    cpt_output_stem = f"/home/nkirs/Desktop/MOBI/Output/sub-{d['subid']}/ses-{d['visit']}/raw/sub-{d['subid']}_ses-{d['visit']}_task-CPT_run-{d['run']}_events"
    cal_task_params = TaskParameters(task_init_path, d)
    cal_task_params.MAX_SECONDS = 600

    cal_state_params = StateValues(state_init_path)
    cpt_task_params = TaskParameters(task_init_path, d)
    cpt_state_params = StateValues(state_init_path)

    # set beginning lambda to the passed init value
    cpt_state_params.lambda_slope = cpt_task_params.LAMBDA_SLOPE_INIT
    cpt_state_params.lambda_val = d["LAMBDA_INIT"]
    cpt_state_params.lambda_intercept = d["LAMBDA_INIT"]

    cal_state_params.lambda_slope = cal_task_params.LAMBDA_SLOPE_INIT
    cal_state_params.lambda_val = d["LAMBDA_INIT"]
    cal_state_params.lambda_intercept = d["LAMBDA_INIT"]
    cpt_task_params.TASK_MODE = "CPT"

    # MoBI LSL
    mobi_dict = {}
    mobi_dict["withEEG"] = d["withEEG"]
    mobi_dict["withEyetracker"] = d["withEyetracker"]
    mobi_dict["eeg_portAddress"] = d["portAddress"]
    mobi_dict["sample_hz"] = d["loop_hz"]
    mobi_dict["UID"] = d["subid"]
    mobi_dict["display"] = None  # need to add at runtime

    params_dict = {}

    cal_task_params.TASK_LOOP_RATE = 1 / d["loop_hz"]
    cpt_task_params.TASK_LOOP_RATE = 1 / d["loop_hz"]

    cal_task_params.OUTPUT_STEM = cal_output_stem
    cpt_task_params.OUTPUT_STEM = cpt_output_stem
    cal_task_params.ONSETS = compute_timeseries(
        (cal_task_params.MAX_SECONDS + 30) / 60, cal_task_params.TASK_LOOP_RATE
    )
    cpt_task_params.ONSETS = compute_timeseries(
        (cpt_task_params.MAX_SECONDS + 30 / 60), cpt_task_params.TASK_LOOP_RATE
    )

    cal_task_params.INSTRUCTIONS = "Get Ready!"
    cpt_task_params.INSTRUCTIONS = "Get Ready!"
    params_dict["cal_task"] = cal_task_params
    params_dict["cal_state"] = cal_state_params
    params_dict["cpt_task"] = cpt_task_params
    params_dict["cpt_state"] = cpt_state_params
    params_dict["mobi_dict"] = mobi_dict

    return params_dict
