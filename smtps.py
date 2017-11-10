# -*- coding: UTF-8 -*-
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from urllib import request as req
import urllib
from flask_cors import *
import time

#from email import MIMEMultipart

import smtplib
import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt'])


ALLCACHE={}
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))
#msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')




# 输入Email地址和口令:
from_addr = '410232436@qq.com'#input('From: ')
password = 'qadaiwzcxeifcaia'#input('Password: ')
# 输入收件人地址:
to_addr = 'codkui@kindle.cn'#input('To: ')
# 输入SMTP服务器地址:
smtp_server = 'smtp.qq.com'#input('SMTP server: ')

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            sendToKindle( file.filename)
            return file.filename#redirect(url_for('uploaded_file',
                                   # filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
@app.route('/search', methods=['GET'])
def search():
    
    agu=request.args
    keyword=req.quote(agu["key"]) 
    res=gets("http://api05iye5.zhuishushenqi.com/book/fuzzy-search?query="+keyword)
    return res

@app.route('/info', methods=['GET'])
def info():
    
    agu=request.args
    keyword=agu["id"]
    res=gets("http://api073nwc.zhuishushenqi.com/book/"+keyword)
    return res

#http://api073nwc.zhuishushenqi.com/book/508de73e55e53b9a1a000031

@app.route('/resource', methods=['GET'])
def resource():
    
    agu=request.args
    keyword=agu["id"]
    res=gets("http://api08mgip.zhuishushenqi.com/atoc?view=summary&book="+keyword)
    return res

#http://api08mgip.zhuishushenqi.com/atoc?view=summary&book=508de73e55e53b9a1a000031

@app.route('/index', methods=['GET'])
def index():
    
    agu=request.args
    keyword=agu["id"]
    #res=gets("http://api073nwc.zhuishushenqi.com/atoc/"+keyword+"?view=chapters")
    res=gets("http://api.zhuishushenqi.com/atoc/"+keyword+"?view=chapters")
    if res=="":
        res=gets("http://api08mgip.zhuishushenqi.com/atoc/"+keyword+"?view=chapters")
    return res
#http://api08mgip.zhuishushenqi.com/atoc/57076a29326011945ee86161?view=chapters
    
@app.route('/url', methods=['GET'])
def urls1():
    
    agu=request.args
    keyword=req.unquote(agu["url"]) 
    res=gets("http://chapterup.zhuishushenqi.com/chapter/"+keyword)
    print("http://chapterup.zhuishushenqi.com/chapter/"+keyword)
    return res
#http://chapterup.zhuishushenqi.com/chapter/
@app.route('/image', methods=['GET'])
def image():
    
    agu=request.args
    keyword=agu["url"]
    if keyword=="undefined":
        return ""
    #print("http://statics.zhuishushenqi.com"+keyword)
    res=gets("http://statics.zhuishushenqi.com"+keyword)
    
    return res
#http://statics.zhuishushenqi.com
def gets(url):
    res=ALLCACHE.get(url,None)
    if res!=None and res["time"]+600>int(time.time()):
    #    print("缓存")
        return ALLCACHE[url]["data"]
    #print("非缓存")
    try:
        data=req.urlopen(url)
        text=data.read()
        data.close()
    except:
        text=""
    ALLCACHE[url]={"time":int(time.time()),"data":text}
    return text

def sendToKindle(filename):
    msg = MIMEMultipart()
    msg['From'] = _format_addr('服务器 <%s>' % from_addr)
    msg['To'] = _format_addr('kindle <%s>' % to_addr)
    msg['Subject'] = Header('新书推送', 'utf-8').encode()
    # 邮件正文是MIMEText:
    msg.attach(MIMEText('发送文件...', 'plain', 'utf-8'))

    # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
    with open(os.path.join(app.config['UPLOAD_FOLDER'],filename), 'rb') as f:
        # 设置附件的MIME和文件名，这里是png类型:
        mime = MIMEBase('file', 'txt', filename=filename)
        # 加上必要的头信息:
        mime.add_header('Content-Disposition', 'attachment', filename=filename)
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        # 把附件的内容读进来:
        mime.set_payload(f.read())
        # 用Base64编码:
        encoders.encode_base64(mime)
        # 添加到MIMEMultipart:
        msg.attach(mime)

    #server = smtplib.SMTP(smtp_server, 25) # SMTP协议默认端口是25
    #smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    # 剩下的代码和前面的一模一样:
    server.set_debuglevel(0)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

if __name__=="__main__":
    app.run(host='0.0.0.0',port=8007,threaded=True)