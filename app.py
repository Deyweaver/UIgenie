import os
from flask import Flask, render_template, request, jsonify, Response
import google.generativeai as genai
from dotenv import load_dotenv
import tkinter as tk
import customtkinter as ctk
import io
import sys
from PIL import ImageGrab
import threading
import time
import json
import re
import tempfile
import subprocess
import shutil
import atexit

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found. Please set it in a .env file.")

app = Flask(__name__)

class AppState:
    def __init__(self):
        self.ui_code = None
        self.ui_window = None
        self.ui_thread = None
        self.ui_process = None
        self.custom_instructions = ""
        self.conversation_history = []
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file_path = os.path.join(self.temp_dir, "ui_preview.py")
        
    def cleanup(self):
        """Clean up temporary files and processes"""
        if self.ui_process:
            try:
                self.ui_process.terminate()
            except:
                pass
        
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                print(f"Failed to clean up temporary directory: {e}")
        
app_state = AppState()

# Register cleanup function to run on exit
atexit.register(app_state.cleanup)

def get_gemini_response(prompt, stream=False):
    """Get a response from Gemini model
    
    If stream=True, this will return a generator that yields chunks of text
    Otherwise, it returns the complete response
    """
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not set. Please add it to your .env file.", 400
        
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        conversation_context = "\n".join([
            f"User: {message['content']}" if message['role'] == 'user' else f"Assistant: {message['content']}"
            for message in app_state.conversation_history
        ])
        
        # Add custom instructions to the prompt
        full_prompt = f"""
        You are an expert CustomTkinter UI developer. Your task is to generate Python code for a desktop application UI based on user descriptions.
        
        Custom instructions:
        {app_state.custom_instructions}
        
        Previous conversation:
        {conversation_context}
        
        User request: {prompt}
        
        Please provide the complete CustomTkinter code for this UI. The code should be complete, functional, and ready to run.
        Only include the Python code (no explanations). The code should:
        1. Use the CustomTkinter library
        2. Create a complete, standalone application
        3. Include all necessary imports
        4. Be ready to execute without modification
        5. Define a main app window variable called 'app'
        """
        
        if stream:
            response = model.generate_content(full_prompt, stream=True)
            # Return the streaming response
            return response
        else:
            response = model.generate_content(full_prompt)
            
            if not hasattr(response, 'text'):
                print(f"Unexpected response format: {response}")
                return "Unexpected response format from Gemini API", 500
                
            extracted_code = extract_code(response.text)
            
            if not extracted_code or not isinstance(extracted_code, str):
                return "Failed to extract valid code from the API response", 500
                
            return extracted_code
    except Exception as e:
        print(f"Error in get_gemini_response: {str(e)}")
        return str(e), 500

def extract_code(text):
    """Extract code blocks from Gemini response"""
    if not text or not isinstance(text, str):
        print(f"Invalid text provided to extract_code: {text}")
        return ""
    
    # First, try to extract code blocks with markdown formatting
    # Match with or without language identifier and with or without newline after opening ```
    code_blocks = re.findall(r'```(?:python)?(?:\n|\r\n)?(.*?)```', text, re.DOTALL)
    
    if code_blocks:
        # Take the first code block
        code = code_blocks[0].strip()
        print(f"Extracted code block (first {min(50, len(code))} chars): {code[:50]}...")
        return code
    
    # If no code blocks with triple backticks found, try single backtick blocks
    code_blocks = re.findall(r'`(.*?)`', text, re.DOTALL)
    if code_blocks:
        # Combine all code blocks
        code = '\n'.join([block.strip() for block in code_blocks])
        print(f"Extracted from single backticks (first {min(50, len(code))} chars): {code[:50]}...")
        return code
    
    # If no code blocks found, return the entire text but warn about it
    print(f"No code blocks found, using entire text (first {min(50, len(text))} chars): {text[:50]}...")
    return text

def save_ui_code(code):
    """Save the UI code to a temporary file"""
    if not isinstance(code, str) or not code.strip():
        print("Error: Empty or invalid code provided")
        return False
    
    try:
        # Terminate any existing process
        if app_state.ui_process and app_state.ui_process.poll() is None:
            try:
                app_state.ui_process.terminate()
                time.sleep(0.5)  # Give it time to terminate
            except Exception as e:
                print(f"Error terminating previous UI process: {e}")
        
        # Write code to temporary file
        with open(app_state.temp_file_path, 'w') as f:
            f.write(code)
        
        print(f"Saved UI code to temporary file: {app_state.temp_file_path}")
        return True
    except Exception as e:
        print(f"Error saving UI code: {e}")
        return False

def run_ui_preview():
    """Run the UI preview from the saved temporary file"""
    if not os.path.exists(app_state.temp_file_path):
        print("Error: No UI code file found")
        return False
    
    try:
        # Start a new process to run the UI code
        python_executable = sys.executable
        app_state.ui_process = subprocess.Popen(
            [python_executable, app_state.temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the process a moment to start
        time.sleep(1)
        
        # Check if the process is still running
        if app_state.ui_process.poll() is None:
            print(f"UI preview started successfully (PID: {app_state.ui_process.pid})")
            return True
        else:
            stdout, stderr = app_state.ui_process.communicate()
            print(f"UI process exited with code {app_state.ui_process.returncode}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
    except Exception as e:
        print(f"Error launching UI preview: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    stream_mode = data.get('stream', False)
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Add user message to conversation history
    app_state.conversation_history.append({
        "role": "user",
        "content": prompt
    })
    
    if not stream_mode:
        # Generate UI code based on prompt (non-streaming mode)
        response = get_gemini_response(prompt)
        
        # Check if response is a tuple (error case)
        if isinstance(response, tuple):
            error_message, status_code = response
            return jsonify({"error": error_message}), status_code
        
        # Ensure we have a string
        code = str(response) if response is not None else ""
        app_state.ui_code = code
        
        # Add assistant response to conversation history
        app_state.conversation_history.append({
            "role": "assistant",
            "content": f"Generated UI code:\n```python\n{code}\n```"
        })
        
        # Save the code to a temporary file (but don't run it yet)
        if code.strip():
            save_ui_code(code)
        
        return jsonify({
            "code": code,
            "success": True,
            "message": "Code generated successfully. Click Preview to run the UI."
        })
    else:
        # Return a flag to indicate successful start of streaming
        return jsonify({
            "success": True,
            "streaming": True,
            "message": "Streaming started"
        })

@app.route('/generate-stream', methods=['POST'])
def generate_stream():
    """Stream the generated code as it's being created"""
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    def stream_generator():
        try:
            # Get streaming response
            streaming_response = get_gemini_response(prompt, stream=True)
            full_text = ""
            
            # Stream the chunks as they arrive
            for chunk in streaming_response:
                if hasattr(chunk, 'text'):
                    chunk_text = chunk.text
                    full_text += chunk_text
                    # Extract any code from accumulated text so far
                    current_code = extract_code(full_text)
                    yield f"data: {json.dumps({'chunk': chunk_text, 'code': current_code})}\n\n"
            
            # Final extracted code
            final_code = extract_code(full_text)
            
            # Store the complete code
            app_state.ui_code = final_code
            
            # Add to conversation history
            app_state.conversation_history.append({
                "role": "assistant",
                "content": f"Generated UI code:\n```python\n{final_code}\n```"
            })
            
            # Save the code to a temporary file
            if final_code.strip():
                save_ui_code(final_code)
                
            # Send a completion message
            yield f"data: {json.dumps({'complete': True, 'code': final_code})}\n\n"
        except Exception as e:
            print(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_generator(), mimetype='text/event-stream')

@app.route('/update-instructions', methods=['POST'])
def update_instructions():
    data = request.json
    app_state.custom_instructions = data.get('instructions', '')
    return jsonify({"success": True})

@app.route('/export-code', methods=['GET'])
def export_code():
    if not app_state.ui_code:
        return jsonify({"error": "No code has been generated yet"}), 400
        
    return jsonify({"code": app_state.ui_code})

@app.route('/run-preview', methods=['POST'])
def run_preview():
    if not app_state.ui_code:
        return jsonify({"error": "No code has been generated yet"}), 400
    
    success = run_ui_preview()
    if success:
        return jsonify({
            "success": True,
            "message": "UI preview launched successfully. The preview window should now be open."
        })
    else:
        return jsonify({
            "success": False,
            "error": "Failed to launch UI preview. Check server logs for details."
        }), 500

@app.route('/preview-status', methods=['GET'])
def preview_status():
    if app_state.ui_process:
        is_running = app_state.ui_process.poll() is None
        return jsonify({
            "isRunning": is_running,
            "pid": app_state.ui_process.pid if is_running else None
        })
    else:
        return jsonify({
            "isRunning": False,
            "pid": None
        })
        
@app.route('/stop-preview', methods=['POST'])
def stop_preview():
    if app_state.ui_process and app_state.ui_process.poll() is None:
        try:
            app_state.ui_process.terminate()
            time.sleep(0.5)
            if app_state.ui_process.poll() is None:
                app_state.ui_process.kill()
            return jsonify({"success": True, "message": "Preview stopped successfully"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": True, "message": "No preview is currently running"})

if __name__ == '__main__':
    app.run(debug=True)
