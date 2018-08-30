import os
from flask import Flask, request, redirect, url_for, send_from_directory,render_template,flash,session
from werkzeug.utils import secure_filename
from time import time
from dapp_token import *
import pymysql



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['mp3'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'seongeun_secret'

# token name = eun
eun = mytoken('MyBasicToken.sol','MyBasicToken')

## file upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


## main page
@app.route('/', methods=['GET','POST'])
def index():
    conn = pymysql.connect(host='localhost', user='root',passwd='qwer1234',db='mydapp',charset='utf8')
    cursor = conn.cursor()
    query = 'SELECT name,title,path,lyrics,created,loveit,id FROM data_table order by id desc'
    cursor.execute(query)
    content_data = cursor.fetchall()
    num_content=len(content_data)

    # login o
    if session:
        user_name = session['user']
        query = 'SELECT wallet FROM user_table WHERE name = %s'
        value = (user_name)
        cursor.execute(query,value)
        user_wallet = (cursor.fetchall())
        user_wallet = user_wallet[0][0]
        show_token = eun.show_token(user_wallet)
        reward_list =[]
        if request.method == 'POST' and 'favorNum' in request.form:
            query = "update data_table set loveit = loveit + 1 where id = '" + request.form['favorNum'] + "'"
            cursor.execute(query)
            conn.commit()
        # admin login
        if user_name == 'admin':
            user_list = w3.eth.accounts
            now_block_number = w3.eth.blockNumber
            if request.method == 'POST' and 'user_name_balance' in request.form:
                addr_balance =  request.form['user_name_balance']
                show_token = eun.show_token(addr_balance)
            if request.method == 'POST' and 'user_name_transfer' in request.form and 'amount' in request.form:
                addr_transfer = request.form['user_name_transfer']
                amount_transfer = int(request.form['amount'])
                eun.send_token(w3.eth.accounts[0],addr_transfer,amount_transfer)
            if request.method == 'POST' and 'reward' in request.form:
                query = 'SELECT name FROM user_table'
                cursor.execute(query)
                data = cursor.fetchall()
                num_data = len(data)

                user_list =[]
                for num in range(num_data):
                    user_name = data[num][0]

                    query = "SELECT loveit From data_table WHERE name=%s"
                    value = (user_name)
                    cursor.execute('set names utf8')
                    cursor.execute(query,value)
                    score = sum(int(x[0]) for x in cursor.fetchall())

                    query = "SELECT wallet From user_table WHERE name=%s"
                    value = (user_name)
                    cursor.execute(query,value)
                    user_wallet = cursor.fetchall()[0][0]
                
                    amount = score * 1000
                    eun.send_token(w3.eth.accounts[0],user_wallet,amount)
                    if user_name == 'admin':
                        continue
                    else:
                        reward_list.append(user_name+'-'+str(amount))
                query = 'update data_table set loveit = 0'
                cursor.execute(query)
                conn.commit()



            totalSupply = eun.show_total_token()
            show_token = eun.show_token(w3.eth.accounts[0])
            return render_template('admin.html',totalSupply=totalSupply,user_list=user_list,show_token=show_token,now_block_number=now_block_number,user_wallet=user_wallet,reward_list=reward_list)
        return render_template('user.html',user_name = user_name,user_wallet=user_wallet,show_token=show_token,content_data=content_data,num_content=num_content)
    # login x
    else:
        return render_template('index.html',content_data=content_data,num_content=num_content)

    cursor.close()
    conn.close()


# logout page
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))


# login page
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pw = request.form['pw']
        conn = pymysql.connect(host='localhost', user='root',passwd='qwer1234',db='mydapp',charset='utf8')
        cursor = conn.cursor()
        query = 'SELECT name FROM user_table WHERE email = %s AND pw = %s'
        value = (email,pw)
        cursor.execute('set names utf8')
        cursor.execute(query,value)
        data = (cursor.fetchall())
        cursor.close()
        conn.close()
        for row in data:
            data = row[0]
            if data:
                session['user'] = data
                return redirect(url_for('index'))
        else:
            return 0
            #flash('Invalid input data detected!')
    return render_template('login.html')

# sign-up page
@app.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pw = request.form['pw']

        conn = pymysql.connect(host='localhost',user='root', passwd='qwer1234', db='mydapp',charset='utf8')
        cursor = conn.cursor()

        query = "SELECT 1 FROM user_table WHERE email='%s'"%(email)
        #value = (email)
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            #flash('user other email')
            error = 'The email is already userd. please use another one'
        else:
            # sign-up 시 지갑 주소 생성 제공!
            wallet_key = w3.personal.newAccount(pw)
            query = 'INSERT INTO user_table (name,email,pw,wallet) value(%s,%s,%s,%s)'
            value = (name,email,pw,wallet_key)
            cursor.execute(query,value)
            data = cursor.fetchall()

            if not data:
                conn.commit()
            else:
                conn.rollback()
                return print('Register Failed')
            return redirect(url_for('login'))


        cursor.close()
        conn.close()
    return render_template('signup.html')




# upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('no filename')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            name = session['user']
            filename = name+'_'+str(round(time.time()))+'_'+secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = os.path.abspath(filename)
            title = request.form['title']
            lyrics = request.form['lyrics']
            conn = pymysql.connect(host='localhost',user='root', passwd='qwer1234', db='mydapp',charset='utf8')
            cursor = conn.cursor()
            query = 'INSERT INTO data_table (name,title,lyrics,path,created) values(%s,%s,%s,%s,NOW())'
            value = (name,title,lyrics,path)
            cursor.execute(query,value)
            data = cursor.fetchall()
            if not data:
                conn.commit()
            else:
                conn.rollback()
            return redirect(url_for('index'))

    return render_template('upload.html')


'''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
'''


if __name__ == '__main__':
    app.run('localhost',5000, debug = True)
