import numpy as np
import serial
from psychopy import core, event
from CST_DataIO_pygaze import CST_User_Input
from CST_Utility_Functions import SerialConstants2
from CST_ViewPygaze import View
from pygaze.libscreen import Display, Screen
import pygaze


class ViewModel(object):
    """Logic and objects to render user interface."""

    def __init__(self, **kwargs):
        self.is_MRI = False
        self.task_params = None
        self.state_params = None
        self.clock = core.Clock()
        self.stim_default_color = [-0.25, -0.25, 0.75]
        self.stim_highlight_color = [0.2, 1.0, 0.2]
        self.outer_stim_default_color = [-0.25, -0.25, 0.75]
        self.stim_highlight_color = [0.2, 1.0, 0.2]
        self.outer_stim_highlight_color = [1.0, 0.7, 0.4]
        self.serial_constants = SerialConstants2()
        self.score_width = 0.15
        self.disp = Display(
            disptype="psychopy",
            bgc=(125, 125, 125),
            dispsize=([1024, 768]),
            fullscr=True,
        )
        self.scr = Screen(disptype="psychopy", bgc=(125, 125, 125))
        self.cst_view = View(pygaze.expdisplay)

    def update_score(self):
        if abs(self.state_params.stim_pos) < self.cst_view.outer_stim.radius:
            self.state_params.current_score += self.task_params.TASK_LOOP_RATE * 1.25

    def set_parameters(self, task_params, state_params):
        self.task_params = task_params
        self.state_params = state_params

        self.cst_user_input = CST_User_Input()

        self.cst_user_input.connect_press_object(
            self.task_params.PRESS_INPUT_MODE, pygaze.expdisplay
        )

        self.cst_user_input.connect_xy_object(
            xy_input=self.task_params.XY_INPUT_MODE,
            window=pygaze.expdisplay,
            reverse_coords=self.task_params.REVERSE_COORDS,
            swap_axes=self.task_params.SWAP_AXES,
        )

    def update_text_boxes(self):
        """Updates values in the text displays"""
        self.update_score()
        self.cst_view.score_display.setText(
            f"Score:{int(self.state_params.current_score)}"
        )
        self.cst_view.lambda_display.setText(
            f"Lambda: {int(self.state_params.lambda_val*1000)}"
        )
        self.cst_view.time_display.setText(f"Time: {self.state_params.flip_time:3.1f}")

    def update_stim_properties(self):

        if self.state_params.stim_to_center_dist < self.cst_view.stim.radius:
            # if S is keeping it inside the smaller circle
            self.cst_view.stim.fillColor = self.stim_highlight_color
            self.cst_view.stim.opacity = 0.5
            self.cst_view.outer_stim.fillColor = self.outer_stim_default_color
            self.cst_view.outer_stim.opacity = 0.5

        elif self.state_params.stim_to_center_dist < self.cst_view.outer_stim.radius:
            # if within outer circle, but not inner:
            self.cst_view.outer_stim.fillColor = self.outer_stim_highlight_color
            self.cst_view.outer_stim.opacity = 0.5
            self.cst_view.stim.fillColor = self.stim_default_color
            self.cst_view.stim.opacity = 1
        else:
            self.cst_view.outer_stim.fillColor = self.outer_stim_default_color
            self.cst_view.outer_stim.opacity = 1
            self.cst_view.stim.fillColor = self.stim_default_color
            self.cst_view.stim.opacity = 1

    def draw_text_boxes(self):
        self.scr.screen.append(self.cst_view.score_display)
        self.scr.screen.append(self.cst_view.lambda_display)
        self.scr.screen.append(self.cst_view.time_display)

    def draw_stimuli(self):
        self.scr.screen.append(self.cst_view.outer_stim)
        self.scr.screen.append(self.cst_view.stim)

    def draw_background(self):
        self.scr.screen.append(self.cst_view.left_bounds)
        self.scr.screen.append(self.cst_view.right_bounds)
        self.scr.screen.append(self.cst_view.fix)

    def draw_stim_screen(self):
        """Draws the screen objects."""
        # update stimulus position
        self.cst_view.outer_stim.pos = self.cst_view.stim.pos = [
            self.state_params.stim_pos,
            0,
        ]
        self.draw_background()
        self.update_text_boxes()
        self.draw_text_boxes()
        self.update_stim_properties()
        self.draw_stimuli()

    def draw_error_screen(self):
        self.scr.clear()
        self.draw_stim_screen()
        self.scr.screen.append(self.cst_view.crash_label)
        self.disp.fill(screen=self.scr)
        self.disp.show()

        core.wait(1.5)
        self.scr.clear()
        self.draw_stim_screen()
        self.disp.fill(screen=self.scr)
        self.disp.show()

    def initialize_stim(self):
        """Bring moving parts back to their starting point
        and set lambda to 50% of escape value."""

        # induce slow drift randomly to left or right.
        d = np.random.randint(0, 2, 1)
        if d:
            direction = -1
        else:
            direction = 1

        reset_pos = [0.005 * direction, 0.0]

        self.cst_view.outer_stim.pos = self.cst_view.stim.pos = reset_pos
        self.state_params.stim_pos = reset_pos[0]
        self.scr.clear()
        self.draw_stim_screen()
        self.scr.screen.append(self.cst_view.reset_label)
        self.cst_user_input.reset_xy_position()
        self.state_params.user_pos = 0.0
        event.Mouse(visible=False)
        self.disp.fill(screen=self.scr)
        self.disp.show()

    def reset_stim(self):
        """Bring moving parts back to their starting point
        and set lambda to 50% of escape value."""

        # induce slow drift randomly to left or right.
        d = np.random.randint(0, 2, 1)
        if d:
            direction = -1
        else:
            direction = 1

        reset_pos = [0.005 * direction, 0.0]

        self.cst_view.outer_stim.pos = self.cst_view.stim.pos = reset_pos
        self.state_params.stim_pos = reset_pos[0]
        self.state_params.user_pos = 0.0

        self.scr.clear()
        self.draw_stim_screen()
        self.scr.screen.append(self.cst_view.reset_label)
        self.disp.fill(screen=self.scr)
        self.disp.show()

        core.wait(1)

        self.draw_stim_screen()
        self.disp.fill(screen=self.scr)
        self.cst_user_input.reset_xy_position()

    def wait_for_pulse(self, pulse_key="T"):
        ser = serial.Serial("/dev/ttyUSB0", 19200, timeout=30)
        ser.flushInput()
        x = ""
        while x != pulse_key:
            x = ser.read().decode()
        ser.close()

    def show_instructions(self, message_str="Get Ready"):

        self.cst_view.instruction_display.setText(message_str)
        self.cst_view.instruction_display.size = 0.5
        self.scr.screen.append(self.cst_view.instruction_display)
        self.disp.fill(screen=self.scr)
        self.disp.show()

        if self.is_MRI is True:
            self.wait_for_pulse()
        else:
            event.waitKeys(keyList=["space"])

        self.disp.fill(screen=self.scr)
        self.disp.show()

    def handle_key_events(self, response):
        if "escape" in response:
            self.state_params.stop_run = True

    def update_and_flip_at(self, exp_clock, at_time):
        """
        Draw stimulus view with passed params.
        Flip screen at a specific time.
        """
        if self.state_params.is_OOB is True:
            start_pause = exp_clock.getTime()
            self.state_params.did_crash = True
            self.draw_error_screen()
            self.reset_stim()
            self.state_params.is_OOB = False
            end_pause = exp_clock.getTime()
            elapsed_time = end_pause - start_pause
            # account for reset time in future onsets
            self.task_params.ONSETS += elapsed_time
            # and for current trial.
            at_time += elapsed_time

        self.scr.clear()
        # self.update_score()
        # self.update_text_boxes()
        response = event.getKeys()
        self.handle_key_events(response)
        self.draw_stim_screen()
        self.disp.fill(screen=self.scr)
        wait_time = at_time - exp_clock.getTime()
        core.wait(wait_time)
        self.disp.show()

        flip_time = exp_clock.getTime()

        return flip_time
