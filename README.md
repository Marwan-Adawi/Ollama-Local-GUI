# Ollama Chat Application

A customizable chat interface for interacting with Ollama models using Python and Tkinter.

## Overview

This application provides a user-friendly GUI for chatting with locally hosted large language models through Ollama. You can customize the system prompt and easily switch between different models.

## Prerequisites

- Python 3.8 or higher
- Ollama installed on your system
- Downloaded model(s) in Ollama

## Installation

### 1. Install Ollama

Download and install Ollama from the official website:
[https://ollama.com/](https://ollama.com/)

### 2. Download a Model

After installing Ollama, download at least one model using the command line:

```bash
ollama pull llama2
```

Replace `llama2` with any model you prefer (e.g., `mistral`, `phi`, `gemma`, etc.)

### 3. Install Required Python Dependencies

```bash
pip install tkinter customtkinter requests threading queue
```

or

```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure Ollama is running in the background
2. Run the Python script:
```bash
python ollama_chat_app.py
```

## Creating an Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed ollama_chat_app.py
```

The executable will be located in the `dist` folder.

## Usage

1. Start Ollama in the background
2. Launch the application
3. Select your desired model from the dropdown menu
4. Type messages in the input field and press Enter or click Send
5. View responses in the chat window

## Customization

### Changing the System Prompt

The system prompt determines how the AI responds. To modify it:
1. Click on the "Settings" button
2. Edit the text in the system prompt field
3. Click "Save"

### Switching Models

To use a different model:
1. Ensure you have downloaded the model using Ollama
2. Select it from the model dropdown menu in the application

## Troubleshooting

- **Application can't connect to Ollama**: Make sure Ollama is running in the background
- **Model not appearing in list**: Download the model first with `ollama pull [model_name]`
- **Slow responses**: Some models require more resources. Try using a smaller model

## File Structure

```
ollama-chat/
├── ollama_chat_app.py       # Main application code
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Requirements.txt

```
tkinter
customtkinter
requests
```

## Notes

- The application runs locally and doesn't send data to external servers (beyond what Ollama itself may do)
- Performance depends on your hardware and the model size
- Make sure to start Ollama before launching the application

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.