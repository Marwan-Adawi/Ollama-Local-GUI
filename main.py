import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext, messagebox
import requests
import json
import threading
import queue
import os
import darkdetect

class OllamaChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chat")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure appearance and theme
        ctk.set_appearance_mode("system")  # Follows system theme (dark/light)
        ctk.set_default_color_theme("blue")  # Primary color theme
        
        self.selected_model = ctk.StringVar()
        self.system_prompt = ctk.StringVar()
        self.prompt_preset = ctk.StringVar(value="casual")
        self.message_queue = queue.Queue()
        self.is_processing = False
        self.chat_history = []
        
        # Define colors
        self.colors = {
            "user_msg_bg": "#e3f2fd",  # Light blue for user messages
            "ai_msg_bg": "#f5f5f5",    # Light gray for AI messages
            "user_msg_bg_dark": "#1e3a5f",  # Darker blue for user messages in dark mode
            "ai_msg_bg_dark": "#2d2d2d",    # Darker gray for AI messages in dark mode
        }
        
        # Define preset system prompts
        self.preset_prompts = {
            "casual": "You are a helpful, friendly AI assistant. Engage in a casual conversation, respond to questions clearly and concisely, and feel free to show some personality.",
            "coding": "You are a helpful, friendly Coding assistant. respond to questions with clear, accurate, and efficient code solutions with explanations, Focus on best practices and help fix any issues in the code. Feel free to show some personality.",
            "creative": "You are a creative writing assistant. Help generate imaginative content, develop ideas, and provide feedback on writing with a focus on creativity and style.",
            "academic": "You are an academic assistant. Provide detailed, well-researched information with proper context and nuance. Focus on accuracy and educational value.",
            "custom": ""  # For custom user input
        }
        
        self.create_widgets()
        self.load_models()
        
        # Set up periodic check for new messages
        self.root.after(100, self.process_message_queue)
    
    def create_widgets(self):
        # Main frame with two columns
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create two columns - sidebar and chat area
        self.sidebar = ctk.CTkFrame(self.main_frame, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)  # Prevent the frame from shrinking
        
        self.chat_column = ctk.CTkFrame(self.main_frame)
        self.chat_column.pack(side="right", fill="both", expand=True)
        
        # === SIDEBAR CONTENT ===
        # App logo/title
        self.title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Ollama Chat", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(pady=(20, 25))
        
        # Model selection frame
        self.model_frame = ctk.CTkFrame(self.sidebar)
        self.model_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        self.model_label = ctk.CTkLabel(self.model_frame, text="Select Model:")
        self.model_label.pack(anchor="w", pady=(10, 5))
        
        # Model selection row with dropdown and refresh button
        self.model_selection_row = ctk.CTkFrame(self.model_frame)
        self.model_selection_row.pack(fill="x")
        
        self.model_combobox = ctk.CTkComboBox(
            self.model_selection_row, 
            variable=self.selected_model,
            state="readonly",
            width=160
        )
        self.model_combobox.pack(side="left", pady=5)
        
        self.refresh_button = ctk.CTkButton(
            self.model_selection_row, 
            text="↻", 
            width=30,
            command=self.load_models,
            fg_color="transparent",
            border_width=1
        )
        self.refresh_button.pack(side="right", padx=(5, 0), pady=5)
        
        # System prompt presets section
        self.preset_frame = ctk.CTkFrame(self.sidebar)
        self.preset_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        self.preset_label = ctk.CTkLabel(self.preset_frame, text="System Prompt Presets:")
        self.preset_label.pack(anchor="w", pady=(10, 5))
        
        # Radio buttons for presets
        self.presets = [
            ("Casual Chat", "casual"),
            ("Coding Assistant", "coding"),
            ("Creative Writing", "creative"),
            ("Academic Helper", "academic"),
            ("Custom", "custom")
        ]
        
        for text, value in self.presets:
            rb = ctk.CTkRadioButton(
                self.preset_frame,
                text=text,
                value=value,
                variable=self.prompt_preset,
                command=self.update_system_prompt
            )
            rb.pack(anchor="w", padx=20, pady=5)
        
        # System prompt entry
        self.prompt_entry_frame = ctk.CTkFrame(self.sidebar)
        self.prompt_entry_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.prompt_entry_label = ctk.CTkLabel(self.prompt_entry_frame, text="System Prompt:")
        self.prompt_entry_label.pack(anchor="w", pady=(10, 5))
        
        self.system_prompt_entry = ctk.CTkTextbox(
            self.prompt_entry_frame, 
            height=80,
            wrap="word"
        )
        self.system_prompt_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        # Theme toggle
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:")
        self.appearance_mode_label.pack(pady=(20, 0))
        
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode
        )
        self.appearance_mode_menu.pack(pady=(10, 20))
        self.appearance_mode_menu.set("System")
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.sidebar)
        self.status_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status:")
        self.status_label.pack(side="left", padx=5)
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame, 
            text="Ready",
            text_color="green"
        )
        self.status_indicator.pack(side="right", padx=5)
        
        # === CHAT COLUMN CONTENT ===
        # Chat display area
        self.chat_frame = ctk.CTkFrame(self.chat_column)
        self.chat_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame, 
            wrap="word",
            font=ctk.CTkFont(size=12),
            height=40
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display.configure(state="disabled")
        
        # User input area
        self.input_frame = ctk.CTkFrame(self.chat_column)
        self.input_frame.pack(fill="x", side="bottom")
        
        self.user_input = ctk.CTkTextbox(
            self.input_frame, 
            wrap="word", 
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.user_input.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        self.user_input.bind("<Return>", self.handle_return)
        self.user_input.bind("<Shift-Return>", self.handle_shift_return)
        
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="Send",
            command=self.send_message,
            width=100,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.send_button.pack(side="right", padx=(5, 10), pady=10)
        
        # Initialize with default prompt
        self.update_system_prompt()

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
    
    def update_system_prompt(self, *args):
        preset = self.prompt_preset.get()
        if preset in self.preset_prompts:
            prompt_text = self.preset_prompts[preset]
            self.system_prompt.set(prompt_text)
            
            # Update the text in the textbox
            self.system_prompt_entry.delete("0.0", "end")
            if preset != "custom":
                self.system_prompt_entry.insert("0.0", prompt_text)
    
    def get_system_prompt(self):
        # Get the content from the textbox
        return self.system_prompt_entry.get("0.0", "end").strip()
    
    def load_models(self):
        self.set_status("Loading models...", "orange")
        
        def _load():
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [model["name"] for model in data["models"]]
                    self.root.after(0, lambda: self.update_models(models))
                else:
                    error_code = response.status_code
                    self.root.after(0, lambda: self.set_status(f"Error: {error_code}", "red"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.set_status(f"Error: {error_msg}", "red"))
        
        threading.Thread(target=_load).start()
    
    def update_models(self, models):
        if models:
            self.model_combobox.configure(values=models)
            self.model_combobox.set(models[0])
            self.set_status(f"Loaded {len(models)} models", "green")
        else:
            self.model_combobox.configure(values=["deepseek-r1:1.5b"])
            self.model_combobox.set("deepseek-r1:1.5b")
            self.set_status("No models found, using default", "orange")
    
    def set_status(self, text, color="green"):
        self.status_indicator.configure(text=text, text_color=color)
    
    def handle_return(self, event):
        if not event.state & 0x1:  # Check if shift is not pressed
            self.send_message()
            return 'break'  # Prevents the default behavior (newline)
        return None  # Allow default behavior
    
    def handle_shift_return(self, event):
        # Allow default behavior (newline) when Shift+Enter is pressed
        return None
    
    def send_message(self):
        user_message = self.user_input.get("0.0", "end").strip()
        if not user_message:
            return
        
        model = self.selected_model.get() or "deepseek-r1:1.5b"
        system = self.get_system_prompt()
        
        # First clear the input field to prevent double-sending
        self.user_input.delete("0.0", "end")
        
        # Display user message with styling
        self.display_user_message(user_message)
        
        # Start a new message for the AI response
        self.start_ai_response()
        
        # Update status and disable input while processing
        self.set_status("Thinking...", "orange")
        self.is_processing = True
        
        # Log to console for debugging
        print(f"Sending message: '{user_message}' to model: {model}")
        
        # Use a thread to send the request
        threading.Thread(target=self.process_message, args=(user_message, model, system)).start()
    
    def display_user_message(self, message):
        """Display user message with styling"""
        self.chat_display.configure(state="normal")
        
        # Add padding if not the first message
        if self.chat_display.get("1.0", "end").strip():
            self.chat_display.insert("end", "\n\n")
        
        # Use bold font for user label
        self.chat_display.insert("end", "You: ", font=ctk.CTkFont(size=12, weight="bold"))
        
        # Add the message
        self.chat_display.insert("end", message)
        
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def start_ai_response(self):
        """Initialize an AI response with styling"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "\n\n")
        
        # Add AI icon/label with bold font
        self.chat_display.insert("end", "AI: ", font=ctk.CTkFont(size=12, weight="bold"))
        
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def update_ai_response(self, text):
        """Update the current AI response with styling"""
        self.chat_display.configure(state="normal")
        
        # Add the new text
        self.chat_display.insert("end", text)
        
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def process_message(self, message, model, system_prompt):
        url = "http://localhost:11434/api/chat"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": True
        }
        
        if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})
        
        try:
            response = requests.post(url, json=payload, stream=True)
            response_text = ""
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    if "message" in data and "content" in data["message"]:
                        chunk = data["message"]["content"]
                        response_text += chunk
                        self.message_queue.put(("append", chunk))
            
            # Signal completion
            self.message_queue.put(("complete", None))
            
        except Exception as e:
            self.message_queue.put(("error", str(e)))
    
    def process_message_queue(self):
        try:
            while not self.message_queue.empty():
                action, data = self.message_queue.get_nowait()
                
                if action == "append":
                    self.update_ai_response(data)
                elif action == "complete":
                    self.is_processing = False
                    self.set_status("Ready", "green")
                elif action == "error":
                    self.is_processing = False
                    self.set_status(f"Error", "red")
                    self.update_ai_response(f"\nError: {data}")
                    
        except queue.Empty:
            pass
        
        # Schedule the next check
        self.root.after(100, self.process_message_queue)

if __name__ == "__main__":
    try:
        ctk.set_default_color_theme("blue")
        root = ctk.CTk()
        app = OllamaChatApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
