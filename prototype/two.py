import ast
import datetime
import os.path
import sqlite3 as sqlite
import subprocess
import time
from bottle import route, run, template, request, static_file, redirect
from os import listdir, getcwd


#CONSTANTS
DATABASE = 'test.db'

#PAGE ROUTES
@route('/')
def index():
    index_page_content = """
        <form action="/upload_file" method="post" enctype="multipart/form-data">
            category: <input name="category" type="text" />
            upload: <input name="upload" type="file" />
            <input type="submit" value="Start upload" />
        </form>
    """
    return index_page_content

@route('/content/<contentId:int>')
def view_content(contentId):
    try:
        conn = create_or_open_db(DATABASE)
        #sql = 'select * from content;'
        sql = '''select * from content where TOKENID like ?;'''
        result = conn.execute(sql, [contentId])
        #result = conn.execute(sql)
        content_id = result.fetchone()[3]
        
        #conn.commit()
        return 'The tokenId will be: {}'.format(content_id)
    except Exception as e:
        print(e)
    finally:
        conn.close()

@route('/upload_file', method="POST")
def upload_file():
    try:
        #get references to the file, file name
        upload = request.files.get('upload')
        save_file(upload)
        #create a database connection, and save the content to the database
        conn = create_or_open_db(DATABASE)
        cursor = conn.cursor()
        name = upload.filename
        author = 'Standin Author'
        timestamp = str(datetime.datetime.now())
        SQL = 'INSERT INTO content(FILENAME, AUTHOR, DATESTAMP) VALUES(?, ?, ?);'
        cursor.execute(SQL, [name, author, timestamp])
        #keep a reference to that item's SQL primary index in memory for future step
        #also keep a reference to the filename in memory; in future the content's hash as well
        row_id = cursor.lastrowid
        #server then uses that in-mem filename to create a new token on the blockchain
        create_token = subprocess.run(['node', './test/proto.js', name], stdout=subprocess.PIPE)
        time.sleep(15)
        #keep the transactionHash in memory for a future step
        txHash = create_token.stdout.decode('utf-8')

        #server then queries Blockchain event log
        get_logs = subprocess.run(['node', './test/logs.js'], stdout=subprocess.PIPE)
        get_logs = get_logs.stdout
        if type(get_logs) == bytes:
            get_logs = get_logs.decode('utf-8')
            if type(get_logs) == str:
                get_logs = ast.literal_eval(get_logs)
        #iterative logs & match the event log to the transaction hash saved from above
        """
        eventLog = None
        print('point e')
        for log in get_logs:
            if log['transactionHash'] == txHash:
                eventLog = log
        """
        #get the tokenId from that transaction log
        contentId = get_logs[1]

        #with the DB connection still open, get the row by the primary index still in memory
        #update that record with the tokenId, save it again
        SQL = 'update content set TOKENID = ? where id = ?;'
        cursor.execute(SQL, [contentId, row_id])
    except Exception as e:
        print(e)
    finally:
        #close connection, redirect user to page for that piece of content
        conn.commit()
        conn.close()
        new_route = '/content/{}'.format(contentId)
        return redirect(new_route)

#SUPPORTING METHODS
def create_or_open_db(db_file):
    try:
        db_is_new = not os.path.exists(db_file)
        conn = sqlite.connect(db_file)
        if db_is_new:
            SQL = 'create table if not exists content(ID INTEGER PRIMARY KEY AUTOINCREMENT, FILENAME TEXT, AUTHOR TEXT, TOKENID TEXT, DATESTAMP TEXT);'
            conn.execute(SQL)
            conn.commit()
        return conn
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


if __name__ == '__main__':
    run(host='0.0.0.0', port=8880, debug=True)
