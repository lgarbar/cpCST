import numpy as np


def compute_timeseries(duration_mins, refresh_dur):
    # refresh_dur = 1/refresh_rate
    duration_secs = duration_mins * 60
    # delay onset of first event by 3 refresh durations
    ts = np.arange(0, duration_secs, refresh_dur)
    # one second delay before we start moving things around
    ts += 1.0
    return ts


class CST_Model(object):
    def __init__(self):
        self.state_params = None
        self.task_params = None
        self.rev_vec = np.array([-1.0, -1.0])

    @staticmethod
    def compute_dx_dt(stim_pos, user_pos, lambda_val):
        lambda_val = lambda_val / 10
        change_rate = 0
        delta_x = stim_pos + user_pos
        change_rate = lambda_val * delta_x
        return change_rate

    @staticmethod
    def compute_distance(pos_1, pos_2):
        """Euclidian distance from point to point."""
        dist = abs(pos_1 + pos_2)
        return dist

    @staticmethod
    def peturb_distance(min_max, maxval=None):
        if isinstance(maxval, type(None)):
            p_min = min_max / 2 * -1
            p_max = min_max / 2
        else:
            p_min = min_max
            p_max = maxval

        xp = np.random.uniform(p_min, p_max)
        yp = np.random.uniform(p_min, p_max)
        return (xp, yp)

    def update_lambda_by_params(self):
        LV = self.state_params.lambda_intercept + (
            self.state_params.lambda_slope
            * self.state_params.flip_time
            / 1000  # current_ts
        )
        if LV > self.state_params.max_lambda:
            self.state_params.lambda_val = self.state_params.max_lambda
        else:
            self.state_params.lambda_val = LV

    def set_parameters(self, task_params, state_params):
        self.task_params = task_params
        self.state_params = state_params

    def update_model(self):

        user_pos = self.state_params.user_pos
        stim_pos = self.state_params.stim_pos
        lambda_val = self.state_params.lambda_val
        self.state_params.stim_to_center_dist = self.compute_distance(stim_pos, 0)
        change_rate = self.compute_dx_dt(stim_pos, user_pos, lambda_val)
        self.state_params.change_rate_x = change_rate
        new_x = self.state_params.stim_pos + change_rate
        self.update_lambda_by_params()
        self.state_params.stim_pos = new_x
