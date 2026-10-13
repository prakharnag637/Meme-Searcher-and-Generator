import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from urllib.parse import quote_plus
import webbrowser

from PIL import Image, ImageTk
from meme_engine import MemeEngine

try:
    from meme_search import MemeSearch
except ImportError:
    MemeSearch = None


# ==================== THEME ====================

BG = "#101116"
PANEL = "#191B24"
PANEL_2 = "#222532"
INPUT = "#11131A"
TEXT = "#F5F7FB"
MUTED = "#A6ADBB"
PURPLE = "#8B5CF6"
PURPLE_HOVER = "#7C3AED"
BLUE = "#3B82F6"
GREEN = "#10B981"
BORDER = "#303444"


class MemeGenPrototype:
    def __init__(self, root):
        self.root = root
        self.root.title("MemeGen AI")
        self.root.geometry("1180x780")
        self.root.minsize(980, 680)
        self.root.configure(bg=BG)

        self.engine = MemeEngine()
        self.searcher = MemeSearch() if MemeSearch else None

        self.current_image = None
        self.preview_image = None
        self.current_source_url = None
        self.is_busy = False

        self.configure_styles()
        self.build_ui()

    # ==================== STYLES ====================

    def configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Modern.TCombobox",
            fieldbackground=INPUT,
            background=PANEL_2,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=BORDER,
            padding=10
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", INPUT)],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", INPUT)],
            selectforeground=[("readonly", TEXT)]
        )

    def create_button(self, parent, text, command, color, hover, compact=False):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=hover,
            activeforeground="white",
            disabledforeground="#858B98",
            font=("Segoe UI", 10 if compact else 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=9 if compact else 13,
            wraplength=420
        )
        button.bind(
            "<Enter>",
            lambda event: button.configure(bg=hover)
            if button["state"] != "disabled" else None
        )
        button.bind(
            "<Leave>",
            lambda event: button.configure(bg=color)
            if button["state"] != "disabled" else None
        )
        return button

    # ==================== UI ====================

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(20, 15))

        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left", anchor="w")

        tk.Label(
            brand, text="😂", font=("Segoe UI Emoji", 27), bg=BG, fg=TEXT
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            brand, text="MemeGen", font=("Segoe UI", 27, "bold"),
            bg=BG, fg=TEXT
        ).pack(side="left")

        tk.Label(
            brand, text=" AI", font=("Segoe UI", 27, "bold"),
            bg=BG, fg=PURPLE
        ).pack(side="left")

        tk.Label(
            header, text="YOUR SCENARIO. YOUR HUMOUR. YOUR MEME.",
            font=("Segoe UI", 9, "bold"), bg=BG, fg=MUTED
        ).pack(side="right", anchor="center", pady=(8, 0))

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=28)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=22)
        body.grid_columnconfigure(0, weight=11, uniform="content")
        body.grid_columnconfigure(1, weight=10, uniform="content")
        body.grid_rowconfigure(0, weight=1)

        # Left editor panel
        left = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        left_inner = tk.Frame(left, bg=PANEL, padx=22, pady=22)
        left_inner.pack(fill="both", expand=True)

        tk.Label(
            left_inner, text="Create your meme",
            font=("Segoe UI", 19, "bold"), bg=PANEL, fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            left_inner, text="Describe a moment. We'll turn it into a meme.",
            font=("Segoe UI", 10), bg=PANEL, fg=MUTED
        ).pack(anchor="w", pady=(5, 18))

        tk.Label(
            left_inner, text="YOUR SCENARIO",
            font=("Segoe UI", 9, "bold"), bg=PANEL, fg="#C4B5FD"
        ).pack(anchor="w", pady=(0, 8))

        self.scenario = tk.Text(
            left_inner, height=5, wrap="word",
            font=("Segoe UI", 11), bg=INPUT, fg=TEXT,
            insertbackground=TEXT, selectbackground=PURPLE,
            relief="flat", bd=0, padx=14, pady=13,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=PURPLE
        )
        self.scenario.pack(fill="x")
        self.scenario.insert(
            "1.0",
            "When the professor announces a surprise test and I haven't studied anything"
        )
        self.scenario.bind(
            "<FocusIn>",
            lambda event: self.scenario.configure(highlightbackground=PURPLE)
        )
        self.scenario.bind(
            "<FocusOut>",
            lambda event: self.scenario.configure(highlightbackground=BORDER)
        )

        tk.Label(
            left_inner, text="TRY A SCENARIO",
            font=("Segoe UI", 9, "bold"), bg=PANEL, fg=MUTED
        ).pack(anchor="w", pady=(15, 8))

        chips = tk.Frame(left_inner, bg=PANEL)
        chips.pack(fill="x")

        examples = [
            ("🍕 Food mystery", "When my mom asks who ate the food in the fridge"),
            ("📝 Surprise test", "When the professor announces a surprise test and I haven't studied anything"),
            ("💻 Coding bug", "When my code finally works and I don't know why"),
            ("🎓 Attendance", "When my attendance is 74.9% and the minimum is 75%"),
        ]

        for index, (label, value) in enumerate(examples):
            chip = tk.Button(
                chips, text=label, command=lambda v=value: self.set_scenario(v),
                bg=PANEL_2, fg=TEXT, activebackground="#34384A",
                activeforeground=TEXT, relief="flat", bd=0,
                font=("Segoe UI", 9), cursor="hand2", padx=9, pady=7
            )
            chip.grid(
                row=index // 2, column=index % 2, sticky="ew",
                padx=(0, 6) if index % 2 == 0 else (0, 0), pady=(0, 6)
            )

        chips.columnconfigure(0, weight=1)
        chips.columnconfigure(1, weight=1)

        tk.Label(
            left_inner, text="HUMOUR STYLE",
            font=("Segoe UI", 9, "bold"), bg=PANEL, fg="#C4B5FD"
        ).pack(anchor="w", pady=(10, 8))

        self.style = ttk.Combobox(
            left_inner, state="readonly", style="Modern.TCombobox",
            values=[
                "Relatable", "Sarcastic", "Dank", "Savage",
                "Wholesome", "Dramatic", "College Life"
            ]
        )
        self.style.current(0)
        self.style.pack(fill="x")

        # Three distinct actions: internal search, generation, browser search.
        actions = tk.Frame(left_inner, bg=PANEL)
        actions.pack(fill="x", pady=(16, 0))

        self.search_button = self.create_button(
            actions, "🔎  Find an existing meme first",
            self.search_then_fallback, BLUE, "#2563EB"
        )
        self.search_button.pack(fill="x", pady=(0, 8))

        self.generate_button = self.create_button(
            actions, "✨  Generate a new meme",
            self.generate_new, PURPLE, PURPLE_HOVER
        )
        self.generate_button.pack(fill="x", pady=(0, 8))

        # Browser search is deliberately a separate, visible option.
        self.browser_button = self.create_button(
            actions, "🌐  Search memes in browser",
            self.open_browser_search, PANEL_2, "#34384A"
        )
        self.browser_button.pack(fill="x", pady=(0, 8))

        self.save_button = self.create_button(
            actions, "💾  Save meme",
            self.save_image, GREEN, "#059669", compact=True
        )
        self.save_button.pack(fill="x")

        # Right preview panel
        right = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        right_inner = tk.Frame(right, bg=PANEL, padx=18, pady=20)
        right_inner.pack(fill="both", expand=True)

        preview_header = tk.Frame(right_inner, bg=PANEL)
        preview_header.pack(fill="x", pady=(0, 12))

        tk.Label(
            preview_header, text="Live preview",
            font=("Segoe UI", 16, "bold"), bg=PANEL, fg=TEXT
        ).pack(side="left")

        tk.Label(
            preview_header, text="PNG",
            font=("Segoe UI", 8, "bold"), bg="#312E81", fg="#DDD6FE",
            padx=9, pady=4
        ).pack(side="right")

        self.preview_frame = tk.Frame(right_inner, bg="#0D0F15")
        self.preview_frame.pack(fill="both", expand=True)

        self.preview = tk.Label(
            self.preview_frame,
            text="😂\n\nYour meme will appear here\n\nEnter a scenario and generate one.",
            justify="center", bg="#0D0F15", fg=MUTED,
            font=("Segoe UI", 12), wraplength=340
        )
        self.preview.pack(fill="both", expand=True, padx=10, pady=10)

        self.source_label = tk.Label(
            right_inner, text="No meme generated yet",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9),
            anchor="w", wraplength=430, justify="left"
        )
        self.source_label.pack(fill="x", pady=(12, 0))

        # Status bar
        footer = tk.Frame(self.root, bg="#0B0C10")
        footer.pack(fill="x", side="bottom")

        self.status_dot = tk.Label(
            footer, text="●", bg="#0B0C10", fg=GREEN, font=("Segoe UI", 9)
        )
        self.status_dot.pack(side="left", padx=(28, 7), pady=10)

        self.status = tk.Label(
            footer, text="Ready when you are",
            bg="#0B0C10", fg=MUTED, font=("Segoe UI", 9), anchor="w"
        )
        self.status.pack(side="left", pady=10)

        tk.Label(
            footer, text="MemeGen AI • Prototype",
            bg="#0B0C10", fg="#6B7280", font=("Segoe UI", 9)
        ).pack(side="right", padx=28, pady=10)

    # ==================== HELPERS ====================

    def set_scenario(self, value):
        self.scenario.delete("1.0", "end")
        self.scenario.insert("1.0", value)
        self.scenario.focus_set()

    def get_scenario(self):
        return self.scenario.get("1.0", "end").strip()

    def set_busy(self, busy, message):
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        self.search_button.configure(state=state)
        self.generate_button.configure(state=state)
        self.browser_button.configure(state=state)
        self.save_button.configure(state=state)
        self.status.configure(text=message)
        self.status_dot.configure(fg="#F59E0B" if busy else GREEN)

    # ==================== INTERNAL MEME SEARCH ====================

    def search_then_fallback(self):
        scenario = self.get_scenario()
        if not scenario:
            messagebox.showwarning("Missing scenario", "Please describe a situation first.")
            return

        if not self.searcher:
            self.status.configure(text="Search module unavailable; generating locally.")
            self.generate_new()
            return

        self.set_busy(True, "Searching for existing memes...")
        threading.Thread(
            target=self.search_worker, args=(scenario,), daemon=True
        ).start()

    def search_worker(self, scenario):
        result, error = None, None
        try:
            result = self.searcher.search_and_download(scenario)
        except Exception as exc:
            error = str(exc)

        self.root.after(0, self.finish_search, scenario, result, error)

    def finish_search(self, scenario, result, error):
        self.set_busy(False, "Search finished")

        if result and result.get("path") and os.path.exists(result["path"]):
            try:
                image = Image.open(result["path"]).convert("RGB")
                self.current_image = image
                self.current_source_url = result.get("source_url")
                self.show_image(image)
                self.source_label.configure(
                    text=f"Existing image found • {self.current_source_url or 'Source URL unavailable'}"
                )
                self.status.configure(
                    text="Existing meme loaded. Check source and usage rights."
                )
                return
            except Exception:
                pass

        try:
            self.generate_for_scenario(scenario)
            message = (
                "Online search unavailable; generated a local meme."
                if error else
                "No suitable online image found; generated a local meme."
            )
            self.status.configure(text=message)
        except Exception as exc:
            messagebox.showerror("Could not create meme", str(exc))
            self.status.configure(text="Could not search or generate a meme.")

    # ==================== GENERATE MEME ====================

    def generate_for_scenario(self, scenario):
        # Support both newer engines (with humour_style) and older versions.
        try:
            output = self.engine.create_meme(
                scenario, humour_style=self.style.get()
            )
        except TypeError as exc:
            if "humour_style" not in str(exc):
                raise
            output = self.engine.create_meme(scenario)

        image = Image.open(output).convert("RGB")
        self.current_image = image
        self.current_source_url = None
        self.show_image(image)
        self.source_label.configure(
            text=f"Generated locally • Style: {self.style.get()}"
        )

    def generate_new(self):
        scenario = self.get_scenario()
        if not scenario:
            messagebox.showwarning("Missing scenario", "Please describe a situation first.")
            return

        try:
            self.generate_for_scenario(scenario)
            self.status.configure(text="Your meme is ready.")
            self.status_dot.configure(fg=GREEN)
        except Exception as exc:
            messagebox.showerror("Generation error", str(exc))

    # ==================== PREVIEW ====================

    def show_image(self, image):
        preview = image.copy()
        preview.thumbnail((520, 520), Image.Resampling.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(preview)
        self.preview.configure(image=self.preview_image, text="", bg="#0D0F15")

    # ==================== BROWSER IMAGE SEARCH ====================

    def open_browser_search(self):
        """Open a real browser search for the user's scenario."""
        scenario = self.get_scenario()
        if not scenario:
            messagebox.showwarning(
                "Missing scenario",
                "Please describe a situation first."
            )
            return

        query = quote_plus(f"{scenario} meme")
        url = f"https://www.google.com/search?tbm=isch&q={query}"

        try:
            webbrowser.open_new_tab(url)
            self.status.configure(text="Opened Google Images in your browser.")
        except Exception as exc:
            messagebox.showerror(
                "Browser error",
                f"Could not open the browser:\n{exc}"
            )

    # ==================== SAVE MEME ====================

    def save_image(self):
        if self.current_image is None:
            messagebox.showinfo("No meme yet", "Generate or find a meme first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("JPEG image", "*.jpg;*.jpeg")
            ],
            initialfile="my_meme.png"
        )
        if not path:
            return

        try:
            self.current_image.save(path)
            messagebox.showinfo("Saved", "Your meme was saved successfully.")
            self.status.configure(text=f"Saved • {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Save error", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    app = MemeGenPrototype(root)
    root.mainloop()
