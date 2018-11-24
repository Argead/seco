import sqlite3 as sqlite
import os.path
import datetime
import subprocess
import time
from bottle import route, run, template, request, static_file, redirect
from os import listdir, getcwd

DB_NAME = 'test.db'

@route('/')
def index():
    return """
        <form action="/upload_file" method="post" enctype="multipart/form-data">
            category: <input name="category" type="text" />
            upload: <input name="upload" type="file" />
            <input type="submit" value="Start upload" />
        </form>
    """

def create_or_open_db(db_file):
    try:
        db_is_new = not os.path.exists(db_file)
        conn = sqlite.connect(db_file)
        if db_is_new:
            sql = '''create table if not exists content (ID INTEGER PRIMARY KEY AUTOINCREMENT, FILENAME TEXT, AUTHOR TEXT, DATESTAMP TEXT);'''
            conn.execute(sql)
        return conn
    except Exception as e:
        raise e

def insert_content(conn, upload):
    try:
        _name = upload.filename
        _author = 'test'
        _time = str(datetime.datetime.now())
        sql = '''INSERT INTO content(FILENAME, AUTHOR, DATESTAMP) VALUES(?, ?, ?);'''
        conn.execute(sql, [_name, _author, _time])
        conn.commit()
        return
    except Exception as e:
        raise e

def save_file(upload):
    try:
        _file = upload.file.read()
        name, ext = os.path.splitext(upload.filename)
        if ext not in ('.txt', '.pdf'):
            return('File extension not allowed')
        save_path = '/tmp/tests/'
        upload.save(save_path)
    except Exception as e:
        print(e)

def test_node():
    create_token = subprocess.run(['node', './test/proto.js'])
    time.sleep(20)
    get_token = subprocess.run(['node', './test/logs.js'],stdout=subprocess.PIPE)
    cleaned_output = get_token.stdout.decode("utf-8").strip().split(" ")
    for item in cleaned_output:
        print(item)



@route('/upload_file', method='POST')
def upload_file():
    try:
        upload = request.files.get('upload')
        conn = create_or_open_db(DB_NAME)
        insert_content(conn, upload)
        save_file(upload)
        test_node()
        #sql = '''select * from content where ID = (SELECT MAX(ID) FROM content)'''
        #a = conn.execute(sql)
        #b = a.fetchone()[0]
        #new_route = '/content/{}'.format(b)
        #return redirect('/content/1')
    except Exception as e:
        print(e)
    finally:
        sql = 'select * from content where ID = (SELECT MAX(ID) FROM content)'
        a = conn.execute(sql)
        b = a.fetchone()[0]
        new_route = '/content/{}'.format(b)
        conn.close()
        return redirect(new_route)

@route('/download_file/<filename:path>')
def download_file(filename):
    try:
        return static_file(filename, root='/tmp/tests', download=filename)
    except Exception as e:
        print(e)

@route('/content/<fileindex:int>')
def view_content(fileindex):
    try:
        conn = create_or_open_db(DB_NAME)
        sql = '''select * from content where ID like ?;'''
        result = conn.execute(sql, [fileindex])
        conn.commit()
        return 'The tokenId will be: {}'.format(result.fetchone()[0])
    except Exception as e:
        print(e)
    finally:
        conn.close()

@route('/content')
def view_all_content():
    try:
        conn = create_or_open_db(DB_NAME)
        sql = 'select * from content;'
        results = conn.execute(sql).fetchall()
        conn.commit()
        items = ''
        for reult in results:
            items += '<td>' + reult[1] + '\n' + str(reult[0]) + '</td>'
        html = '<table><tr>{}</tr></table>'.format(items)
        return html
            

    except Exception as e:
        print(e)

    finally:
        conn.close()



if __name__ == '__main__':
    run(host='0.0.0.0', port=8880, debug=True)
