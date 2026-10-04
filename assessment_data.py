import os
import random
import cv2

from PIL import Image, ImageTk


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ASSESSMENT_DIR = os.path.join(
    BASE_DIR,
    "assets",
    "assessment"
)


# ============================================================
# ASSESSMENT DATA
# ============================================================

ASSESSMENT_DATA = {

    "fighter": [

        {
            "video": "fighter_01.mp4",

            "question":
                "The enemy is low HP, but two enemies are missing "
                "from the minimap. What should you do?",

            "options": [
                "A) Chase the enemy immediately",
                "B) Retreat and check the minimap",
                "C) Dive under the enemy tower",
                "D) Ignore the missing enemies"
            ],

            "correct": 1,

            "explanation":
                "Checking the minimap before chasing is safer because "
                "the missing enemies may be preparing an ambush."
        },

        {
            "video": "fighter_02.mp4",

            "question":
                "Your team wins a team fight near an objective. "
                "What should you consider doing next?",

            "options": [
                "A) Take an available objective",
                "B) Recall immediately",
                "C) Chase an enemy across the map",
                "D) Farm alone in the opposite lane"
            ],

            "correct": 0,

            "explanation":
                "A team-fight victory can create an opportunity to "
                "secure an objective and convert the advantage."
        }
    ],


    "assassin": [

        {
            "video": "assassin_01.mp4",

            "question":
                "The enemy marksman is exposed during a team fight. "
                "What should you consider before attacking?",

            "options": [
                "A) Enemy crowd-control abilities",
                "B) Only the marksman's HP",
                "C) Ignore the minimap",
                "D) Attack without an escape plan"
            ],

            "correct": 0,

            "explanation":
                "An assassin should consider enemy crowd-control "
                "abilities before committing to an attack."
        },

        {
            "video": "assassin_02.mp4",

            "question":
                "You are alone in the enemy jungle and several enemies "
                "are missing from the minimap. What is the safer decision?",

            "options": [
                "A) Continue deeper into the jungle",
                "B) Fight the nearest enemy",
                "C) Check enemy positions before continuing",
                "D) Ignore the minimap"
            ],

            "correct": 2,

            "explanation":
                "Missing enemies create uncertainty. Checking their "
                "positions helps prevent an unnecessary ambush."
        }
    ],


    "mage": [

        {
            "video": "mage_01.mp4",

            "question":
                "Your team is preparing for a team fight. "
                "Where should a mage generally position?",

            "options": [
                "A) Directly in front of the enemy tank",
                "B) Behind appropriate frontline protection",
                "C) Alone inside the enemy jungle",
                "D) Under the enemy tower"
            ],

            "correct": 1,

            "explanation":
                "Mages generally benefit from maintaining safe distance "
                "while still being able to use their abilities."
        },

        {
            "video": "mage_02.mp4",

            "question":
                "The enemy team is grouped together. What can a mage "
                "consider before using an important area-of-effect ability?",

            "options": [
                "A) Ability range and enemy positioning",
                "B) Ignore enemy movement",
                "C) Use it randomly",
                "D) Walk directly into the enemy team"
            ],

            "correct": 0,

            "explanation":
                "Ability range, timing, and enemy positioning can affect "
                "whether an area-of-effect skill is effective."
        }
    ],


    "marksman": [

        {
            "video": "marksman_01.mp4",

            "question":
                "An enemy assassin is missing from the minimap. "
                "What should you do?",

            "options": [
                "A) Push forward alone",
                "B) Stay aware of possible threats",
                "C) Ignore the minimap",
                "D) Enter the enemy jungle alone"
            ],

            "correct": 1,

            "explanation":
                "Marksmen can be vulnerable to sudden attacks, so "
                "awareness of missing enemies is important."
        },

        {
            "video": "marksman_02.mp4",

            "question":
                "Your frontline is engaging the enemy team. "
                "What should you consider?",

            "options": [
                "A) Maintain a safe attacking distance",
                "B) Run directly into the enemy team",
                "C) Ignore enemy assassins",
                "D) Stop watching the minimap"
            ],

            "correct": 0,

            "explanation":
                "Maintaining appropriate distance can allow the marksman "
                "to contribute damage while reducing unnecessary risk."
        }
    ],


    "tank": [

        {
            "video": "tank_01.mp4",

            "question":
                "Your damage dealers are nearby and ready. "
                "What should a tank consider before initiating?",

            "options": [
                "A) Team positioning and enemy abilities",
                "B) Running into the enemy alone",
                "C) Ignoring your team",
                "D) Leaving the team fight"
            ],

            "correct": 0,

            "explanation":
                "A tank should consider whether teammates can follow "
                "the initiation and whether important enemy abilities "
                "are available."
        },

        {
            "video": "tank_02.mp4",

            "question":
                "An enemy assassin is targeting your marksman. "
                "What should you consider?",

            "options": [
                "A) Protecting your vulnerable teammate",
                "B) Leaving the marksman alone",
                "C) Chasing an unrelated enemy",
                "D) Ignoring the team fight"
            ],

            "correct": 0,

            "explanation":
                "Protecting vulnerable teammates can be an important "
                "part of a tank's role during team fights."
        }
    ],


    "support": [

        {
            "video": "support_01.mp4",

            "question":
                "Your teammate is being attacked and you have a "
                "protective ability available. What should you consider?",

            "options": [
                "A) Protecting the teammate when appropriate",
                "B) Immediately leaving the area",
                "C) Ignoring the teammate",
                "D) Using the ability randomly"
            ],

            "correct": 0,

            "explanation":
                "Support decisions should consider teammate positioning, "
                "enemy threats, and ability timing."
        },

        {
            "video": "support_02.mp4",

            "question":
                "Your team is preparing for an objective. "
                "What should a support player consider?",

            "options": [
                "A) Vision, positioning, and team safety",
                "B) Walking alone into the enemy jungle",
                "C) Ignoring enemy positions",
                "D) Leaving the team"
            ],

            "correct": 0,

            "explanation":
                "Vision, positioning, and awareness of enemy threats "
                "can help the team prepare for an objective."
        }
    ]
}


# ============================================================
# ASSESSMENT ENGINE
# ============================================================

class Assessment:

    def __init__(self, role, number_of_questions=5):

        self.role = role.lower()

        self.number_of_questions = number_of_questions

        self.questions = []

        self.current_question = 0

        self.score = 0

        self.answered = False

        self.load_questions()


    # --------------------------------------------------------
    # LOAD QUESTIONS
    # --------------------------------------------------------

    def load_questions(self):

        if self.role not in ASSESSMENT_DATA:

            raise ValueError(
                f"Unknown role: {self.role}"
            )

        available_questions = ASSESSMENT_DATA[
            self.role
        ]

        questions = available_questions.copy()

        random.shuffle(questions)

        self.questions = questions[
            :min(
                self.number_of_questions,
                len(questions)
            )
        ]


    # --------------------------------------------------------
    # CURRENT QUESTION
    # --------------------------------------------------------

    def get_current_question(self):

        if self.current_question >= len(
            self.questions
        ):
            return None

        question = self.questions[
            self.current_question
        ].copy()

        video_path = os.path.join(
            ASSESSMENT_DIR,
            self.role,
            question["video"]
        )

        question["video_path"] = video_path

        return question


    # --------------------------------------------------------
    # CHECK ANSWER
    # --------------------------------------------------------

    def submit_answer(self, selected_index):

        question = self.get_current_question()

        if question is None:
            return None

        correct = (
            selected_index ==
            question["correct"]
        )

        if correct:
            self.score += 1

        self.answered = True

        return {
            "correct": correct,
            "correct_index": question["correct"],
            "explanation": question["explanation"]
        }


    # --------------------------------------------------------
    # NEXT QUESTION
    # --------------------------------------------------------

    def next_question(self):

        self.current_question += 1

        self.answered = False


    # --------------------------------------------------------
    # CHECK IF FINISHED
    # --------------------------------------------------------

    def is_finished(self):

        return (
            self.current_question >=
            len(self.questions)
        )


    # --------------------------------------------------------
    # GET SCORE
    # --------------------------------------------------------

    def get_score(self):

        total = len(self.questions)

        percentage = (
            (self.score / total) * 100
            if total > 0
            else 0
        )

        return {
            "score": self.score,
            "total": total,
            "percentage": percentage
        }


# ============================================================
# VIDEO PLAYER
# ============================================================

class VideoPlayer:

    def __init__(self, parent):

        self.parent = parent

        self.video_path = None

        self.cap = None

        self.running = False

        self.photo = None

        self.video_label = None


    # --------------------------------------------------------
    # CREATE VIDEO DISPLAY
    # --------------------------------------------------------

    def create_display(self):

        import tkinter as tk

        self.video_label = tk.Label(
            self.parent,
            text="No video loaded",
            bg="black",
            fg="white",
            width=80,
            height=20
        )

        self.video_label.pack(
            fill="both",
            expand=True
        )


    # --------------------------------------------------------
    # LOAD VIDEO
    # --------------------------------------------------------

    def load_video(self, video_path):

        self.stop()

        if not os.path.exists(video_path):

            self.video_label.config(
                text=f"Video not found:\n{video_path}"
            )

            return

        self.video_path = video_path

        self.cap = cv2.VideoCapture(
            video_path
        )

        if not self.cap.isOpened():

            self.video_label.config(
                text="Unable to open video."
            )

            return

        self.running = True

        self.update_frame()


    # --------------------------------------------------------
    # DISPLAY FRAMES
    # --------------------------------------------------------

    def update_frame(self):

        if not self.running:
            return

        if self.cap is None:
            return

        success, frame = self.cap.read()

        if not success:

            self.cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                0
            )

            success, frame = self.cap.read()

        if success:

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            image = Image.fromarray(
                frame
            )

            # Resize while preserving aspect ratio
            max_width = 800
            max_height = 450

            image.thumbnail(
                (max_width, max_height),
                Image.Resampling.LANCZOS
            )

            self.photo = ImageTk.PhotoImage(
                image
            )

            self.video_label.config(
                image=self.photo,
                text=""
            )

        self.parent.after(
            33,
            self.update_frame
        )


    # --------------------------------------------------------
    # STOP VIDEO
    # --------------------------------------------------------

    def stop(self):

        self.running = False

        if self.cap:

            self.cap.release()

            self.cap = None

def create_assessment_tab(self, notebook):

    import tkinter as tk
    from tkinter import messagebox

    # ========================================================
    # ASSESSMENT TAB
    # ========================================================

    assessment_tab = tk.Frame(
        notebook
    )

    notebook.add(
        assessment_tab,
        text="Assessment"
    )


    # ========================================================
    # TOP SECTION
    # ========================================================

    top_frame = tk.Frame(
        assessment_tab,
        padx=20,
        pady=15
    )

    top_frame.pack(
        fill="x"
    )


    tk.Label(
        top_frame,
        text="MLBB Tactical Assessment",
        font=("Arial", 22, "bold")
    ).pack(
        anchor="w"
    )


    tk.Label(
        top_frame,
        text="Select your role and analyze the gameplay scenario.",
        font=("Arial", 11)
    ).pack(
        anchor="w"
    )


    # ========================================================
    # ROLE SELECTION
    # ========================================================

    role_frame = tk.Frame(
        assessment_tab
    )

    role_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )


    tk.Label(
        role_frame,
        text="Role:",
        font=("Arial", 11, "bold")
    ).pack(
        side="left"
    )


    role_variable = tk.StringVar(
        value="fighter"
    )


    role_menu = tk.OptionMenu(
        role_frame,
        role_variable,
        "fighter",
        "assassin",
        "mage",
        "marksman",
        "tank",
        "support"
    )

    role_menu.pack(
        side="left",
        padx=10
    )


    # ========================================================
    # CONTENT AREA
    # ========================================================

    content_frame = tk.Frame(
        assessment_tab
    )

    content_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )


    # --------------------------------------------------------
    # VIDEO
    # --------------------------------------------------------

    video_frame = tk.LabelFrame(
        content_frame,
        text="Scenario Video",
        padx=10,
        pady=10
    )

    video_frame.pack(
        fill="both",
        expand=True
    )


    video_player = VideoPlayer(
        video_frame
    )

    video_player.create_display()


    # ========================================================
    # QUESTION AREA
    # ========================================================

    question_frame = tk.Frame(
        assessment_tab,
        padx=20,
        pady=10
    )

    question_frame.pack(
        fill="x"
    )


    question_label = tk.Label(
        question_frame,
        text="Click START ASSESSMENT.",
        font=("Arial", 13, "bold"),
        wraplength=1000,
        justify="left"
    )

    question_label.pack(
        anchor="w"
    )


    # ========================================================
    # ANSWER BUTTONS
    # ========================================================

    answer_variable = tk.IntVar(
        value=-1
    )

    answer_buttons = []


    for index in range(4):

        button = tk.Radiobutton(
            question_frame,
            text="",
            variable=answer_variable,
            value=index,
            font=("Arial", 11),
            anchor="w",
            justify="left",
            wraplength=950
        )

        button.pack(
            fill="x",
            pady=3
        )

        answer_buttons.append(
            button
        )


    # ========================================================
    # CONTROL BUTTONS
    # ========================================================

    control_frame = tk.Frame(
        assessment_tab,
        pady=10
    )

    control_frame.pack()


    assessment = {
        "engine": None
    }


    # ========================================================
    # UPDATE QUESTION
    # ========================================================

    def update_question():

        engine = assessment["engine"]

        if engine is None:
            return

        if engine.is_finished():

            score = engine.get_score()

            video_player.stop()

            question_label.config(
                text=(
                    f"ASSESSMENT COMPLETE\n\n"
                    f"Score: {score['score']} / {score['total']}\n"
                    f"Percentage: {score['percentage']:.1f}%"
                )
            )

            for button in answer_buttons:

                button.config(
                    state="disabled"
                )

            submit_button.config(
                state="disabled"
            )

            next_button.config(
                state="disabled"
            )

            return


        question = engine.get_current_question()

        if question is None:
            return


        video_player.load_video(
            question["video_path"]
        )


        question_label.config(
            text=(
                f"Question "
                f"{engine.current_question + 1}"
                f" of "
                f"{len(engine.questions)}\n\n"
                f"{question['question']}"
            )
        )


        answer_variable.set(
            -1
        )


        for index, button in enumerate(
            answer_buttons
        ):

            button.config(
                text=question["options"][index],
                state="normal"
            )


        submit_button.config(
            state="normal"
        )

        next_button.config(
            state="disabled"
        )


    # ========================================================
    # START ASSESSMENT
    # ========================================================

    def start_assessment():

        role = role_variable.get()

        try:

            assessment["engine"] = Assessment(
                role=role,
                number_of_questions=5
            )

            update_question()

        except Exception as e:

            messagebox.showerror(
                "Assessment Error",
                str(e)
            )


    # ========================================================
    # SUBMIT ANSWER
    # ========================================================

    def submit_answer():

        engine = assessment["engine"]

        if engine is None:
            return


        selected = answer_variable.get()

        if selected == -1:

            messagebox.showwarning(
                "No Answer",
                "Please select an answer."
            )

            return


        result = engine.submit_answer(
            selected
        )


        if result["correct"]:

            messagebox.showinfo(
                "Correct",
                "Correct answer!\n\n"
                + result["explanation"]
            )

        else:

            correct_index = result[
                "correct_index"
            ]

            correct_answer = engine.questions[
                engine.current_question
            ]["options"][correct_index]


            messagebox.showinfo(
                "Incorrect",
                "The selected answer is incorrect.\n\n"
                f"Correct answer:\n"
                f"{correct_answer}\n\n"
                f"{result['explanation']}"
            )


        for button in answer_buttons:

            button.config(
                state="disabled"
            )


        submit_button.config(
            state="disabled"
        )


        if not engine.is_finished():

            next_button.config(
                state="normal"
            )

        else:

            update_question()


    # ========================================================
    # NEXT QUESTION
    # ========================================================

    def next_question():

        engine = assessment["engine"]

        if engine is None:
            return

        engine.next_question()

        update_question()


    # ========================================================
    # BUTTONS
    # ========================================================

    start_button = tk.Button(
        control_frame,
        text="START ASSESSMENT",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=8,
        command=start_assessment
    )

    start_button.pack(
        side="left",
        padx=5
    )


    submit_button = tk.Button(
        control_frame,
        text="SUBMIT ANSWER",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=8,
        state="disabled",
        command=submit_answer
    )

    submit_button.pack(
        side="left",
        padx=5
    )


    next_button = tk.Button(
        control_frame,
        text="NEXT SCENARIO",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=8,
        state="disabled",
        command=next_question
    )

    next_button.pack(
        side="left",
        padx=5
    )
