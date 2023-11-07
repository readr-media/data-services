import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone, timedelta
from configs import homepage_data

def status_update():
    db = os.environ['DBNAME']
    db_user = os.environ['DATABASE_USER']
    db_pw = os.environ['DATABASE_PASSWORD']
    db_host = os.environ['DATABASE_HOST']
    db_port = os.environ['DATABASE_PORT']
    connection = psycopg2.connect(database=db, user=db_user,password=db_pw, host=db_host, port=db_port)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    current_time = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")

    update_post = """UPDATE "Post" SET "state" = 'published', "updatedAt" = '%s' WHERE "state" = 'scheduled' AND "publishTime" < '%s'""" % (current_time, current_time)
    print(update_post)
    cursor.execute(update_post)
    connection.commit()
    return "ok"

def election_2024():
    # just for 2024 election homepage json
    #db = os.environ['DBNAME']
    #db_user = os.environ['DATABASE_USER']
    #db_pw = os.environ['DATABASE_PASSWORD']
    #db_host = os.environ['DATABASE_HOST']
    #db_port = os.environ['DATABASE_PORT']
    db = 'openrelationship'
    db_user = 'openrelationship'
    db_pw = 'k),F:>T1+oBVgl9'
    db_host = '35.234.56.9'
    db_port = 5432
    connection = psycopg2.connect(database=db, user=db_user,password=db_pw, host=db_host, port=db_port)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    update_post = """
SELECT "Politic"."person", "Politic"."politicCategory", count(*) FROM "Politic", "PersonElection" WHERE "Politic"."thread_parent" IS NULL AND "Politic"."reviewed" = TRUE AND "Politic"."person" = "PersonElection"."id" AND "PersonElection"."election" = 81 GROUP BY "Politic"."person", "Politic"."politicCategory";
    """
    print(update_post)
    cursor.execute(update_post)
    connection.commit()
    return "ok"
    

def homepage_data():
    category_latest_gql = '''
query Category {
  categories(
      take: %s
      where: { 
        state: { equals: "true" } 
        slug: { equals: "breakingnews" }
      }
      orderBy: { createdAt: asc }
    ) {
      id
      slug
      title
      post: relatedPost(
        take: %s
        skip: 0
        where: {
          state: { equals: "published" }
          style: { in: ["news", "report"] }
        }
        orderBy: { publishTime: desc }
      ) {
        id
      }
      reports: relatedPost(
        take: %s
        skip: 0
        where: {
          state: { equals: "published" }
          style: { in: ["project", "project3"] }
        }
        orderBy: { publishTime: desc }
      ) {
        id
      }
      ogDescription
      ogImage {
        resized {
          w1200
        }
      }
      
    }
}
    ''' % (homepage_data["homepage_categories"], homepage_data["homepage_category_posts"], homepage_data["homepage_category_reports"])
    return "ok"

if __name__=="__main__":
    status_update()
