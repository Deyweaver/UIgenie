<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Project Instructions

This project is a Flask-based AI application that generates CustomTkinter desktop UIs based on natural language descriptions. It uses the Gemini API to convert text descriptions into working Python code.

## Key Components

- Flask web application
- Google Generative AI integration (Gemini API)
- CustomTkinter UI generation
- Real-time UI preview functionality
- Code export capabilities

## Guidance

When working with this codebase:

1. **UI Generation Logic**: Focus on improving the code extraction and generation algorithms in the `get_gemini_response()` and `extract_code()` functions.

2. **Threading Concerns**: Be mindful of the thread safety issues with Tkinter. The application uses a separate thread for UI previews but this has inherent limitations.

3. **Error Handling**: Prioritize robust error handling when generating and executing dynamic code.

4. **CustomTkinter Knowledge**: Remember that this app specifically generates CustomTkinter UIs (not standard Tkinter), which has its own widget set and theming system.

5. **Prompt Engineering**: Help improve the prompt templates to get better results from the Gemini API.

6. **API Key Management**: Maintain security around the Gemini API key handling.

7. **Front-end Development**: The web interface uses HTML, CSS (Tailwind), and JavaScript for interaction.
