from flask import Flask, request, session, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('/main.html')

@app.route('/main')
def main():
    
    
    return render_template('main.html')

@app.route('/register_page')
def register_page():
    return render_template('register/register_page.html')

@app.route('/register_proc', methods=['POST', 'GET'])
def register_proc():
    if request.method == 'GET':
        return render_template('register.html')
    
    else:
        username = request.form['userName']
        id = request.form['userId']
        pwd = request.form['userPwd']
        passwordcheck = request.form['passwordcheck']
        email = request.form['userEmail']

        if len(username) <= 8 or len(pwd) <= 8 or len(passwordcheck) <= 8:
            return 'username and password should be greater then 8 chars!'
        elif pwd != passwordcheck:
            return "Please Enter your password correctly"
        else:
            
            try:
                conn = sqlite3.connect('membership_db.db')
                c = conn.cursor()
                c.execute("""CREATE TABLE IF NOT EXISTS member(
                userName VARCHAR,
                userId VARCHAR,
                userPwd VARCHAR,
                userEmail VARCHAR
                )""")
                c.execute("INSERT INTO member(userName, userId, userPwd, userEmail) VALUES(?,?,?,?)", (str(username), str(id), str(pwd), str(email), ))
                c1 = conn.cursor()
                c1.execute("""CREATE TABLE IF NOT EXISTS content(
                userId VARCHAR,
                userTitle VARCHAR,
                userData VARCHAR,
                userImg VARCHAR
            )""")
                conn.commit()
            except Exception as e:
                print('c error:', e)
            finally:
                return redirect(url_for('login_page'))
           

@app.route('/login_page')
def login_page():
    return render_template('login/login_page.html')

@app.route('/login_proc', methods=['POST', 'GET'])
def login_proc():
    if request.method == 'POST':
        userId = request.form['id']
        userPwd = request.form['pwd']
        if len(userId) == 0 or len(userPwd) ==0:
            return 'This ID is not subscribed, or it is an invalid password!'
        else:
            conn = sqlite3.connect('membership_db.db')
            cursor = conn.cursor()
            sql = 'select rowid, userName, userId, userPwd, userEmail from member where userId = ?'
            cursor.execute(sql, (userId, ))
            rows = cursor.fetchall()
            for rs in rows:
                if userId == rs[2] and userPwd == rs[3]:
                    session['logFlag'] = True
                    session['rowid'] = rs[0]
                    session['userId'] = userId
                    return redirect(url_for('main'))
                else:
                    return redirect(url_for('login_page'))
    else:
        return 'Wrong access'

@app.route('/user_info_edit/<int:edit_rowid>', methods=['GET'])
def getUser(edit_rowid):
    if session.get('logFlag') != True:
        return redirect('login_page')
    conn = sqlite3.connect('membership_db.db')
    cursor = conn.cursor()
    sql = 'select userEmail from member where rowid = ?'
    cursor.execute(sql, (edit_rowid, ))
    row = cursor.fetchone()
    edit_email = row[0]
    cursor.close()
    conn.close()
    return render_template('user/user_info.html', edit_rowid=edit_rowid, edit_email=edit_email)

@app.route('/user_info_edit_proc', methods=['POST'])
def user_info_edit_proc():
    rowid = request.form['rowid']
    userPwd = request.form['userPwd']
    userEmail = request.form['userEmail']
    if len('rowid') == 0:
        return 'Edit Data Not Found'
    else:
        conn = sqlite3.connect('membership_db.db')
        cursor = conn.cursor()
        sql = 'update member set userPwd = ?, userEmail = ? where rowid = ?'
        cursor.execute(sql, (userPwd, userEmail, rowid))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route('/post_page')
def post_page():
    return render_template('post/post_page.html')


@app.route('/post_proc', methods = ['POST', 'GET'])
def post_proc():
    if request.method == 'GET':
        return render_template('post/post_page.html')
    else:
        id = session['userId']
        title = request.form['title']
        content = request.form['content']
        f = request.files['file']
        if len(f.filename)<=4:
            imgname = "./image/blank.png"
        else:
            f.save("./static/image/" + secure_filename(f.filename))
            imgname = "./image/" + f.filename
            
        try:
            conn = sqlite3.connect('membership_db.db')
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS content(
                userId VARCHAR,
                userTitle VARCHAR,
                userData VARCHAR,
                userImg VARCHAR
            )""")
            c.execute("INSERT INTO content(userId, userTitle, userData, userImg) VALUES (?,?,?,?)", (str(id), str(title), str(content), str(imgname)))
            conn.commit()

        except Exception as e:
            print('c error:', e)
        finally:
            return redirect('post_list')

@app.route('/post_list')
def post_list():
        id = session['userId']
        conn = sqlite3.connect('membership_db.db')
        cursor = conn.cursor()
        sql = 'select userTitle, userData, rowid, userImg from content where userId = ? order by rowid asc'
        cursor.execute(sql, (id, ))
        row = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()  
        return render_template('post/post_list.html', row=row)

@app.route('/post_read/<int:read_rowid>', methods=['GET'])
def readPost(read_rowid):
    conn = sqlite3.connect('membership_db.db')
    cursor = conn.cursor()
    sql = 'select userTitle, userData, rowid, userImg from content where rowid = ?'
    cursor.execute(sql, (read_rowid, ))
    row = cursor.fetchone()
    read_data = row[1]
    read_title = row[0]
    read_img = row[3]
    cursor.close()
    conn.close()
    return render_template('post/post_read.html', read_rowid=read_rowid, read_data=read_data, read_title=read_title, read_img=read_img)

@app.route('/post_edit/<int:edit_rowid>', methods=['GET'])
def getPost(edit_rowid):
    conn = sqlite3.connect('membership_db.db')
    cursor = conn.cursor()
    sql = 'select userTitle, userData, rowid, userImg from content where rowid = ?'
    cursor.execute(sql, (edit_rowid, ))
    row = cursor.fetchone()
    edit_data = row[1]
    edit_title = row[0]
    cursor.close()
    conn.close()
    return render_template('post/post_edit.html', edit_rowid=edit_rowid, edit_data=edit_data, edit_title=edit_title)

@app.route('/post_edit_proc', methods=['POST'])
def post_edit_proc():
    rowid = request.form['rowid']
    title = request.form['title']
    content = request.form['content']
    f = request.files['file']
    
    if len('rowid')==0:
        return 'Edit Data Not Found'
    else:
        if len(f.filename)<=4:
            imgname = "./image/blank.png"
        else:
            f.save("./static/image/" + secure_filename(f.filename))
            imgname = "./image/" + f.filename
        try:    
            conn = sqlite3.connect('membership_db.db')
            cursor = conn.cursor()
            sql = 'update content set userTitle = ?, userData = ?, userImg = ? where rowid = ?'
            cursor.execute(sql, (str(title), str(content), str(imgname), rowid, ))
            conn.commit()
            cursor.close()
        except Exception as e:
            print('c error:', e)
        finally:
            return redirect(url_for('post_list'))

@app.route('/post_delete_proc/<int:delete_rowid>', methods=['GET'])
def post_delete_proc(delete_rowid):
    if len('rowid')==0:
        return 'Edit Data Not Found'
    else:
        conn = sqlite3.connect('membership_db.db')
        cursor = conn.cursor()
        sql = 'delete from content where rowid = ?'
        cursor.execute(sql, (delete_rowid, ))
        conn.commit()
        cursor.close()
        return redirect(url_for('post_list'))

@app.route('/post_upload')
def post_upload():
    return render_template('post/post_upload.html')

@app.route('/post_upload_proc', methods = ['POST', 'GET'])
def post_upload_proc():
    if request.method == 'POST':
        id = session['userId']
        conn = sqlite3.connect('membership_db.db')
        cursor = conn.cursor()
        sql = 'select userTitle, userData, rowid from content where userId = ? order by rowid asc'
        cursor.execute(sql, (id, ))
        row = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()   
        f = request.files['file']
        f.save('./static/image/' + secure_filename(f.filename))
        imgname=f.filename
        print(f.filename)
        return render_template('post/post_list.html', imgname=imgname, row=row)

if __name__ == '__main__':
    app.secret_key = "2015112230"
    app.debug = True
    app.run()
