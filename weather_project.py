from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import platform
from PIL import Image, ImageTk
from gtts import gTTS
from weather_classification import predict_weather

# ============================================================
# SETTINGS & ULTRA-MODERN DARK LUXURY THEME
# ============================================================
APP_TITLE = "Weather Classification & AI Desktop Hub"
PREVIEW_SIZE = (280, 180)

BG_MAIN = "#090D16"         # Deep obsidian background
BG_CARD = "#131B2E"         # Elevated card surface
BORDER_COLOR = "#1F293D"    # Subtle border definition
TEXT_MAIN = "#F8FAFC"       # Bright white text
TEXT_MUTED = "#94A3B8"      # Muted slate grey
ACCENT_PRIMARY = "#6366F1"  # Vibrant indigo
ACCENT_HOVER = "#4F46E5"    # Darker indigo for hover
ACCENT_BLUE = "#38BDF8"     # Sky blue highlight
SUCCESS_GREEN = "#10B981"   # Emerald green for success states


# ============================================================
# TEXT-TO-SPEECH ENGINE (gTTS + Background Thread)
# ============================================================
class TTSEngine:
    def __init__(self):
        self.enabled = True
        self.language = "en"

    def speak(self, text):
        if not self.enabled:
            return
        
        # Pastro simbolet ose emojit që gTTS të mos ketë probleme
        clean_text = (
            text.replace("*", "")
                .replace("🌦️", "").replace("👋", "").replace("⚡", "")
                .replace("💧", "").replace("❄️", "").replace("🌈", "")
                .replace("☔", "").replace("🌪️", "").replace("🌫️", "")
                .replace("🧊", "").replace("😊", "")
        )
        
        if not clean_text.strip():
            return

        def run_speech():
            try:
                filename = "weather_speech_temp"
                tts = gTTS(text=clean_text, lang=self.language, slow=False)
                audio_path = f"{filename}.mp3"
                tts.save(audio_path)

                os_system = platform.system()
                if os_system == "Windows":
                    os.system(f"start {audio_path}")
                elif os_system == "Darwin":
                    os.system(f"open {audio_path}")
                else:
                    os.system(f"xdg-open {audio_path}")
            except Exception as e:
                print(f"gTTS Speech Error: {e}")

        threading.Thread(target=run_speech, daemon=True).start()


# ============================================================
# WEATHER CHATBOT LOGIC
# ============================================================
class WeatherChatbot:
    def __init__(self, app):
        self.app = app

    def get_response(self, message):
        message = message.lower().strip()
        weather = self.app.current_weather

        if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I am your Weather Assistant. Ask me anything about the weather science or your image prediction!"
        if any(word in message for word in ["prediction", "detected", "result", "my weather"]):
            if weather:
                return f"Your detected weather is {weather['weather_class']} with {weather['confidence']:.2%} confidence."
            return "You haven't uploaded a weather image yet. Upload one using the panel above!"
        if "dew" in message:
            return "Dew consists of tiny water droplets that form on cool surfaces, usually overnight or in the early morning."
        if any(w in message for w in ["fogsmog", "fog", "smog"]):
            return "Fog is a ground-level cloud reducing visibility. Smog is a mixture of fog and atmospheric pollutants."
        if "frost" in message:
            return "Frost forms when water vapor freezes directly onto sub-zero surfaces into delicate ice crystals."
        if "glaze" in message:
            return "Glaze ice is a slick, smooth layer formed when supercooled raindrops freeze instantly upon impact."
        if any(w in message for w in ["lightning", "lightining"]):
            return "Lightning is a massive electrostatic discharge during thunderstorms. Always stay indoors during active storms!"
        if "rainbow" in message:
            return "Rainbows form when sunlight is refracted, reflected, and dispersed through suspended water droplets."
        if "rain" in message:
            return "Rain is condensed atmospheric water vapor falling in droplets. Don't forget your umbrella!"
        if any(w in message for w in ["sandstorm", "sand storm"]):
            return "A sandstorm is a meteorological hazard driven by strong winds carrying dense clouds of sand and dust."
        if "snow" in message:
            return "Snow consists of frozen ice crystals precipitating from clouds when temperatures remain below freezing."
        if "confidence" in message or "accuracy" in message:
            if weather:
                return f"The model's confidence score for your latest prediction is {weather['confidence']:.2%}."
            return "Upload an image first to evaluate model confidence."
        if "help" in message:
            return "I can assist you with explaining weather phenomena, reviewing your image classification, and checking confidence levels."
        if "thank" in message:
            return "You're very welcome! Let me know if you have any other questions."
        return "I'm your Weather Assistant! Try asking: 'What is snow?' or 'What is fogsmog?'"


# ============================================================
# MAIN WEATHER APP UI (MODERN DESKTOP LAYOUT)
# ============================================================
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("780x950")
        self.root.minsize(720, 850)
        self.root.configure(bg=BG_MAIN)

        self.preview_image = None
        self.current_weather = None
        self.tts = TTSEngine()
        self.chatbot = WeatherChatbot(self)

        self.setup_ui()

    def setup_ui(self):
        # Kryekontejneri me padding elegant
        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------
        header_frame = tk.Frame(main_container, bg=BG_MAIN)
        header_frame.pack(fill=tk.X, pady=(0, 14))

        title_label = tk.Label(
            header_frame,
            text="🌦️ Weather Classification Hub",
            font=("Segoe UI", 18, "bold"),
            bg=BG_MAIN,
            fg=TEXT_MAIN
        )
        title_label.pack(side=tk.LEFT)

        self.tts_button = tk.Button(
            header_frame,
            text="🔊 Voice: ON",
            command=self.toggle_tts,
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD,
            fg=SUCCESS_GREEN,
            activebackground=BORDER_COLOR,
            activeforeground=SUCCESS_GREEN,
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.tts_button.pack(side=tk.RIGHT)

        # ----------------------------------------------------
        # KARTA 1: DASHBOARD I IMAZHIT
        # ----------------------------------------------------
        top_card = tk.Frame(
            main_container,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        top_card.pack(fill=tk.X, pady=(0, 14))

        top_inner = tk.Frame(top_card, bg=BG_CARD)
        top_inner.pack(fill=tk.X, padx=16, pady=16)

        # Kolona Majtas: Imazhi & Butoni
        left_col = tk.Frame(top_inner, bg=BG_CARD)
        left_col.pack(side=tk.LEFT, padx=(0, 20))

        self.image_label = tk.Label(
            left_col,
            text="📷 No Image Loaded\nClick below to browse",
            width=24,
            height=9,
            relief="solid",
            borderwidth=1,
            bg="#0D1322",
            fg=TEXT_MUTED,
            font=("Segoe UI", 9)
        )
        self.image_label.pack(pady=(0, 10))

        self.choose_button = tk.Button(
            left_col,
            text="📁 Choose Image",
            command=self.choose_image,
            font=("Segoe UI", 9, "bold"),
            bg=ACCENT_PRIMARY,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2"
        )
        self.choose_button.pack(fill=tk.X)
        self.add_hover_effect(self.choose_button, ACCENT_PRIMARY, ACCENT_HOVER)

        # Kolona Djathtas: Rezultatet
        right_col = tk.Frame(top_inner, bg=BG_CARD)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        res_heading = tk.Label(
            right_col,
            text="📊 Analysis Results",
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=TEXT_MAIN,
            anchor="w"
        )
        res_heading.pack(fill=tk.X, pady=(0, 10))

        self.result_label = tk.Label(
            right_col,
            text="Weather: Awaiting prediction...",
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=ACCENT_BLUE,
            anchor="w"
        )
        self.result_label.pack(fill=tk.X, pady=(2, 2))

        self.confidence_label = tk.Label(
            right_col,
            text="Confidence: —",
            font=("Segoe UI", 11, "bold"),
            bg=BG_CARD,
            fg=SUCCESS_GREEN,
            anchor="w"
        )
        self.confidence_label.pack(fill=tk.X, pady=(2, 8))

        self.path_label = tk.Label(
            right_col,
            text="",
            font=("Segoe UI", 9),
            wraplength=320,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        self.path_label.pack(fill=tk.X)

        # ----------------------------------------------------
        # KARTA 2: CHATBOT INTERAKTIV & AUDIO PËR ÇDO MESAZH
        # ----------------------------------------------------
        chat_card = tk.Frame(
            main_container,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        chat_card.pack(fill=tk.BOTH, expand=True)

        chat_inner = tk.Frame(chat_card, bg=BG_CARD)
        chat_inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        chat_title = tk.Label(
            chat_inner,
            text="🤖 Weather Assistant Chat",
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=TEXT_MAIN,
            anchor="w"
        )
        chat_title.pack(fill=tk.X, pady=(0, 8))

        # Zona e skrollueshme për mesazhet me kartat e tyre moderne
        chat_outer_frame = tk.Frame(chat_inner, bg="#0D1322", relief="solid", borderwidth=1)
        chat_outer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.chat_canvas = tk.Canvas(chat_outer_frame, bg="#0D1322", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(chat_outer_frame, orient="vertical", command=self.chat_canvas.yview)
        
        self.messages_frame = tk.Frame(self.chat_canvas, bg="#0D1322")
        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )

        self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Shiriti i inputit të mesazheve
        input_frame = tk.Frame(chat_inner, bg=BG_CARD)
        input_frame.pack(fill=tk.X)

        self.chat_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg="#0D1322",
            fg=TEXT_MAIN,
            insertbackground="white",
            relief="solid",
            borderwidth=1
        )
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.chat_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            input_frame,
            text="Send ➤",
            command=self.send_message,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_PRIMARY,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.RIGHT)
        self.add_hover_effect(self.send_button, ACCENT_PRIMARY, ACCENT_HOVER)

        # Mesazhi fillestar mirëseardhës
        welcome_text = "Hello! I'm your Weather Assistant. Ask me anything about weather!"
        self.add_message("Bot", "Hello! 👋 I'm your Weather Assistant. Ask me anything about weather science or fogsmog!")
        self.tts.speak(welcome_text)

    def toggle_tts(self):
        self.tts.enabled = not self.tts.enabled
        if self.tts.enabled:
            self.tts_button.config(text="🔊 Voice: ON", fg=SUCCESS_GREEN)
        else:
            self.tts_button.config(text="🔇 Voice: OFF", fg=TEXT_MUTED)

    def add_hover_effect(self, widget, normal_bg, hover_bg):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

    def choose_image(self):
        image_path = filedialog.askopenfilename(
            title="Choose Weather Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All files", "*.*")]
        )
        if not image_path:
            return

        if not self.show_preview(image_path):
            return

        self.predict(image_path)

    def show_preview(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")
            image.thumbnail(PREVIEW_SIZE)
            self.preview_image = ImageTk.PhotoImage(image)

            self.image_label.configure(image=self.preview_image, text="", borderwidth=0)
            self.path_label.configure(text=f"Selected: {Path(image_path).name}")
            return True
        except Exception as error:
            messagebox.showerror("Image Error", str(error))
            return False

    def predict(self, image_path):
        try:
            result = predict_weather(image_path)
        except Exception as error:
            messagebox.showerror("Prediction Error", str(error))
            return

        self.current_weather = result
        weather = result["weather_class"]
        confidence = result["confidence"]

        self.result_label.configure(text=f"Weather: {weather}")
        self.confidence_label.configure(text=f"Confidence: {confidence:.2%}")

        response_text = f"Successfully classified image as {weather} with {confidence:.2%} confidence!"
        self.add_message("Bot", f"Successfully classified image as {weather} with {confidence:.2%} confidence! 🌦️")
        self.tts.speak(response_text)

    def add_message(self, sender, message):
        # Kornizë moderne për çdo mesazh (bubble effect)
        bubble_bg = "#161E31" if sender == "You" else "#101827"
        msg_frame = tk.Frame(self.messages_frame, bg=bubble_bg, highlightbackground="#1F293D", highlightthickness=1)
        msg_frame.pack(fill=tk.X, expand=True, pady=6, padx=10)

        inner_bubble = tk.Frame(msg_frame, bg=bubble_bg)
        inner_bubble.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        sender_color = ACCENT_BLUE if sender == "You" else SUCCESS_GREEN
        sender_lbl = tk.Label(
            inner_bubble,
            text=f"{sender}:",
            font=("Segoe UI", 9, "bold"),
            bg=bubble_bg,
            fg=sender_color,
            anchor="w"
        )
        sender_lbl.pack(fill=tk.X)

        text_label = tk.Label(
            inner_bubble,
            text=message,
            font=("Segoe UI", 10),
            bg=bubble_bg,
            fg=TEXT_MAIN,
            justify="left",
            anchor="w",
            wraplength=480
        )
        text_label.pack(fill=tk.X, pady=(2, 4))

        # Shto butonin audio (🔊 Dëgjo) vetëm për përgjigjet e Bot-it
        if sender == "Bot":
            audio_btn = tk.Button(
                inner_bubble,
                text="🔊 Dëgjo këtë",
                command=lambda m=message: self.tts.speak(m),
                font=("Segoe UI", 8, "bold"),
                bg="#1A233A",
                fg=SUCCESS_GREEN,
                activebackground=BORDER_COLOR,
                activeforeground=SUCCESS_GREEN,
                relief="solid",
                borderwidth=1,
                padx=8,
                pady=2,
                cursor="hand2"
            )
            audio_btn.pack(anchor="e", pady=(4, 0))

        # Skrollo automatikisht poshtë
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def send_message(self, event=None):
        message = self.chat_entry.get().strip()
        if not message:
            return "break" if event else None

        self.add_message("You", message)
        self.chat_entry.delete(0, tk.END)

        response = self.chatbot.get_response(message)
        self.add_message("Bot", response)
        self.tts.speak(response)
        
        if event:
            return "break"


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
