from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import requests
from obs import ObsClient
import logging
from datetime import datetime
from pymongo import MongoClient

base_url = "http://123.249.18.228:5000"  # 修改为云服务器的实际URL

app = Flask(__name__)
app.secret_key = 'caicaizheshisha'

# MongoDB配置
username = 'rwuser'
password = '022000Ql!'
hostname = '120.46.54.234'
port = 8635
database_name = 'test'
MONGO_URI = f"mongodb://{username}:{password}@{hostname}:{port}/{database_name}?authSource=admin"

# 创建MongoDB客户端
client = MongoClient(MONGO_URI)
db = client[database_name]  # 获取数据库对象

# OBS配置
OBS_ACCESS_KEY_ID = 'D2RWFCWOQQRMMZ0JGRK1'
OBS_SECRET_ACCESS_KEY = 'B4LXgF10cWE9gNMIK93wWHRu5C161B1BAFIM2ZHc'
OBS_ENDPOINT = 'obs.cn-north-4.myhuaweicloud.com'
OBS_BUCKET_NAME = 'yunjs'

obs_client = ObsClient(
    access_key_id=OBS_ACCESS_KEY_ID,
    secret_access_key=OBS_SECRET_ACCESS_KEY,
    server=OBS_ENDPOINT
)

logging.basicConfig(level=logging.DEBUG)

login_logs = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 确保username和password作为字符串处理
        print(f"Trying to log in with username: {username} and password: {password}")

        # 查询MongoDB中的用户凭证
        user = db.user.find_one({"id": str(username), "passwd": str(password)})

        if user:
            print(f"User found: {user}")
            session['logged_in'] = True
            session['username'] = username
            # 获取当前时间
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 更新用户的登录时间，不包括微秒
            db.user.update_one(
                {"id": str(username)},
                {"$set": {"login_time": login_time}}
            )

            return redirect(url_for('upload_file'))
        else:
            print("Invalid credentials")
            error = "Invalid credentials. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/user_management')
def user_management():
    # 从 MongoDB 中检索用户数据，同时获取登录时间
    users = list(db.user.find())

    # 渲染模板并传递变量，包括登录时间
    return render_template('user_management.html', users=users)


def upload_to_obs(file_path, file_name):
    try:
        logging.debug(f"Uploading {file_path} to OBS bucket {OBS_BUCKET_NAME} as {file_name}")
        obs_client.putFile(OBS_BUCKET_NAME, file_name, file_path)
        obs_url = f"https://{OBS_BUCKET_NAME}.{OBS_ENDPOINT}/{file_name}"
        logging.debug(f"File uploaded successfully: {obs_url}")
        return obs_url
    except Exception as e:
        logging.error(f"Failed to upload file {file_name} to OBS: {str(e)}")
        flash(f"Failed to upload file {file_name} to OBS: {str(e)}")
        return None

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash('没有文件部分')
            return redirect(request.url)

        file = request.files['image_file']
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)

            obs_url = upload_to_obs(file_path, filename)
            if obs_url:
                try:
                    data = {'file_name': filename}
                    response = requests.post(base_url + "/predict", json=data)
                    logging.info(response)

                    if response.status_code == 200:
                        predictions = response.json().get('predictions', [])
                        # Pass the image URL to the template
                        return render_template('upload.html', predictions=predictions, image_url=obs_url)
                    else:
                        flash('预测失败，服务器返回状态码: {}'.format(response.status_code))
                        return redirect(request.url)
                except Exception as e:
                    flash('请求预测过程中出现错误: {}'.format(str(e)))
                    return redirect(request.url)
            else:
                flash('上传文件到OBS失败')
                return redirect(request.url)
    return render_template('upload.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5001, debug=True)
