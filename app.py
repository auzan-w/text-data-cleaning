from operator import methodcaller
from flask import Flask, render_template, url_for, redirect, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
import pandas as pd
# from wtforms.validators import InputRequired

from clean_func import clean_and_stem_text, clean_csv, clean_and_stem_csv, clean_text


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
        option = request.form.get('option')
        text_cleaned = clean_text(text_input)
        
        
        # if option == 1 or option == None:
        #     text_cleaned = clean_text(text_input)
            
        # if option == 2:
        #     text_cleaned = clean_and_stem_text(text_input)
        
        # Save to db
        database_txt(text_input, text_cleaned)
        
        return '''
                  <h3>Your text: {}</h3>
                  <h3>Cleaned text: {}</h3>'''.format(text_input, text_cleaned)
       
    return render_template('text_input.html')

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
            
            process_file('csv', 'clean_and_stem_csv', os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('text_app.html')

def process_file(file_type, process, path, filename):
    if file_type == 'csv':
        if process == 'clean_and_stem_csv':
            clean_and_stem_csv(path, filename)
            database_csv(filename)
        if process == 'clean_csv':
            clean_csv(path, filename)
    # if file_type == 'text':
    #     if process == 'clean_and_stem_text':
    #         clean_and_stem_text(path, filename)
    #         database_csv(filename)
    #     if process == 'clean_text':
    #         clean_text(path, filename)
        
def database_txt(text, result):
    conn = sqlite3.connect("cleaned.db")
    cursor = conn.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS cleaned_text_input (input, cleaned)""")
    cursor.execute("""INSERT INTO cleaned_text_input (input, cleaned) VALUES (?,?)""",(text, result))
    
    conn.commit()
    cursor.close()
    conn.close()
    
def database_csv(data):
    df = pd.read_csv("downloads/" + data, header=0)
    
    conn = sqlite3.connect("cleaned.db")
    cursor = conn.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS cleaned_text_csv (input, tweet_clean, Tweet_processed)""")
    
    df.to_sql('cleaned_text_csv', conn, if_exists = 'append', index = False)


@app.route('/uploads/<filename>', methods = ["GET", "POST"])
def uploaded_file(filename):
    if request.method=="POST":   
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)
    return render_template('download.html')
    # return render_template('success.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)