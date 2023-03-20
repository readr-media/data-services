from datetime import datetime, timezone
from dateutil import parser, tz
# workaround as feegen raise error: AttributeError: module 'lxml' has no attribute 'etree'
from lxml import etree
from feedgen import util
from feedgen.feed import FeedGenerator
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import hashlib
import re
import os
from utils.draft_converter import convert_draft_to_html
from configs import field_name_mapping, feed_config_mapping
PROJECT_NAME = os.environ['PROJECT_NAME']


def gql2rss(gql_endpoint: str, gql_string: str, relatedPost_prefix: str, rm_ytbiframe=False):
    escapse_char = u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+'
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport,
                        fetch_schema_from_transport=False)
    query = gql(gql_string)
    gql_result = gql_client.execute(query)
    if 'posts' in gql_result and gql_result['posts']:
        posts = gql_result['posts']
    else:
        return None
    feed_config = feed_config_mapping[PROJECT_NAME]
    base_url = feed_config['baseURL']
    __timezone__ = tz.gettz("Asia/Taipei")
    field_name = field_name_mapping[PROJECT_NAME]
    fg = FeedGenerator()
    fg.load_extension('media', atom=False, rss=True)
    fg.load_extension('dc', atom=False, rss=True)
    fg.title(feed_config['title'])
    fg.description(feed_config['description'])
    fg.id(feed_config['link'])
    fg.pubDate(datetime.now(timezone.utc).astimezone(__timezone__))
    fg.updated(datetime.now(timezone.utc).astimezone(__timezone__))
    fg.image(url=feed_config['image'],
             title=feed_config['title'], link=feed_config['link'])
    fg.rights(rights=feed_config['copyright'])
    fg.link(href=feed_config['link'], rel='alternate')
    fg.ttl(300)
    fg.language('zh-TW')
    for post in posts:
        slug = post[field_name['slug']]
        guid = hashlib.sha224((base_url+slug).encode()).hexdigest()
        fe = fg.add_entry(order='append')
        fe.id(guid)
        name = post[field_name['name']]
        name = re.sub(escapse_char, '', name)
        fe.title(name)
        fe.link(href=base_url+slug, rel='alternate')
        fe.guid(guid)
        publishedDate = post[field_name['publishedDate']]
        if publishedDate is None:
            publishedDate = post['createdAt']
        fe.pubDate(util.formatRFC2822(parser.isoparse(publishedDate).astimezone(__timezone__)))
        if post['updatedAt']:
            fe.updated(util.formatRFC2822(parser.isoparse(post['updatedAt']).astimezone(__timezone__)))
        else:
            fe.updated(util.formatRFC2822(parser.isoparse(publishedDate).astimezone(__timezone__)))
        content = ''
        # draft_to_html()
        if post['heroImage']:
            img = post['heroImage']['resized']['original']
            fe.media.content(
                content={'url': img, 'medium': 'image'}, group=None)
            if post['heroCaption']:
                content += '<img src="%s" alt="%s" />' % (img, post['heroCaption'])
            else:
                content += '<img src="%s" />' % (img)
        brief = post[field_name['brief']]
        if brief:
            brief = re.sub(escapse_char, '', convert_draft_to_html(brief))
            fe.description(description=brief, isSummary=True)
            content += brief

        if post['content']:
            contentHtml = convert_draft_to_html(post['content'])
            if rm_ytbiframe:
                contentHtml = re.sub('<iframe.*?src="https://www.youtube.com/embed.*?</iframe>', '', contentHtml)
            content += contentHtml
        relateds = post[field_name['relatedPosts']]
        if len(relateds) > 0 and relatedPost_prefix:
            content += relatedPost_prefix
            for related_post in relateds[:3]:
                related_slug = related_post[field_name['slug']]
                related_name = post[field_name['name']]
                content += '<br/><a href="%s">%s</a>' % (base_url + related_slug, related_name)
        content = re.sub(escapse_char, '', content)
        fe.content(content=content, type='CDATA')
        categories = post[field_name['categories']]
        fe.category(
            list(map(lambda c: {'term': c[field_name['categories_name']], 'label': c[field_name['categories_name']]}, categories)))
        if 'writers' in post and post['writers']:
            fe.dc.dc_creator(creator=list(map(lambda w: w['name'], post['writers'])))

    return fg.rss_str(pretty=False, extensions=True, encoding='UTF-8', xml_declaration=True)


if __name__ == '__main__':
    relatedPost = '<br/><p class="read-more-vendor"><span>相關文章</span>'
    rm_ytbiframe = True
    gql_string = '''# Write your query or mutation here
        query{
        posts(where:{status:{equals:published}}, orderBy:{publishDate:desc}, take:100){
            id
            title
            publishDate
            category{
            name
            }
            heroCaption
            heroImage{
            urlOriginal
            resized{
                original
            }
            }
            brief
            content
            updatedAt
            relatedPosts{
            id
            title
            }
        }
        }'''
    dest_file = 'rss/standard_rss.xml'

    gql_endpoint = os.environ['GQL_ENDPOINT']
    rss_data = gql2rss(gql_endpoint, gql_string, relatedPost)
    with open(dest_file, 'w') as f:
        f.write(rss_data.decode())
        # upload_data(bucket, rss_data, 'application/xml', dest_file)
