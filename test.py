# -*- coding: utf-8 -*-
import os
from flask import Flask, request, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename, redirect


ALLOWED_EXTENSIONS = set(['html'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd() + '\\data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/manage')
def manage_file():
    files_list = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('list.html', files_list=files_list)

@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('manage_file'))

if __name__ == '__main__':
    app.run()
