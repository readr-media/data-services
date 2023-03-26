import os
import re
import json
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from rss_general import gen_general_rss
from rss_line import gen_line_rss
from configs import field_check_list


PROJECT_NAME = os.environ['PROJECT_NAME']
FIELD_NAME = json.loads(os.environ['FIELD_NAME_MAPPING'])
escapse_char = u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+'


def field_mapping_check():
    for field in field_check_list:
        if field not in FIELD_NAME:
            print("key missing in field mapping ")
            return
    return True


def gql2rss(gql_endpoint: str, gql_string: str, schema_type: str, relatedPost_prefix: str = '', rm_ytbiframe: bool = False, relatedPost_number: int = 3):
    if field_mapping_check() is None:
        return
    
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport,
                        fetch_schema_from_transport=False)
    query = gql(gql_string)
    gql_result = gql_client.execute(query)

    if 'videos' in gql_result and gql_result['videos']:
        gql_data = gql_result['videos']
        is_video = True
    elif 'posts' in gql_result and gql_result['posts']:
        gql_data = gql_result['posts']
        is_video = False
    else:
        print('gql query failed')
        return

    if schema_type == 'line':
        return gen_line_rss(gql_data, relatedPost_prefix, is_video, rm_ytbiframe, relatedPost_number)
    return gen_general_rss(gql_data, relatedPost_prefix, is_video, rm_ytbiframe, relatedPost_number)


if __name__ == '__main__':
    relatedPost = '<br/><p class="read-more-vendor"><span>相關文章</span>'
    rm_ytbiframe = True
    gql_string = '''# Write your query or mutation here
        query {
  posts(
    where: { state: { equals: "published" } }
    orderBy: { publishedDate: desc }
    take: 100
  ) {
    id
    slug
    title
    publishedDate
    categories {
      name
    }
    heroCaption
    heroImage {
      urlOriginal
      resized {
        original
      }
    }
    brief
    content
    updatedAt
    relateds {
      id
      slug
      title
      heroImage {
        urlOriginal
        resized {
          original
        }
      }
    }
    tags {
        name
      }
    writers{
        name
    }
  }
}'''
    gql_string = '''query {
  videos(
    where: { isFeed: { equals: true } }
    orderBy: { publishedDate: desc }
    take: 20
  ) {
    id
    name
    file {
      url
    }
    urlOriginal
    content
    publishedDate
    createdAt
    updatedAt
  }
}'''
    relatedPost_number = None
    dest_file = 'rss/mm_standard_rss_video.xml'
    # dest_file = 'rss/mm_standard_rss.xml'
    # dest_file = 'rss/mm_line.xml'
    # dest_file = 'rss/mm_line_video.xml'
    relatedPost='相關文章'
    gql_endpoint = os.environ['GQL_ENDPOINT']
    rss_data = gql2rss(gql_endpoint, gql_string, 'general', relatedPost, relatedPost_number)
    with open(dest_file, 'w') as f:
        f.write(rss_data)
        # upload_data(bucket, rss_data, 'application/xml', dest_file)
