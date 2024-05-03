from datetime import datetime
import numpy as np
import pandas as pd
from psychopy import core
from CST_Calculations import CST_Model
from CST_ViewModelPygaze import ViewModel
from CST_DataIO_pygaze import MoBI_Devices


class StateMachine(object):
    """
    This class drives the task by updating timestamps
    in the state_params and advancing the CST_Model on a
    set of fixed time points to prevent timing drift.
    The CST_Model updates the state_params. Then the
    statemachine tells the ViewModel to update. The
    viewmodel has its own logic for what to do with the
    updated state_params, and implements them in its own
    View, which we can make to be just about anything.
    IO is through the abstracted CST_DataIO
    class. Maybe a bit much, but I wanted to make it as
    flexible as possible.
    """

    def __init__(self, **kwargs):
        self.view_model = ViewModel()
        self.cst_model = CST_Model()
        self.exp_timer = core.Clock()
        self.mobi_dev = None
        self.lambda_c_vals = []

        self.log_data = []
        self.logged_values = [
            "expected_time",
            "flip_time",
            "stim_pos",
            "user_pos",
            "crash_count",
            "lambda_val",
            "change_rate_x",
            "did_crash",
            "lambda_slope",
        ]
        self.logged_units = [
            "seconds",
            "seconds",
            "arbitrary_distance",
            "arbitrary_distance",
            "integer_count",
            "units_per_second",
            "units_per_second",
            "binary_state",
            "units_per_second",
        ]

        self.params_are_set = False

    def set_parameters(self, task_params, state_params, mobi_dict):
        self.task_params = task_params
        self.state_params = state_params
        self.view_model.set_parameters(self.task_params, self.state_params)
        self.cst_model.set_parameters(self.task_params, self.state_params)
        ## MoBI LSL
        # Update mobi_dict with runtime info
        mobi_dict["display"] = self.view_model.disp
        mobi_dict["num_channels"] = len(
            self.logged_values
        )  # create a slot for each logged value

        mobi_dict["channel_info"] = dict(zip(self.logged_values, self.logged_units))

        self.mobi_dev = MoBI_Devices(mobi_dict)

        self.state_params.crash_count = 0

        self.params_are_set = True

    def show_instructions(self, message_str=None):
        self.view_model.show_instructions(message_str=message_str)

    def update_log(self):
        vals = self.state_params.get_these_values(self.logged_values)
        self.state_params.did_crash = False
        self.log_data.append(vals)

    def write_log(self):
        x = self.task_params.OUTPUT_STEM
        x = x.split("_")
        if x[3] == "CPT":
            x[3] = "MAIN"
        else:
            x[3] == "CALIB"
        outname = f"{self.task_params.OUTPUT_STEM}.csv"
        df = pd.DataFrame(columns=self.logged_values, data=self.log_data)
        now = datetime.now()  # current date and time
        date_time = now.strftime("%m/%d/%Y,%H:%M:%S")
        df["datetime_ended"] = date_time
        df.to_csv(outname, index=False)

    def write_out_lambdas(self):
        now = datetime.now()  # current date and time
        date_time = now.strftime("%m/%d/%Y,%H:%M:%S")
        lambda_c_vals = np.array(self.lambda_c_vals)
        lambda_c_str = ",".join(lambda_c_vals.astype(str))
        params = self.task_params.OUTPUT_STEM.split("_")[2:]
        params_str = ",".join(params)
        save_str = f"{self.task_params.subid},{params_str},{date_time},{lambda_c_str}\n"
        with open("calibration_lambdas.csv", "a") as f:
            f.writelines(save_str)

    def mobi_send_started(self):
        self.mobi_dev.slt.pushToStreamLabel(f"Onset {self.task_params.TASK_MODE}")
        self.mobi_dev.eeg.setData(255)
        self.mobi_dev.eyetracker.log(f"Onset {self.task_params.TASK_MODE}")
        self.mobi_dev.eyetracker.status_msg(f"Running:{self.task_params.TASK_MODE}")

    def mobi_send_crashed(self, at_time, vals):
        self.mobi_dev.slt.pushToStreamLabel(f"Crashed {vals}")
        self.mobi_dev.eeg.setData(128)
        self.mobi_dev.lsl_outlet.push_sample(vals)
        self.mobi_dev.eyetracker.log(f"Crashed:{at_time}")
        self.mobi_dev.eyetracker.status_msg(f"Crashed:{at_time}")

    def mobi_close_devices(self):
        self.mobi_dev.slt.pushToStreamLabel(f"TaskEnded {self.task_params.TASK_MODE}")
        self.mobi_dev.eeg.setData(255)
        self.mobi_dev.eyetracker.log(f"TaskEnded {self.task_params.TASK_MODE}")
        self.mobi_dev.eyetracker.status_msg(f"Closing:{self.task_params.TASK_MODE}")
        self.mobi_dev.eyetracker.stop_recording()
        self.mobi_dev.eyetracker.close()
        self.mobi_dev.eeg.__del__()

    def mobi_update_vals(self, vals):
        self.mobi_dev.lsl_outlet.push_sample(vals)
        self.mobi_dev.eeg.setData(0)

    def run(self):
        if self.params_are_set is True:
            self.state_params.stop_run = False
            self.state_params.current_score = 0
            trial_num = 0

            #self.show_instructions("Before we begin, we will calibrate the eyetracker")

            #self.mobi_dev.eyetracker.calibrate()
            #self.show_instructions("Great Job!")

            #self.mobi_dev.eyetracker.start_recording()

            # use window flip in view_model to synch
            # onset timing to VBL
            self.view_model.initialize_stim()
            self.exp_timer.reset()
            self.mobi_send_started()
            for t in self.task_params.ONSETS:
                self.state_params.current_trial = trial_num
                (
                    self.state_params.user_pos,
                    _,
                ) = self.view_model.cst_user_input.get_xy_position()

                if self.state_params.stim_to_center_dist > self.task_params.MAX_BOUNDS:
                    self.state_params.is_OOB = True
                    ## MoBI Devices
                    # pulling list of values from params object and sending to mobi_send_crashed
                    self.mobi_send_crashed(
                        at_time=self.state_params.flip_time,
                        vals=self.state_params.get_these_values(self.logged_values),
                    )
                    self.lambda_c_vals.append(self.state_params.lambda_val)
                    scale_val = self.task_params.SCALE_VALS[
                        self.state_params.crash_count
                    ]
                    self.state_params.lambda_intercept -= (
                        scale_val * self.state_params.lambda_val
                    )

                    self.state_params.lambda_slope *= 0.95
                    self.state_params.crash_count += 1

                else:
                    ## MoBI Devices
                    # pulling list of values from params object and sending to mobi_update
                    self.mobi_update_vals(
                        self.state_params.get_these_values(self.logged_values)
                    )
                if np.logical_and(
                    self.state_params.crash_count >= self.task_params.NUM_TEST_TRIALS,
                    self.task_params.TASK_MODE == "CALIBRATE",
                ):
                    self.state_params.stop_run = True

                self.state_params.expected_time = t
                flip_time = self.view_model.update_and_flip_at(
                    self.exp_timer, t - 0.005
                )
                self.state_params.flip_time = flip_time

                self.update_log()
                self.cst_model.update_model()

                if self.state_params.flip_time >= self.task_params.MAX_SECONDS:
                    self.state_params.stop_run = True

                if self.state_params.stop_run is True:
                    self.update_log()
                    self.write_log()
                    self.mobi_close_devices()
                    if self.task_params.TASK_MODE == "CALIBRATE":
                        self.write_out_lambdas()
                    self.view_model.show_instructions("Great Job!")
                    return self.lambda_c_vals
                trial_num += 1
        else:
            raise ValueError(
                "\nERROR:\nTask and state parameters must be set before running\n"
            )
            print("exited for loop in run")
            self.write_log()
            return self.lambda_c_vals
