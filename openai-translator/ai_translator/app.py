import os, json
from flask import Flask, flash, url_for, request, abort, redirect, render_template, send_from_directory, session
from markupsafe import escape
from werkzeug.utils import secure_filename
# 设置跨域
from flask_cors import CORS, cross_origin

from translator import PDFTranslator
from model import OpenAIModel


app = Flask(__name__)

CORS(app, resources=r'/*')
# Set the secret key to some random bytes. Keep this really secret!
# 设置密钥
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# 上传文件保存路径
UPLOAD_FOLDER = '/Users/hughdwong/Temp/flaskTempUpload/'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 限制上传文件的大小，16M
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=escape(session['username']))
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        # username = request.args.get('username')
        password = request.form['password']
        if username=='admin' and password=='password':
            session['username'] = username
            return render_template('login-ok.html', username=username)
        else:
            error = 'Invalid username/password'
    elif request.method == 'GET':
        return render_template('login.html')
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', message=error, username=username)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/session_username')
def check_session():
    return session['username']

# 文件上传页面
@app.route('/upload', methods=['GET'])
def upload():
    return render_template('upload.html')

# 为上传的文件提供查看
@app.route('/uploads/<filename>', methods=['GET'])
def file_uploaded(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 对上传的文件进行翻译
@app.route('/api/v1/files/<filename>/translate', methods=['POST'])
def file_translate(filename):

    data = request.get_data()
    # 解析 data
    json_data = json.loads(data.decode('utf-8'))
    filetype = json_data.get('file_type')
    target_language = json_data.get('target_language')
    target_format = json_data.get('target_format')
    filefullname = filename + '.' + filetype

    newModel = OpenAIModel(model='gpt-3.5-turbo', api_key='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')
    translator = PDFTranslator(newModel)

    output_file_path = translator.translate_pdf(app.config['UPLOAD_FOLDER'] + filefullname, target_language, target_format)
    print(output_file_path)
    output_filename = os.path.basename(output_file_path)

    return {
        'status': 0,
        'msg': '',
        'data': output_filename
    }

# 检查允许的文件
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 上传文件
@app.route('/api/v1/file', methods=['POST'])
def file_upload():
    # check if the post request has the file part
    if 'file' not in request.files:
        return {
            'status': 1,
            'msg': 'No file part',
        }
    file = request.files['file']
    # if user does not select file, browser also submit an empty part without filename
    # 没有选择文件，浏览器会提交一个没有文件名的 空部分
    if file.filename == '':
        return {
            'status': 2,
            'msg': 'No selected file'
        }
    if file:
        if allowed_file(file.filename):
            # 对文件名进行安全检查，并转换
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return {
                'status': 0,
                'msg': 'success',
                'data': filename
            }
        else:
            return {
                'status': 3,
                'msg': 'Not allowed file type'
            }
    return {
        'status': 999,
        'msg': ''
    }

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run(debug=True)