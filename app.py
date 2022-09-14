from operator import methodcaller
from flask import Flask, render_template, url_for, redirect, request, send_from_directory
# from flask_wtf import FlaskForm
# from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
import re
# from wtforms.validators import InputRequired

from clean_func import cleaned_and_stemmed, remove_punct_regex 


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/input', methods=['GET', 'POST'])
def input_text():
    if request.method == 'POST':
        text_input = request.form.get('text_input')
        return '''
                  <h3>Your text: {}</h3>
                  <h3>Cleaned text: {}</h3>'''.format(text_input, remove_punct_regex(text_input))
    return '''
              <form method="POST">
                  <div><label>Input your text: <input type="text" name="text_input"></label></div>
                  <input type="submit" value="Submit">
              </form>'''

@app.route('/upload', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            process_file('csv', 'cleaned_and_stemmed', os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('text_app.html')

# @app.route('/download', methods=['GET', 'POST'])
# def download(filename):
#     if request.methods == 'POST':
#         return redirect(url_for('uploaded_file', filename=filename))
#     return render_template('text_app.html')

def process_file(file_type, process, path, filename):
    if file_type == 'csv':
        if process == 'cleaned_and_stemmed':
            cleaned_and_stemmed(path, filename)
        if process == 'cleaned':
            pass
    if file_type == 'text':
        pass
        
@app.route('/uploads/<filename>', methods = ["GET"])
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)
    # return render_template('success.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)