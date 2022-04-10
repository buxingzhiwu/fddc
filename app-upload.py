# -*- coding: utf-8 -*-
import os
from flask import Flask, request, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename, redirect
import subprocess
import pandas as pd

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


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    ifsuccess = 1
    filename = None
    if request.method == 'POST':
        file = request.files['file']
        try:
            if allowed_file(file.filename):
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    file_url = url_for('uploaded_file', filename=filename)
                    ifsuccess = 2
            else:
                ifsuccess = 3
        except:
            ifsuccess = 4
    return render_template('test.html', ifsuccess=ifsuccess, filename=filename)


@app.route('/Extraction')
def extraction():
    # ht_dir = os.path.dirname(os.path.abspath(__file__)) + '\\modelfile\\ht'
    # cmd = 'python ' + ht_dir + '/run_ht.py'
    # res = subprocess.call(cmd.split())
    # print("run_ht.py exit_code:", res)
    submit = os.path.dirname(os.path.abspath(__file__)) + '\\modelfile\\submit'
    datas = pd.read_csv(submit + '/hetong.txt',sep='\t')
    datas = datas.values.tolist()
    return render_template('result.html', datas=datas)


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
