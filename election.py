import os
import psycopg2
import psycopg2.extras
import requests
import json
from data_export import sheet2json, gql2json, upload_data
from datetime import datetime, timezone, timedelta
from configs import homepage_data

def election2024():
    # just for 2024 election homepage json
    #db = os.environ['DBNAME']
    #db_user = os.environ['DATABASE_USER']
    #db_pw = os.environ['DATABASE_PASSWORD']
    #db_host = os.environ['DATABASE_HOST']
    #db_port = os.environ['DATABASE_PORT']
    db = 'openrelationship'
    db_user = 'openrelation'
    db_pw = ''
    db_host = '35.234.56.9'
    db_port = 5432
    election_id = 85
    connection = psycopg2.connect(database=db, user=db_user,password=db_pw, host=db_host, port=db_port)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    politics_count = """
SELECT "Politic"."person", "Politic"."politicCategory", count(*) FROM "Politic", "PersonElection" WHERE "Politic"."thread_parent" IS NULL AND "Politic"."reviewed" = TRUE AND "Politic"."person" = "PersonElection"."id" AND "PersonElection"."election" = %s GROUP BY "Politic"."person", "Politic"."politicCategory";
    """ % (election_id)
    # how to get the relationship count
    # SELECT count("_Politic_factCheck"."B") FROM "_Politic_factCheck", "Politic" WHERE "_Politic_factCheck"."A" = "Politic"."id" AND "Politic"."id" = ANY(ARRAY[8031, 8032, 8033, 8034]);
    print(politics_count)
    cursor.execute(politics_count)
    all_politics = cursor.fetchall()
    for politic in all_politics:
        print(politic[0], politic[1], politic[2])
    return "ok"

def factcheck_data():
    #DATA_SERVICE = os.environ['DATA_SERVICE']
    WHORU_BUCKET = os.environ['WHORU_BUCKET']
    #WHORU_BUCKET = 'whoareyou-gcs-dev.readr.tw'
    gql_endpoint = os.environ['WHORU_GQL_ENDPOINT']
    #gql_endpoint = 'https://openrelationship-gql-dev-4g6paft7cq-de.a.run.app/api/graphql'
    get_categories = """
query { politicCategories {
  id
} }
    """
    categories = gql2json(gql_endpoint, get_categories)
    for category in categories["politicCategories"]:
        gql_string = """
query GetPresidents {
  personElections(
    orderBy:{ number: asc },
    where: {
      election: {id: { equals: 85 } },
      mainCandidate: null
    }) {
    id
    number
    person_id {
      id
      name
    }
    politicsCount(
      where: {
        status: { equals: "verified" },
        reviewed: { equals: true },
        politicCategory: { id: { equals: %s } }
      })
    politics(
      where: {
        status: { equals: "verified" },
        reviewed: { equals: true }
        politicCategory: { id: { equals: %s } }
      }) {
        id
        desc
        politicCategory {
          id
          name
        }
        positionChange {
          id
          isChanged
          factcheckPartner {
            id
            name
          }
        }
        positionChangeCount
        expertPoint {
          id
          expertPointSummary
          expert
        }
        expertPointCount
        factCheck {
          id
          factCheckSummary
          checkResultType
          factcheckPartner {
            id
            name
          }
        }
        factCheckCount
        repeat {
          id
          repeatSummary
          factcheckPartner {
            id
            name
          }
        }
        repeatCount
    }
  }
}
""" % (category['id'], category['id'])
    json_data = gql2json(gql_endpoint, gql_string)
    dest_file = """json/landing_factcheck_%s.json""" % (category["id"])
    upload_data(WHORU_BUCKET, json.dumps(json_data, ensure_ascii=False).encode('utf8'), 'application/json', dest_file)
    return "ok"

if __name__=="__main__":
    factcheck_data()
