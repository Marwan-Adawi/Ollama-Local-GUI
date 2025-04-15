import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
import queue

class OllamaChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chat")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        self.selected_model = tk.StringVar()
        self.system_prompt = tk.StringVar()
        self.prompt_preset = tk.StringVar(value="casual")
        self.message_queue = queue.Queue()
        self.is_processing = False
        
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
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        
        # Top frame for model selection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Model selection
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_combobox = ttk.Combobox(top_frame, textvariable=self.selected_model, state="readonly", width=20)
        self.model_combobox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh models button
        refresh_button = ttk.Button(top_frame, text="↻", width=3, command=self.load_models)
        refresh_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Prompt preset selection frame
        preset_frame = ttk.LabelFrame(main_frame, text="System Prompt Presets", padding=(5, 5))
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create radio buttons for preset selection
        modes = [
            ("Casual Chat", "casual"),
            ("Coding Assistant", "coding"),
            ("Creative Writing", "creative"),
            ("Academic Helper", "academic"),
            ("Custom", "custom")
        ]
        
        for i, (text, value) in enumerate(modes):
            rb = ttk.Radiobutton(
                preset_frame, 
                text=text,
                value=value,
                variable=self.prompt_preset,
                command=self.update_system_prompt
            )
            rb.grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=2)
        
        # System prompt entry
        prompt_frame = ttk.Frame(main_frame)
        prompt_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(prompt_frame, text="System Prompt:").pack(side=tk.LEFT, padx=(0, 5))
        system_prompt_entry = ttk.Entry(prompt_frame, textvariable=self.system_prompt, width=60)
        system_prompt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Chat display area
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=("Arial", 10))
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # User input area
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.user_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=3, font=("Arial", 10))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.handle_return)
        self.user_input.bind("<Shift-Return>", self.handle_shift_return)
        
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize with default prompt
        self.update_system_prompt()
    
    def update_system_prompt(self, *args):
        preset = self.prompt_preset.get()
        if preset in self.preset_prompts:
            prompt_text = self.preset_prompts[preset]
            self.system_prompt.set(prompt_text)
            
            # If custom is selected, clear the field for user input
            if preset == "custom":
                self.system_prompt.set("")
    
    def load_models(self):
        self.status_var.set("Loading models...")
        
        def _load():
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [model["name"] for model in data["models"]]
                    self.root.after(0, lambda: self.update_models(models))
                else:
                    self.root.after(0, lambda: self.status_var.set(f"Error: {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        
        threading.Thread(target=_load).start()
    
    def update_models(self, models):
        if models:
            self.model_combobox['values'] = models
            self.model_combobox.current(0)
            self.status_var.set(f"Loaded {len(models)} models")
        else:
            self.model_combobox['values'] = ["deepseek-r1:1.5b"]
            self.model_combobox.current(0)
            self.status_var.set("No models found, using default")
    
    def handle_return(self, event):
        if not event.state & 0x1:  # Check if shift is not pressed
            self.send_message()
            return 'break'  # Prevents the default behavior (newline)
        return None  # Allow default behavior
    
    def handle_shift_return(self, event):
        # Allow default behavior (newline) when Shift+Enter is pressed
        return None
    
    def send_message(self):
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            return
        
        model = self.selected_model.get() or "deepseek-r1:1.5b"
        system = self.system_prompt.get()
        
        self.append_to_chat("You: " + user_message)
        self.user_input.delete("1.0", tk.END)
        
        # Start a new line for the AI response
        self.append_to_chat("AI: ", newline=True)
        
        # Update status and disable input while processing
        self.status_var.set("Thinking...")
        self.is_processing = True
        
        # Use a thread to send the request
        threading.Thread(target=self.process_message, args=(user_message, model, system)).start()
    
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
                    self.append_to_chat(data, append_only=True)
                elif action == "complete":
                    self.is_processing = False
                    self.status_var.set("Ready")
                    # Add a newline for the next message
                    self.append_to_chat("", newline=True)
                elif action == "error":
                    self.is_processing = False
                    self.status_var.set(f"Error: {data}")
                    self.append_to_chat(f"Error: {data}", newline=True)
                    
        except queue.Empty:
            pass
        
        # Schedule the next check
        self.root.after(100, self.process_message_queue)
    
    def append_to_chat(self, text, newline=False, append_only=False):
        self.chat_display.config(state=tk.NORMAL)
        
        if newline and not append_only:
            self.chat_display.insert(tk.END, "\n\n")
        
        self.chat_display.insert(tk.END, text)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = OllamaChatApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")