import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone, timedelta

def status_update():
    db = os.environ['DBNAME']
    db_user = os.environ['DATABASE_USER']
    db_pw = os.environ['DATABASE_PASSWORD']
    db_host = os.environ['DATABASE_HOST']
    db_port = os.environ['DATABASE_PORT']
    connection = psycopg2.connect(database=db, user=db_user,password=db_pw, host=db_host, port=db_port)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    current_time = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")

    update_post = """UPDATE "Post" SET "status" = 'published', "updatedAt" = '%s' WHERE "status" = 'scheduled' AND "publishDate" < '%s'""" % (current_time, current_time)
    print(update_post)
    cursor.execute(update_post)
    connection.commit()
    return "ok"

if __name__=="__main__":
    status_update()
