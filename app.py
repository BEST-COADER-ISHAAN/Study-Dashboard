from flask import Flask, render_template, send_from_directory, request, redirect
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

STUDY_MATERIAL_PATH = "Study Material"

# Create Study Material folder if it doesn't exist
if not os.path.exists(STUDY_MATERIAL_PATH):
    os.makedirs(STUDY_MATERIAL_PATH)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/explorer')
def explorer():
    def get_directory_contents(path):
        contents = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            relative_path = os.path.relpath(item_path, STUDY_MATERIAL_PATH)
            
            if is_dir:
                contents.append({
                    'name': item,
                    'is_dir': True,
                    'path': relative_path,
                    'contents': get_directory_contents(item_path)
                })
            else:
                contents.append({
                    'name': item,
                    'is_dir': False,
                    'path': relative_path,
                    'is_pdf': item.lower().endswith('.pdf')
                })
        return sorted(contents, key=lambda x: (not x['is_dir'], x['name'].lower()))

    contents = get_directory_contents(STUDY_MATERIAL_PATH)
    return render_template('explorer.html', contents=contents)

@app.route('/study-material/<path:filepath>')
def serve_file(filepath):
    return send_from_directory(STUDY_MATERIAL_PATH, filepath)

@app.route('/create-folder', methods=['POST'])
def create_folder():
    folder_path = request.form.get('folder_path')
    parent_path = request.form.get('parent_path', '')
    if folder_path:
        full_path = os.path.join(STUDY_MATERIAL_PATH, parent_path, folder_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
    return redirect('/explorer')

@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/explorer')
    
    file = request.files['file']
    parent_path = request.form.get('parent_path', '')
    
    if file.filename:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(STUDY_MATERIAL_PATH, parent_path, filename)
        file.save(upload_path)
    
    return redirect('/explorer')

if __name__ == '__main__':
    app.run(debug=True) 