import tkinter as tk
import tweepy
import threading

from credentials import TWITTER_CREDENTIALS

class TweetWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_text_widget()
        self.setup_progress_bar()
        self.setup_error_label()
        self.setup_char_count_label()
        self.setup_bindings()
        self.result = None

    def setup_window(self):
        self.root.title("tweet")
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        self.root.configure(bg='#121212')
        
        self.frame = tk.Frame(self.root, bg='#121212')
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_text_widget(self):
        self.text_widget = tk.Text(
            self.frame,
            wrap="word",
            bd=0,
            fg='white',
            bg='#121212',
            font=('JetBrainsMono Nerd Font', 10),
            padx=15,
            pady=15,
            highlightthickness=0,
            insertbackground='white',
            insertwidth=2,
            height=5
        )
        self.text_widget.pack(fill="both", expand=True)
        
        self.text_widget.insert("1.0", "tweet: ")
        self.text_widget.tag_add("prefix", "1.0", "1.7")
        self.text_widget.tag_config("prefix", foreground="#c6a0f6")
        self.text_widget.tag_configure("body", lmargin1=50, lmargin2=57)
        self.text_widget.tag_add("body", "1.7", "end")
        
        self.text_widget.mark_set("insert", "1.7")
        self.text_widget.focus_set()
        self.text_widget.edit_modified(False)

    def setup_progress_bar(self):
        self.progress = tk.Canvas(
            self.frame,
            height=2,
            bg='#121212',
            highlightthickness=0
        )
        self.progress.pack(fill="x", padx=15, pady=(5, 0))
        
        self.progress_rect = self.progress.create_rectangle(
            0, 0, 0, 2,
            fill='#a6da95',
            width=0
        )
        self.animation_running = False
        self.progress_value = 0

    def setup_error_label(self):
        self.error_label = tk.Label(
            self.frame,
            text="",
            fg='#ff4444',
            bg='#121212',
            font=('JetBrainsMono Nerd Font', 10),
            wraplength=460,
            justify='left'
        )
        self.error_label.pack(fill="x", padx=15, pady=(5, 5))

    def setup_char_count_label(self):
        self.char_count_label = tk.Label(
            self.frame,
            text="0",
            fg='#a6da95',
            bg='#121212',
            font=('JetBrainsMono Nerd Font', 10),
            anchor='e'
        )
        self.char_count_label.pack(fill="x", padx=15, pady=(5, 0))

    def setup_bindings(self):
        self.text_widget.bind("<<Modified>>", self.on_text_change)
        self.text_widget.bind('<Return>', self.submit_text)
        self.root.bind('<Escape>', self.close_window)

    def on_text_change(self, event=None):
        if self.text_widget.edit_modified():
            if self.text_widget.get("1.0", "1.7") != "tweet: ":
                self.text_widget.delete("1.0", "end")
                self.text_widget.insert("1.0", "tweet: ")
            self.text_widget.tag_add("prefix", "1.0", "1.7")
            self.text_widget.tag_add("body", "1.7", "end")
            
            char_count = len(self.text_widget.get("1.7", "end-1c"))
            verified = TWITTER_CREDENTIALS.get('verified', False)
            
            if char_count > 250:
                if verified:
                    self.char_count_label.config(text=f"{char_count}/250", fg='#a6da95')
                else:
                    self.char_count_label.config(text=f"{char_count}/250", fg='#ed8796')
            else:
                self.char_count_label.config(text=str(char_count), fg='#a6da95')
            
            self.text_widget.edit_modified(False)

    def show_error(self, message):
        self.error_label.config(text=message)
        self.animation_running = False
        self.progress.coords(self.progress_rect, 0, 0, 0, 2)
        self.progress_value = 0

    def animate_progress(self):
        if not self.animation_running:
            return
        
        width = self.progress.winfo_width()
        self.progress_value = (self.progress_value + 10) % width
        self.progress.coords(self.progress_rect, 0, 0, self.progress_value, 2)
        
        if self.animation_running:
            self.root.after(10, self.animate_progress)

    def start_animation(self):
        self.animation_running = True
        self.progress_value = 0
        self.text_widget.configure(state='disabled')
        self.animate_progress()

    def handle_tweet_result(self, success, error):
        if success:
            self.root.destroy()
        else:
            self.show_error(error)
            self.text_widget.configure(state='normal')
            self.text_widget.focus_set()

    def post_tweet_threaded(self, tweet_text):
        success, error = post_tweet(tweet_text)
        self.root.after(0, self.handle_tweet_result, success, error)

    def submit_text(self, event=None):
        self.result = self.text_widget.get("1.0", "end-1c")[7:].strip()
        char_count = len(self.result)
        verified = TWITTER_CREDENTIALS.get('verified', False)
        
        if char_count > 250 and not verified:
            self.show_error("Exceeded character limit.")
            return "break"

        if self.result:
            self.show_error("")
            self.start_animation()
            threading.Thread(target=self.post_tweet_threaded, args=(self.result,)).start()
        return "break"

    def close_window(self, event=None):
        self.result = None
        self.root.destroy()

    def get_input(self):
        self.root.mainloop()
        return self.result

def post_tweet(tweet_text):
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_CREDENTIALS['consumer_key'],
            consumer_secret=TWITTER_CREDENTIALS['consumer_secret'],
            access_token=TWITTER_CREDENTIALS['access_token'],
            access_token_secret=TWITTER_CREDENTIALS['access_token_secret']
        )
        client.create_tweet(text=tweet_text)
        return True, None
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    TweetWindow().get_input()
