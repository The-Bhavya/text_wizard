from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from utils import allowed_file_type, summarize_text_from_file, analyze_sentiment_from_file
from flask import send_from_directory
import os
app = Flask(__name__)
app.secret_key = 'supersecretmre'


@app.route('/')
def index():
    flash('', 'info')
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    errors = []
    if request.method == 'POST':
        f = request.files['file']
        if not f:
            flash('No file part', 'error')
            errors.append('No file part')
        if f.filename == '':
            flash('No selected file', 'error')
            errors.append('No selected file')
        if not allowed_file_type(f.filename):
            flash('File type not allowed', 'error')
            errors.append('File type not allowed')
        if not errors:
            BASE_DIR = 'static/uploads'
            filepath = os.path.join(BASE_DIR, secure_filename(f.filename))
            f.save(filepath)
            # store the name in the session
            session['file'] = "/"+filepath
            flash('File uploaded successfully', 'success')
            return redirect(url_for('upload'))
    # all files in upload folder
    files = os.listdir('static/uploads')
    allowed_files = [file for file in files if allowed_file_type(file)]
    return render_template('upload.html', files=allowed_files, errors=" ".join(errors))

@app.route('/delete/<filename>')
def delete(filename):
    filepath = os.path.join('static/uploads', filename)
    os.remove(filepath)
    flash('File deleted successfully', 'success')
    return redirect(url_for('upload'))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('static/uploads', filename, as_attachment=True)

@app.route('/select/<filename>')
def select(filename):
    BASE_DIR = 'static/uploads'
    filepath = os.path.join(BASE_DIR, secure_filename(filename))
    session['file'] = "/"+filepath
    flash('File selected successfully', 'success')
    return redirect(url_for('upload'))

@app.route('/wizard', methods=['GET', 'POST'])
def wizard():
    selected_file = session.get('file', None)
    if not selected_file:
        flash('Please select a file first', 'error')
        return redirect(url_for('upload'))
    return render_template('wizard.html', file=selected_file)

@app.route('/summarizer', methods=['GET', 'POST'])
def summarizer():
    selected_file = session.get('file', None)
    if not selected_file:
        flash('Please select a file first', 'error')
        return redirect(url_for('upload'))
    ss, algo = 2, 'lsa'
    if request.method == 'POST':
        ss = request.form['size'] or 2
        algo = request.form['algorithm'] or 'lsa'
    print(f"current file is {selected_file}")
    result = summarize_text_from_file(selected_file[1:], summary_sentences=ss, algorithm=algo, language='english')
    print(result)
    return render_template('summarizer.html', 
        file=os.path.basename(selected_file),
        result=result
    )

@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    selected_file = session.get('file', None)
    if not selected_file:
        flash('Please select a file first', 'error')
        return redirect(url_for('upload'))
    print(f"current file is {selected_file}")
    bar_chart, pie_chart, results = analyze_sentiment_from_file(selected_file[1:])
    return render_template('sentiment.html',
        file=os.path.basename(selected_file),
        bar_chart=bar_chart.to_html(full_html=False),
        pie_chart=pie_chart.to_html(full_html=False),
        results=results
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)