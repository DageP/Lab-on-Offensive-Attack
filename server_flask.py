from flask import Flask, request, send_file

# Code to upload to the server
# curl -X POST -F 'file=@/path/to/file.txt' http://localhost:5000/upload

# Code to download from the server
# curl -O http://localhost:5000/download/filename.txt

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(file.filename)
    return 'File uploaded successfully.'

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
