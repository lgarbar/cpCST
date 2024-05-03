import numpy as np
from psychopy import event
from CST_StateMachine import StateMachine
from CST_Utility_Functions import SerialConstants2, cst_parser, get_session_params

args = cst_parser()
ser_consts = SerialConstants2()

# Initialize task with appropriate info
TPV = get_session_params(args.args(), task_init_path="1D_CPT_static_accel.par")
# TPV["cal_task"].TASK_MODE = "CALIBRATE"

practice_task = StateMachine()

TPV["cpt_state"].max_lambda = 0.05
TPV["cpt_state"].lambda_val = 0.01
TPV["cpt_task"].TASK_MODE = "PRACTICE"
practice_task.set_parameters(TPV["cpt_task"], TPV["cpt_state"], TPV["mobi_dict"])

inst = []
inst.append(
    """Next activity starting soon"""
)

inst.append(
    """In this task, you will be asked to control
a circle on the screen using this 
device."""
)

inst.append(
    """The circle will drift to the left or right.
Your job will be to keep it at the center 
of the screen by tilting the device in 
the opposite direction."""
)

inst.append(
    """Before we start the task, we will  give you a 
chance to practice."""
)

for k in range(len(inst)):
    practice_task.show_instructions(message_str=inst[k])


_ = practice_task.run()

inst = []
inst.append(
    """This part of the task will start out just like the 
practice session. But it will become harder to keep 
the circle in the middle of the screen."""
)
inst.append(
    """You will eventually lose control and 'crash'. 
This is OK. In this part of the task, we want 
to see how long you can keep the circle on the screen."""
)
inst.append(
    """Just do your best, and keep the circle on the screen
for as long as you can.
"""
)

for k in range(len(inst)):
    practice_task.show_instructions(message_str=inst[k])


cst_task = StateMachine()
# set parameters
TPV["cal_task"].TASK_MODE = "CALIBRATE"
TPV["cpt_state"].lambda_val = 0.1
TPV["cpt_state"].lambda_intercept = 0.1

cst_task.set_parameters(TPV["cal_task"], TPV["cal_state"], TPV["mobi_dict"])

# cst_task.show_instructions(
#     message_str="""Great! We will now continue on to the task."""
# )

# run the task, returning array of lambda_c
lambda_c_values = cst_task.run()
lambda_c_values = np.array(lambda_c_values)
lambda_c_values.sort()

mlv = lambda_c_values[-3:].mean()  # mean of the 3 best scores

cpt_max_lambda = mlv * TPV["cpt_task"].CPT_PROP_OF_MAX

TPV["cpt_task"].TASK_MODE = "CPT"
TPV["cpt_state"].max_lambda = cpt_max_lambda  # set CPT max as % of lambda_c
TPV["cpt_state"].current_score = 0  # carry score over from calibration
TPV["cpt_state"].lambda_val = cpt_max_lambda * 0.5  # set init as 1/2 of CPT max

cpt_task = StateMachine()
cpt_task.set_parameters(TPV["cpt_task"], TPV["cpt_state"], TPV["mobi_dict"])

inst = []
inst.append(
    """This part of the task will be much easier.
Try to keep the circles as close to
the center of the screen as you can."""
)

for k in range(len(inst)):
    cpt_task.show_instructions(message_str=inst[k])

cpt_lambda_c_vals = cpt_task.run()

# If we are using the accelerometer, close it down nicely
if TPV["cpt_task"].XY_INPUT_MODE == "ACCEL":
    cst_task.view_model.cst_user_input.shutdown()

