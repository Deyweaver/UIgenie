# CustomTkinter AI UI Generator

This Flask-based AI application allows you to create beautiful CustomTkinter desktop UIs just by describing them in natural language. Powered by Google's Gemini API, it instantly generates Python code, provides a live preview, and lets you interactively refine your design through conversation.

## Features

- **Natural Language UI Generation**: Describe your UI in plain English (e.g., "make a dark-themed login screen with a password field")
- **Live Preview**: Instantly see your generated UI in action
- **Interactive Refinement**: Chat with the AI to tweak your design ("make the button red" or "move it to the right")
- **Custom Instructions**: Add specific guidelines to direct how the AI builds your UI
- **Code Export**: Download the complete Python code to use as a foundation for your project

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get a Gemini API key from [Google AI Studio](https://ai.google.dev/)
4. Add your API key to the `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```
   python app.py
   ```
6. Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

1. **Describe Your UI**: Enter a description of the UI you want to create in the input field.
2. **Generate UI**: Click the "Generate UI" button to create your CustomTkinter interface.
3. **Refine Your Design**: Use the chat to request changes or improvements to your UI.
4. **Add Custom Instructions**: Set specific guidelines for how the AI should generate UIs.
5. **Export Code**: Download the Python code to use in your own projects.

## Requirements

- Python 3.7+
- Flask
- Google Generative AI Python SDK
- CustomTkinter
- Pillow
- python-dotenv

## Example Prompts

- "Create a dark mode app with a sidebar navigation and main content area"
- "Generate a login form with username and password fields, remember me checkbox, and login button"
- "Make a file browser interface with a tree view and preview pane"
- "Design a settings page with toggles for dark mode, notifications, and sound"

## Limitations

- The AI may occasionally generate code that needs minor adjustments
- Complex UI layouts might require iterative refinements
- The preview functionality depends on your local environment setup
