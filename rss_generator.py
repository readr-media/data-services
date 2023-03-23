from dateutil import parser, tz
import time
import uuid
import lxml.etree as ET
from lxml.etree import Element
from feedgen import util
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import timedelta
import hashlib
import re
import os
import json
from utils.draft_converter import convert_draft_to_html
from configs import feed_config_mapping, field_check_list
from utils.rss_fmt_parser import recparse, sub, tsConverter, stringWrapper


PROJECT_NAME = os.environ['PROJECT_NAME']
FIELD_NAME = json.loads(os.environ['FIELD_NAME_MAPPING'])
escapse_char = u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+'


def gen_general_rss(posts, feed_config, __timezone__, relatedPost_prefix):
    base_url = feed_config['baseURL']
    nsmap_media = feed_config['media']
    nsmap_dcterms = feed_config['dcterms']
    nsmap_content = feed_config['content']
    mainXML = {
        "title": feed_config['title'],
        "link": feed_config['link'],
        "description": feed_config['description'],
        "language": "zh-TW",
        "copyright": feed_config['copyright'],
        "image": {
            "title": feed_config['title'],
            "link": feed_config['link'],
            "url": feed_config['image']
        },
        "ttl": 300,
        "item": []
    }
    root = Element('rss', nsmap={'content': nsmap_content,
                   'media': nsmap_media, 'dcterms': nsmap_dcterms}, version='2.0')
    channel = sub(root, 'channel')

    for post in posts:
        slug = post[FIELD_NAME['slug']]
        guid = hashlib.sha224((base_url+slug).encode()).hexdigest()
        name = post[FIELD_NAME['name']]
        name = re.sub(escapse_char, '', name)
        publishedDate = post[FIELD_NAME['publishedDate']] if FIELD_NAME['publishedDate'] else post['createdAt']
        updated = post['updatedAt'] if post['updatedAt'] else publishedDate
        categories = post[FIELD_NAME['categories']]
        item = {
            "id": guid,
            "title": name,
            "link": base_url+slug,
            "pubDate": util.formatRFC2822(parser.isoparse(publishedDate).astimezone(__timezone__)),
            "updated": util.formatRFC2822(parser.isoparse(updated).astimezone(__timezone__)),
            "category": list(c[FIELD_NAME['categories_name']]for c in categories)
        }
        content = ''
        if post['heroImage']:
            img = post['heroImage']['resized']['original']
            item["media:content"] = Element(_tag='{%s}content' % nsmap_media, nsmap={
                                            'media': nsmap_media}, url=img, medium='image')
            if post['heroCaption']:
                content += '<img src="%s" alt="%s" />' % (
                    img, post['heroCaption'])
            else:
                content += '<img src="%s" />' % (img)
        brief = post[FIELD_NAME['brief']]
        if brief:
            brief = re.sub(escapse_char, '', convert_draft_to_html(brief))
            item["brief"] = brief
            content += brief
        if post['content']:
            contentHtml = convert_draft_to_html(post['content'])
            if rm_ytbiframe:
                contentHtml = re.sub(
                    '<iframe.*?src="https://www.youtube.com/embed.*?</iframe>', '', contentHtml)
            content += contentHtml
        relateds = post[FIELD_NAME['relatedPosts']]
        if isinstance(relateds, list) and len(relateds) > 0 and relatedPost_prefix:
            content += relatedPost_prefix
            for related_post in relateds[:3]:
                related_slug = related_post[FIELD_NAME['slug']]
                related_name = post[FIELD_NAME['name']]
                content += '<br/><a href="%s">%s</a>' % (
                    base_url + related_slug, related_name)
        content = re.sub(escapse_char, '', content)
        item["media:content"] = Element(_tag='{%s}content' % nsmap_media, nsmap={
            'media': nsmap_media}, url=img, medium='image')
        item["content:encoded"] = Element(_tag='{%s}encoded' % nsmap_content, nsmap={
                                          'content': nsmap_content})
        item["content:encoded"].text = stringWrapper('content', content)
        if 'writers' in post and post['writers']:
            item["dc:creator"] = []
            for w in post['writers']:
                creator = Element(_tag='{%s}creator' % nsmap_dcterms, nsmap={
                                  'creator': nsmap_dcterms})
                creator.text = stringWrapper('author', w['name'])
                item["dc:creator"].append(creator)
        mainXML['item'].append(item)
    recparse(channel, mainXML)
    return f'<?xml version="1.0" encoding="UTF-8" ?>{ET.tostring(root, encoding="unicode")}'


def gen_line_rss(posts, feed_config, __timezone__, relatedPost_prefix):
    base_url = feed_config['baseURL']
    news_available_days = 365
    mainXML = {
        'UUID': str(uuid.uuid4()),
        'time': int(round(time.time() * 1000)),
        'article': []
    }
    root = Element('articles')

    for post in posts:
        slug = post[FIELD_NAME['slug']]
        name = post[FIELD_NAME['name']]
        name = re.sub(escapse_char, '', name)
        publishedDate = post[FIELD_NAME['publishedDate']
                             ] if FIELD_NAME['publishedDate'] else post['createdAt']
        updated = post['updatedAt'] if post['updatedAt'] else publishedDate
        availableDate = max(tsConverter(publishedDate), tsConverter(updated))
        categories = post[FIELD_NAME['categories']]

        item = {
            'ID': post['id'],
            'nativeCountry': 'TW',
            'language': 'zh',
            'startYmdtUnix': availableDate,
            'endYmdtUnix': tsConverter(publishedDate) + (round(timedelta(news_available_days, 0).total_seconds()) * 1000),
            'title': name,
            'category': categories[0][FIELD_NAME['categories_name']] if len(categories) > 0 else [],
            'publishTimeUnix': tsConverter(publishedDate),
            'updateTimeUnix': tsConverter(updated),
            'contentType': 0,
        }
        if post['heroImage']:
            img = post['heroImage']['resized']['original']
            item['thumbnail'] = img
            if post['heroCaption']:
                heroCaption = post['heroCaption']
                content = f"<figure class=\"image\"><img alt=\"{heroCaption}\" src=\"{img}\"><figcaption>{heroCaption}</figcaption></figure>"
            else:
                content = f"<img src=\"{img}\">"
        else:  # logo image as heroimage
            content = f"<figure class=\"image\"><img alt=\"logo\" src=\"{feed_config['image']}\"><figcaption>logo</figcaption></figure>"
        brief = post[FIELD_NAME['brief']]
        if brief:
            brief = re.sub(escapse_char, '', convert_draft_to_html(brief))
            content += brief
        if post['content']:
            contentHtml = convert_draft_to_html(post['content'])
            if rm_ytbiframe:
                contentHtml = re.sub(
                    '<iframe.*?src="https://www.youtube.com/embed.*?</iframe>', '', contentHtml)
            content += contentHtml
            content += contentHtml + feed_config['officialLine']
        relateds = post[FIELD_NAME['relatedPosts']]
        if isinstance(relateds, list) and len(relateds) > 0 and relatedPost_prefix:
            content += relatedPost_prefix
            recommendArticles = []
            for related_post in relateds[:3]:
                related_slug = related_post[FIELD_NAME['slug']]
                related_name = related_post[FIELD_NAME['name']]
                relatedPostUrl = base_url + related_slug + \
                    feed_config['utmSource('] % ('line', slug)
                content += '<li><a href="%s">%s</li>' % (
                    relatedPostUrl, related_name)
                recommendArticle = {
                    'title': related_name, 'url': relatedPostUrl}
                if related_post['heroImage']:
                    recommendArticle['thumbnail'] = related_post['heroImage']['resized']['original']
                recommendArticles.append(recommendArticle)
            content += "</ul>"
            item['recommendArticles'] = {'article': recommendArticles}
        content = re.sub(escapse_char, '', content)
        item['contents'] = {'text': {'content': content}}

        item['author'] = feed_config['title']
        item['sourceUrl'] = base_url + slug + feed_config['utmSource'] % 'line'
        if post['tags']:
            tags = [tag['name'] for tag in post['tags']]
            item['tags'] = {'tag': tags}
        mainXML['article'].append(item)
    recparse(root, mainXML)
    return f'<?xml version="1.0" encoding="UTF-8" ?>{ET.tostring(root, encoding="unicode")}'


def field_mapping_check():
    for field in field_check_list:
        if field not in FIELD_NAME:
            print("key missing in field mapping ")
            return
    return True


def gql2rss(gql_endpoint: str, gql_string: str, schema_type: str, is_video: bool, relatedPost_prefix: str, rm_ytbiframe=False):
    feed_config = feed_config_mapping[PROJECT_NAME]
    if field_mapping_check() is None:
        return
    __timezone__ = tz.gettz("Asia/Taipei")
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport,
                        fetch_schema_from_transport=False)
    query = gql(gql_string)
    gql_result = gql_client.execute(query)
    if is_video:
        if 'videos' in gql_result and gql_result['videos']:
            gql_data = gql_result['videos']

        else:
            print('gql query failed')
            return
    else:
        if 'posts' in gql_result and gql_result['posts']:
            gql_data = gql_result['posts']
        else:
            print('gql query failed')
            return
    if schema_type == 'line':
        return gen_line_rss(gql_data, feed_config, __timezone__, relatedPost_prefix)

    else:
        return gen_general_rss(gql_data, feed_config, __timezone__, relatedPost_prefix)


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
    dest_file = 'rss/mm_standard_rss.xml'
    # dest_file = 'rss/mm_line.xml'
    # dest_file = 'rss/sein_line.xml'

    gql_endpoint = os.environ['GQL_ENDPOINT']
    rss_data = gql2rss(gql_endpoint, gql_string, 'general', False, relatedPost)
    with open(dest_file, 'w') as f:
        f.write(rss_data)
        # upload_data(bucket, rss_data, 'application/xml', dest_file)
