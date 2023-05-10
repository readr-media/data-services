import time
import uuid
import os
import re
import json
import lxml.etree as ET
from lxml.etree import Element
from datetime import timedelta
from utils.draft_converter import convert_draft_to_html
from utils.rss_fmt_parser import recparse, tsConverter, parse_basic_field, parse_field
from configs import feed_config, escapse_char


FIELD_NAME = json.loads(os.environ['FIELD_NAME_MAPPING'])
FEED_CONFIG_MAPPING = json.loads(os.environ['FEED_CONFIG_MAPPING'])
news_available_days = 365
feed_config.update(FEED_CONFIG_MAPPING)
base_url = feed_config['baseURL']


def parse_post_line(post, relatedPost_prefix: str, is_video: bool, rm_ytbiframe: str, relatedPost_number: int):
    slug, name, publishedDate, updated = parse_basic_field(post, is_video)
    availableDate = max(tsConverter(publishedDate), tsConverter(updated))

    item = {
        'ID': post['id'],
        'nativeCountry': 'TW',
        'language': 'zh',
        'startYmdtUnix': availableDate,
        'endYmdtUnix': tsConverter(publishedDate) + (round(timedelta(news_available_days, 0).total_seconds()) * 1000),
        'title': name,
        'category': '',
        'publishTimeUnix': tsConverter(publishedDate),
        'updateTimeUnix': tsConverter(updated),
        'contentType': 0,
        'contents': {}
        
    }

    content = ''
    relatedPost_html = ''
    content_html = ''

    if is_video:
        video_url = post['urlOriginal'] if post['urlOriginal'] else post['file']['url']
        item.update({
            'category': "影音",
            'contents': {'video': {'url': video_url}, 'text': {'content': ''}},
        })
        post_content = post.get('content', '')
        if post_content:
            content_html = convert_draft_to_html(post_content)
            if rm_ytbiframe:
                content_html = re.sub(
                    '<iframe.*?src="https://www.youtube.com/embed.*?</iframe>', '', content_html)

        related_posts = post.get(FIELD_NAME['relatedPosts'], [])
        if relatedPost_prefix and isinstance(related_posts, list) and len(related_posts) > 0:
            related_posts = related_posts[:relatedPost_number]
    else:
        categories, hero_image, hero_caption, brief, content_html, related_posts = parse_field(
            post, rm_ytbiframe, relatedPost_prefix, relatedPost_number)
        item['category'] = categories[0][FIELD_NAME['categories_name']] if len(
            categories) > 0 else ['不分類'] #category is a required tag
        item['sourceUrl'] = base_url + slug + \
            feed_config['utmSource'] % ('line', slug)

        if hero_image:
            img = hero_image['resized']['original']
            item['thumbnail'] = img
            
            if hero_caption:
                content += f"<figure class=\"image\"><img alt=\"{hero_caption}\" src=\"{img}\"><figcaption>{hero_caption}</figcaption></figure>"
                item['contents']['image'] = {'url': img, 'description': hero_caption}
            else:
                content += f"<img src=\"{img}\">"
                item['contents']['image'] = {'url': img}
        else:  # logo image as heroimage
            content += f"<figure class=\"image\"><img alt=\"logo\" src=\"{feed_config['image']}\"><figcaption>logo</figcaption></figure>"

        if brief:
            content += brief

    if content_html:
        content += content_html + feed_config['officialLine']

    if related_posts:
        relatedPost_html += relatedPost_prefix
        recommendArticles = []
        for related_post in related_posts:
            related_slug = related_post[FIELD_NAME['slug']]
            related_name = related_post[FIELD_NAME['name']]
            relatedPostUrl = base_url + related_slug + feed_config['utmSource'] % ('line', slug)
            relatedPost_html += '<li><a href="%s">%s</li>' % (relatedPostUrl, related_name)

            recommendArticle = {'title': related_name, 'url': relatedPostUrl}
            if related_post['heroImage']:
                recommendArticle['thumbnail'] = related_post['heroImage']['resized']['original']
            recommendArticles.append(recommendArticle)
        relatedPost_html += "</ul>"
        item['recommendArticles'] = {'article': recommendArticles}
        
    content += relatedPost_html
    content = re.sub(escapse_char, '', content)
    item['contents']['text'] = {'content': content}

    item['author'] = feed_config['title']

    tags = post.get('tags', None)
    if tags:
        item['tags'] = {'tag': [tag['name'] for tag in tags]}
    return item


def gen_line_rss(posts, relatedPost_prefix: str, is_video: bool = False, rm_ytbiframe: str = '', relatedPost_number: int = 3):

    mainXML = {
        'UUID': str(uuid.uuid4()),
        'time': int(round(time.time() * 1000)),
        'article': [parse_post_line(post, relatedPost_prefix, is_video, rm_ytbiframe, relatedPost_number) for post in posts]
    }
    root = Element('articles')
    recparse(root, mainXML)
    return f'<?xml version="1.0" encoding="UTF-8" ?>{ET.tostring(root, encoding="unicode")}'
