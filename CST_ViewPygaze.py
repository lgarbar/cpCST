from psychopy import visual


class View:
    """
    Class holding view objects.
    """

    def __init__(self, win, **kwargs):

        # Instruction String. Can change at runtime as well.
        self.instruction_str = (
            "Keep the cursor at the center of the screen."
        )
        self.instruction_display = visual.TextStim(
            win, text=self.instruction_str, units="norm", wrapWidth=1.25
        )

        # Initialize graphical objects

        self.out_of_bounds = visual.Rect(
            win,
            -1.0,
            1,
            pos=(0.0, 0.0),
            fillColor=[0.8, -0.2, -0.2],
            lineWidth=2,
            lineColor=[-1, -1, -1],
            units="norm",
        )

        self.stim = visual.Circle(
            win,
            fillColor=[-0.25, -0.25, 0.75],
            lineColor=[-1, -1, -1],
            units="height",
            radius=0.025,
        )

        self.outer_stim = visual.Circle(
            win,
            # slightly darker
            fillColor=[-0.4, -0.4, 0.75],
            lineColor=[-1, -1, -1],
            units="height",
            radius=0.05,
        )

        self.fix = visual.Circle(
            win,
            fillColor=[-1, -0.25, -0.25],
            lineColor=[-1, -1, -1],
            units="height",
            radius=0.006,
            pos=[0, 0],
        )

        self.left_bounds = visual.Rect(
            win,
            0.1,
            0.8,
            pos=(0.0 - 75, 0),
            fillColor=[0.75, -0.25, -0.25],
            lineWidth=2,
            lineColor=[-0.75, -0.75, -0.75],
        )

        self.right_bounds = visual.Rect(
            win,
            0.1,
            0.8,
            pos=(0.75, 0),
            fillColor=[0.75, -0.25, -0.25],
            lineWidth=2,
            lineColor=[-0.75, -0.75, -0.75],
        )

        # Text Boxes
        # Top, Left
        self.time_display = visual.TextBox(
            window=win,
            text="Time:",
            font_size=32,
            font_color=[-1.0, -1.0, -1.0],
            color_space="rgb",
            size=(1.8, 0.1),
            pos=(0, 0.9),
            units="norm",
        )

        # Top, Right
        self.lambda_display = visual.TextBox(
            window=win,
            text="Lambda:",
            font_size=32,
            font_color=[-1.0, -1.0, -1.0],
            color_space="rgb",
            size=(1.8, 0.1),
            pos=(0.7, 0.9),
            units="norm",
            grid_horz_justification="center",
        )

        # Top, Center
        self.score_display = visual.TextStim(
            win=win,
            text="Score:",
            color=[-1.0, -1.0, -1.0],
            colorSpace="rgb",
            pos=(0, 0.9),
            units="norm",
        )

        self.reset_label = visual.TextStim(
            win=win,
            text="Get Ready",
            color=[-1.0, -1.0, -1.0],
            colorSpace="rgb",
            pos=(0, 0),
            units="norm",
        )

        self.crash_label = visual.TextStim(
            win=win,
            text="Crash!",
            color=[1.0, 0.25, 0.25],
            colorSpace="rgb",
            pos=(0, 0),
            units="norm",
        )
