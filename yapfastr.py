import tkinter as tk
import tweepy
import threading
import re
from spellchecker import SpellChecker
from dotenv import load_dotenv
import os

load_dotenv()

class TweetWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.result = None
        self.shift_pressed = False
        self.spell_checker = SpellChecker()
        self.animation_running = False
        self.progress_value = 0
        
        self._init_ui()
        self._init_bindings()

    def _init_ui(self):
        self.root.title("tweet")
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#121212")
        
        self.frame = tk.Frame(self.root, bg="#121212")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._setup_text()
        self._setup_progress()
        self._setup_labels()

    def _setup_text(self):
        self.text_widget = tk.Text(
            self.frame,
            wrap="word",
            height=5,
            font=("JetBrainsMono Nerd Font", 10),
            fg="white",
            bg="#121212",
            insertbackground="white",
            insertwidth=2,
            padx=15,
            pady=15,
            bd=0,
            highlightthickness=0
        )
        self.text_widget.pack(fill="both", expand=True)
        self._init_text_tags()

    def _init_text_tags(self):
        self.text_widget.insert("1.0", "tweet: ")
        for tag, config in {
            "prefix": {"foreground": "#c6a0f6"},
            "body": {"lmargin1": 50, "lmargin2": 57},
            "misspelled": {"underline": True, "foreground": "#ed8796"}
        }.items():
            self.text_widget.tag_configure(tag, **config)
        self.text_widget.tag_add("prefix", "1.0", "1.7")
        self.text_widget.tag_add("body", "1.7", "end")
        self.text_widget.mark_set("insert", "1.7")
        self.text_widget.focus_set()
        self.text_widget.edit_modified(False)

    def _setup_progress(self):
        self.progress = tk.Canvas(self.frame, height=2, bg="#121212", highlightthickness=0)
        self.progress.pack(fill="x", padx=15, pady=(5, 0))
        self.progress_rect = self.progress.create_rectangle(0, 0, 0, 2, fill="#a6da95", width=0)

    def _setup_labels(self):
        self.error_label = tk.Label(
            self.frame,
            text="",
            fg="#ed8796",
            bg="#121212",
            font=("JetBrainsMono Nerd Font", 10),
            wraplength=460,
            justify="left"
        )
        self.error_label.pack(fill="x", padx=15, pady=(5, 5))

        count_frame = tk.Frame(self.frame, bg="#121212")
        count_frame.pack(fill="x", padx=15, pady=(5, 0))

        self.helper_label = tk.Label(
            count_frame,
            text="use shift+enter for new line",
            fg="#666666",
            bg="#121212",
            font=("JetBrainsMono Nerd Font", 10),
            anchor="e"
        )
        self.helper_label.pack(side="right")

        tk.Label(count_frame, text="   ", bg="#121212").pack(side="right")
        
        self.char_count_label = tk.Label(
            count_frame,
            text="0",
            fg="#a6da95",
            bg="#121212",
            font=("JetBrainsMono Nerd Font", 10),
            anchor="e"
        )
        self.char_count_label.pack(side="right")

    def _init_bindings(self):
        bindings = {
            "<<Modified>>": self.on_text_change,
            "<Return>": self.handle_return,
            "<Shift-Return>": self.handle_shift_return
        }
        for event, handler in bindings.items():
            self.text_widget.bind(event, handler)

        root_bindings = {
            "<Escape>": self.close_window,
            "<Shift_L>": lambda e: setattr(self, 'shift_pressed', True),
            "<Shift_R>": lambda e: setattr(self, 'shift_pressed', True),
            "<KeyRelease-Shift_L>": lambda e: setattr(self, 'shift_pressed', False),
            "<KeyRelease-Shift_R>": lambda e: setattr(self, 'shift_pressed', False)
        }
        for event, handler in root_bindings.items():
            self.root.bind(event, handler)

    def on_text_change(self, event=None):
        if not self.text_widget.edit_modified():
            return

        text = self.text_widget.get("1.0", "1.7")
        if text != "tweet: ":
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", "tweet: ")

        self.text_widget.tag_add("prefix", "1.0", "1.7")
        self.text_widget.tag_add("body", "1.7", "end")

        char_count = len(self.text_widget.get("1.7", "end-1c"))
        verified = os.getenv("TWITTER_VERIFIED", "False") == "True"
        
        color = "#a6da95"
        count_text = str(char_count)
        if char_count > 250:
            color = "#a6da95" if verified else "#ed8796"
            count_text = f"{char_count}/250"
            
        self.char_count_label.config(text=count_text, fg=color)
        self._check_spelling()
        self.text_widget.edit_modified(False)

    def _check_spelling(self):
        text = self.text_widget.get("1.7", "end-1c")
        words = re.sub(r'[^\w\s]', '', text).split()
        self.text_widget.tag_remove("misspelled", "1.7", "end")
        
        for word in self.spell_checker.unknown(words):
            start = self.text_widget.search(word, "1.7", stopindex="end", nocase=True)
            if start:
                self.text_widget.tag_add("misspelled", start, f"{start}+{len(word)}c")

    def handle_return(self, event):
        return self.submit_text() if not self.shift_pressed else None

    def handle_shift_return(self, event):
        self.text_widget.insert(tk.INSERT, "\n")
        return "break"

    def submit_text(self):
        self.result = self.text_widget.get("1.0", "end-1c")[7:].strip()
        char_count = len(self.result)
        verified = os.getenv("TWITTER_VERIFIED", "False") == "True"

        if char_count > 250 and not verified:
            self.show_error("Exceeded character limit.")
            return "break"

        if self.result:
            self.show_error("")
            self.start_animation()
            threading.Thread(target=self._post_tweet_thread).start()
        return "break"

    def _post_tweet_thread(self):
        success, error = self._post_tweet()
        self.root.after(0, self._handle_tweet_result, success, error)

    def _post_tweet(self):
        try:
            client = tweepy.Client(
                consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
                consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            )
            client.create_tweet(text=self.result)
            return True, None
        except Exception as e:
            return False, str(e)

    def _handle_tweet_result(self, success, error):
        if success:
            self.root.destroy()
        else:
            self.show_error(error)
            self.text_widget.configure(state="normal")
            self.text_widget.focus_set()

    def show_error(self, message):
        self.error_label.config(text=message)
        self.animation_running = False
        self.progress.coords(self.progress_rect, 0, 0, 0, 2)
        self.progress_value = 0

    def start_animation(self):
        self.animation_running = True
        self.progress_value = 0
        self.text_widget.configure(state="disabled")
        self._animate_progress()

    def _animate_progress(self):
        if not self.animation_running:
            return
        width = self.progress.winfo_width()
        self.progress_value = (self.progress_value + 10) % width
        self.progress.coords(self.progress_rect, 0, 0, self.progress_value, 2)
        if self.animation_running:
            self.root.after(10, self._animate_progress)

    def close_window(self, event=None):
        self.result = None
        self.root.destroy()

    def get_input(self):
        self.root.mainloop()
        return self.result

if __name__ == "__main__":
    TweetWindow().get_input()
