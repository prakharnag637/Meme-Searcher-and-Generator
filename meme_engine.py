import random
import re
from PIL import Image, ImageDraw, ImageFont


class MemeEngine:
    """Scenario-aware local meme generator. No API key or internet required."""

    def __init__(self):
        self.backgrounds = [
            (35, 39, 42), (50, 35, 70), (25, 65, 75),
            (85, 45, 45), (40, 65, 45), (30, 45, 80)
        ]

        # Each entry contains scenario keywords and captions by humour style.
        self.memes = [
            {
                "category": "food / caught",
                "keywords": ["mom asks", "mum asks", "who ate", "food in the fridge",
                             "ate the food", "who took my food", "leftovers"],
                "captions": {
                    "Relatable": ("MOM: WHO ATE THE FOOD?", "ME CHEWING IN 4K: WHAT FOOD?"),
                    "Sarcastic": ("THE FRIDGE HAS BEEN RAIDED", "I WOULD INVESTIGATE, BUT I'M BUSY DIGESTING"),
                    "Dank": ("CAMERA FOOTAGE: ME AT 2 AM", "ME: THIS EVIDENCE IS AI-GENERATED"),
                    "Savage": ("MOM STARTS THE INVESTIGATION", "SIBLINGS GET FALSELY ACCUSED IN 0.2 SECONDS"),
                    "Wholesome": ("MOM: WHO TOOK MY LEFTOVERS?", "ME: LET'S ORDER YOU SOMETHING BETTER ❤️"),
                    "Dramatic": ("THE LEFTOVERS ARE GONE", "A FAMILY-WIDE INVESTIGATION HAS BEGUN"),
                    "College Life": ("HOSTEL FOOD: MISSING", "SUSPECT: EVERY ROOMMATE"),
                },
            },
            {
                "category": "surprise exam",
                "keywords": ["surprise test", "pop quiz", "unexpected exam", "exam tomorrow",
                             "haven't studied", "havent studied", "not studied", "exam paper",
                             "test announced", "professor announces", "teacher says take out a sheet"],
                "captions": {
                    "Relatable": ("PROFESSOR: SURPRISE TEST!", "MY BRAIN: SURPRISE, I KNOW NOTHING"),
                    "Sarcastic": ("THE PROFESSOR SAID 'IT'S EASY'", "SO IS SKYDIVING, UNTIL YOU JUMP"),
                    "Dank": ("MY PREPARATION: 0 BYTES", "PANIC.EXE HAS STOPPED RESPONDING"),
                    "Savage": ("PROFESSOR: THIS IS FROM THE SYLLABUS", "THE SYLLABUS I HAVE NEVER OPENED"),
                    "Wholesome": ("SURPRISE TEST TODAY", "AT LEAST WE'RE ALL PANICKING TOGETHER"),
                    "Dramatic": ("ONE ANNOUNCEMENT", "1000 HEART RATES IMMEDIATELY INCREASE"),
                    "College Life": ("SIR: TAKE OUT A SHEET OF PAPER", "ME: CAN I TAKE OUT A LEAVE APPLICATION?"),
                },
            },
            {
                "category": "coding",
                "keywords": ["code", "coding", "bug", "python", "program", "debug", "error", "compiler"],
                "captions": {
                    "Relatable": ("THE CODE FINALLY WORKS", "DON'T ASK ME HOW. DON'T TOUCH IT."),
                    "Sarcastic": ("FIXED ONE BUG", "THE OTHER 17 WERE FEELING NEGLECTED"),
                    "Dank": ("IT WORKS ON MY MACHINE", "DEPLOYMENT: LET THE HORROR BEGIN"),
                    "Savage": ("THE BUG WAS ONE SEMICOLON", "I LOST THREE HOURS AND A PIECE OF MY SOUL"),
                    "Wholesome": ("MY CODE RAN WITHOUT ERRORS", "WE'RE SO PROUD OF YOU, LITTLE PROGRAM"),
                    "Dramatic": ("I CHANGED ONE LINE", "THE ENTIRE APPLICATION ENTERED A NEW TIMELINE"),
                    "College Life": ("ASSIGNMENT DUE IN 5 MINUTES", "COMPILING AND PRAYING"),
                },
            },
            {
                "category": "attendance",
                "keywords": ["attendance", "74.9", "75%", "short attendance", "attendance shortage"],
                "captions": {
                    "Relatable": ("ATTENDANCE: 74.9%", "MY DEGREE DEPENDS ON 0.1%"),
                    "Sarcastic": ("I ATTENDED MOST OF THE SEMESTER", "THE PORTAL: SOURCE? TRUST ME BRO"),
                    "Dank": ("ATTENDANCE: 74.9%", "ONE MORE ABSENCE AND I'M A VISITOR"),
                    "Savage": ("SOCIETY: AIM HIGH", "ME: FIRST, LET ME REACH 75%"),
                    "Wholesome": ("JUST 0.1% LEFT", "YOU'VE GOT THIS. GO TO CLASS ❤️"),
                    "Dramatic": ("ATTENDANCE: 74.9%", "THE FINAL 0.1% IS THE FINAL BOSS"),
                    "College Life": ("FRIEND: SKIP CLASS?", "ME WITH 74.9% ATTENDANCE: BLOCKED"),
                },
            },
            {
                "category": "friend claims they studied",
                "keywords": ["friend says he studied", "friend says they studied", "studied everything",
                             "bro studied", "gaming before exam", "friend studied"],
                "captions": {
                    "Relatable": ("BRO: I STUDIED EVERYTHING", "ALSO BRO, ONLINE 8 HOURS PLAYING GAMES"),
                    "Sarcastic": ("'I DIDN'T STUDY AT ALL'", "THEIR HIGHLIGHTED NOTES HAVE A TABLE OF CONTENTS"),
                    "Dank": ("BRO SAYS HE'S UNPREPARED", "HIS REVISION NOTES HAVE REVISION NOTES"),
                    "Savage": ("FRIEND: I'M DEFINITELY FAILING", "TOPS THE CLASS BY 12 MARKS"),
                    "Wholesome": ("FRIEND: I DIDN'T STUDY", "LET'S REVISE TOGETHER ANYWAY ❤️"),
                    "Dramatic": ("HE SAID HE DIDN'T STUDY", "THE CLASS RANKING SYSTEM TREMBLES"),
                    "College Life": ("BRO WAS GAMING ALL NIGHT", "NOW HE'S ASKING WHICH CHAPTER IS IMPORTANT"),
                },
            },
            {
                "category": "group project",
                "keywords": ["group project", "team project", "nobody has started", "project due tomorrow",
                             "group assignment", "one person does everything"],
                "captions": {
                    "Relatable": ("GROUP PROJECT DUE TOMORROW", "ME DISCOVERING I'M THE WHOLE GROUP"),
                    "Sarcastic": ("TEAMWORK MAKES THE DREAM WORK", "WHEN THE TEAM IS JUST YOU AND YOUR LAPTOP"),
                    "Dank": ("GROUP MEMBERS: 5", "CONTRIBUTORS: 1. MEET THE ENTIRE DEPARTMENT"),
                    "Savage": ("'I'LL DO MY PART TONIGHT'", "SENT 3 DAYS AFTER THE DEADLINE"),
                    "Wholesome": ("GROUP PROJECT PANIC", "AT LEAST THE SUBMISSION PORTAL BELIEVES IN US ❤️"),
                    "Dramatic": ("DEADLINE: TOMORROW", "GROUP CHAT: LAST SEEN 3 WEEKS AGO"),
                    "College Life": ("GROUP PROJECT", "MY TEAMMATES' BIGGEST CONTRIBUTION: 'BRO UPDATE?'"),
                },
            },
            {
                "category": "teacher asks a question",
                "keywords": ["teacher asks a question", "professor asks", "whole class looks at me",
                             "teacher asks", "any doubts", "called on me"],
                "captions": {
                    "Relatable": ("TEACHER: ANY ANSWERS?", "THE CLASS SUDDENLY STUDIES THE FLOOR"),
                    "Sarcastic": ("I MADE EYE CONTACT FOR 0.1 SECONDS", "NOW I'M THE CLASS REPRESENTATIVE"),
                    "Dank": ("TEACHER: YOU, ANSWER THIS", "MY SOUL HAS LEFT THE CHAT"),
                    "Savage": ("I KNEW THE ANSWER", "THEN THE TEACHER SAID 'EXPLAIN WHY'"),
                    "Wholesome": ("TEACHER: ANYONE WANT TO TRY?", "ME, GATHERING 2% COURAGE: I CAN TRY"),
                    "Dramatic": ("THE TEACHER LOOKED IN MY DIRECTION", "TIME SLOWED DOWN. MUSIC STARTED."),
                    "College Life": ("SIR: ANY DOUBTS?", "ME: YES, ABOUT MY DEGREE CHOICE"),
                },
            },
            {
                "category": "sleep / late scrolling",
                "keywords": ["sleep early", "scrolling until", "3 am", "3am", "sleep at 3", "phone all night"],
                "captions": {
                    "Relatable": ("ME: I'LL SLEEP EARLY TONIGHT", "ALSO ME AT 3 AM: ONE LAST VIDEO"),
                    "Sarcastic": ("SLEEP SCHEDULE: FIXED", "FIXED IN THE SENSE THAT IT'S PERMANENTLY BROKEN"),
                    "Dank": ("IT'S JUST A 5-MINUTE SCROLL", "THE BIRDS ARE SINGING"),
                    "Savage": ("MY ALARM: 7 AM", "MY SCREEN TIME: YOUR HONOUR, I PLEAD GUILTY"),
                    "Wholesome": ("YOU DESERVE SOME REST", "SAID ME, THEN SCROLLED FOR 4 MORE HOURS"),
                    "Dramatic": ("I CHECKED ONE NOTIFICATION", "THE SUN HAS RISEN"),
                    "College Life": ("CLASS AT 8 AM", "ME GOING TO BED AT 3:47 AM"),
                },
            },
            {
                "category": "bank balance / spending",
                "keywords": ["bank balance", "ordered food", "ordering food", "broke after", "money after shopping"],
                "captions": {
                    "Relatable": ("FOOD DELIVERY: ORDER CONFIRMED", "BANK BALANCE: CHARACTER DEVELOPMENT"),
                    "Sarcastic": ("I DESERVE A LITTLE TREAT", "MY BANK ACCOUNT DISAGREES"),
                    "Dank": ("BALANCE BEFORE ORDER: ₹500", "BALANCE AFTER DELIVERY FEE: LORE"),
                    "Savage": ("I'M GREAT AT SAVING MONEY", "JUST NOT AT KEEPING IT"),
                    "Wholesome": ("TREAT YOURSELF SOMETIMES", "JUST MAYBE CHECK THE BALANCE FIRST ❤️"),
                    "Dramatic": ("ORDER TOTAL: ₹249", "FINANCIAL CRISIS: UNLOCKED"),
                    "College Life": ("MONTH-END IN HOSTEL", "MAGGI IS NOW A FINANCIAL STRATEGY"),
                },
            },
        ]

        self.fallbacks = {
            "Relatable": ("ME TRYING TO GET MY LIFE TOGETHER", "LIFE: PLEASE RESTART AND TRY AGAIN"),
            "Sarcastic": ("EVERYTHING IS UNDER CONTROL", "THAT'S A VERY CONFIDENT LIE"),
            "Dank": ("SYSTEM STATUS: ???", "BRAIN.EXE HAS STOPPED RESPONDING"),
            "Savage": ("I HAVE A PLAN", "THE PLAN HAS OTHER PLANS"),
            "Wholesome": ("YOU DON'T HAVE TO BE PERFECT", "JUST KEEP GOING ❤️"),
            "Dramatic": ("THIS IS THE WORST THING EVER", "UNTIL THE NEXT THING HAPPENS"),
            "College Life": ("COLLEGE LIFE", "SURVIVING ON DEADLINES AND CHAI"),
        }

    def detect_category(self, scenario):
        text = re.sub(r"[^a-z0-9.%₹ ]", " ", scenario.lower())
        text = " ".join(text.split())
        best = None
        best_score = 0
        for item in self.memes:
            score = 0
            for keyword in item["keywords"]:
                key = keyword.lower()
                if key in text:
                    score += 2 if " " in key else 1
            if score > best_score:
                best, best_score = item, score
        return best

    def generate_caption(self, scenario, humour_style="Relatable"):
        item = self.detect_category(scenario)
        style = humour_style if humour_style in self.fallbacks else "Relatable"
        if item:
            return item["captions"].get(style, item["captions"]["Relatable"])
        return self.fallbacks[style]

    def get_font(self, size):
        for path in [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]:
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
        return ImageFont.load_default()

    def _fit_font(self, draw, text, max_width, initial_size=58):
        size = initial_size
        while size > 24:
            font = self.get_font(size)
            if draw.textbbox((0, 0), text, font=font, stroke_width=3)[2] <= max_width:
                return font
            size -= 2
        return self.get_font(size)

    def draw_centered_text(self, draw, text, y, font, width, max_width=None):
        max_width = max_width or width - 90
        words = text.split()
        lines, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=font, stroke_width=3)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        line_height = font.size + 12
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font, stroke_width=3)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            draw.text((x, y), line, font=font, fill="white",
                      stroke_width=3, stroke_fill="black")
            y += line_height
        return y

    def draw_meme_face(self, draw, center_x, center_y, category=None):
        # A playful reaction face; expression varies by category.
        radius = 100
        draw.ellipse((center_x-radius, center_y-radius, center_x+radius, center_y+radius),
                     fill="#FFD166", outline="black", width=6)
        if category and category["category"] in ("food / caught", "friend claims they studied"):
            # suspicious eyes
            draw.ellipse((center_x-52, center_y-32, center_x-22, center_y-2), fill="black")
            draw.ellipse((center_x+22, center_y-32, center_x+52, center_y-2), fill="black")
            draw.line((center_x-55, center_y-42, center_x-20, center_y-48), fill="black", width=6)
            draw.line((center_x+20, center_y-48, center_x+55, center_y-42), fill="black", width=6)
            draw.arc((center_x-45, center_y-8, center_x+45, center_y+50), 190, 340, fill="black", width=7)
        elif category and category["category"] in ("surprise exam", "teacher asks a question"):
            draw.ellipse((center_x-52, center_y-38, center_x-22, center_y-8), fill="black")
            draw.ellipse((center_x+22, center_y-38, center_x+52, center_y-8), fill="black")
            draw.ellipse((center_x-20, center_y+20, center_x+20, center_y+60), fill="black")
        else:
            draw.ellipse((center_x-50, center_y-35, center_x-20, center_y-5), fill="black")
            draw.ellipse((center_x+20, center_y-35, center_x+50, center_y-5), fill="black")
            draw.arc((center_x-50, center_y-25, center_x+50, center_y+55),
                     start=10, end=170, fill="black", width=7)

    def create_meme(self, scenario, output_path="generated_meme.png", humour_style="Relatable"):
        width, height = 1080, 1080
        category = self.detect_category(scenario)
        background = random.choice(self.backgrounds)
        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)

        # Subtle decorative dots
        for _ in range(14):
            x, y = random.randint(0, width-40), random.randint(0, height-40)
            r = random.randint(10, 35)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=(95, 105, 110), width=2)

        top_text, bottom_text = self.generate_caption(scenario, humour_style)
        top_font = self._fit_font(draw, top_text.upper(), width - 90, 58)
        bottom_font = self._fit_font(draw, bottom_text.upper(), width - 90, 58)

        self.draw_centered_text(draw, top_text.upper(), 70, top_font, width)
        self.draw_meme_face(draw, width // 2, height // 2, category)
        self.draw_centered_text(draw, bottom_text.upper(), 820, bottom_font, width)

        image.save(output_path, format="PNG")
        return output_path
