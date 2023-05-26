# Code to upload to the server
# curl -X POST -F 'file=@/path/to/file.txt' http://localhost:5000/upload

# Code to download from the server
# curl -O http://localhost:5000/download/filename.txt

from flask import Flask, request, send_file, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session encryption

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        session['user_id'] = generate_user_id()  # Generate a unique user ID if not already present
    user_id = session['user_id']
    file = request.files['file']
    file.save(file.filename)
    print(f"User ID: {user_id}")
    return 'File uploaded successfully.'

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if 'user_id' not in session:
        session['user_id'] = generate_user_id()  # Generate a unique user ID if not already present
    user_id = session['user_id']
    print(f"User ID: {user_id}")
    return send_file(filename, as_attachment=True)

def generate_user_id():
    # Generate a unique user ID using a suitable algorithm or library
    # Here's a simple example using a counter
    if 'user_counter' not in session:
        session['user_counter'] = 0
    user_counter = session['user_counter']
    session['user_counter'] += 1
    return f"user_{user_counter}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
