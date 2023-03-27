from dateutil import parser,tz
import lxml.etree as ET
from lxml.etree import Element
from feedgen import util
import hashlib
import re
import os
import json
from utils.draft_converter import convert_draft_to_html
from utils.rss_fmt_parser import recparse, sub, stringWrapper, parse_writer, parse_basic_field, parse_field
from configs import feed_config, escapse_char


FIELD_NAME = json.loads(os.environ['FIELD_NAME_MAPPING'])
FEED_CONFIG_MAPPING = json.loads(os.environ['FEED_CONFIG_MAPPING'])
timezone = tz.gettz("Asia/Taipei")
feed_config.update(FEED_CONFIG_MAPPING)
base_url = feed_config['baseURL']
nsmap_media = feed_config['media']
nsmap_dcterms = feed_config['dcterms']
nsmap_content = feed_config['content']
title = feed_config['title']


def parse_post_genral(post, relatedPost_prefix: str = '', is_video: bool = False, rm_ytbiframe: str = '',  relatedPost_number:int=3):
    slug, name, publishedDate, updated = parse_basic_field(post, is_video)
    item = {
            "guid": hashlib.sha224((base_url+slug).encode()).hexdigest(),
            "title": name,
            "link": base_url + slug,
            "pubDate": util.formatRFC2822(parser.isoparse(publishedDate).astimezone(timezone)),
            "updated": util.formatRFC2822(parser.isoparse(updated).astimezone(timezone)),
        }
    
    content = ''
    relatedPost_html = ''
    if is_video:
        video_url = post['urlOriginal'] if post['urlOriginal'] else post['file']['url']
        post_content = post['content']
        if post_content:
            content = re.sub(escapse_char, '', convert_draft_to_html(post_content))
        item.update({
            "link": video_url,
            "description": content,
            "media:content": Element(_tag='{%s}content' % nsmap_media, nsmap={'media': nsmap_media}, type="video/mp4", medium="video", url=video_url, isDefault="true"),
            "media:credit": Element(_tag='{%s}credit' % nsmap_media, nsmap={'media': nsmap_media}, role="author"),
            "media:keywords": Element(_tag='{%s}keywords' % nsmap_media, nsmap={'media': nsmap_media}),
            "category": "影音"
        })
        item["media:credit"].text = stringWrapper('author', title)
    else:
        categories, hero_image, hero_caption, brief, content_html, related_posts = parse_field(post, rm_ytbiframe, relatedPost_prefix, relatedPost_number)
        
        item['category'] = list(c[FIELD_NAME['categories_name']]for c in categories)

        if hero_image:
            img = hero_image['resized']['original']
            item["media:content"] = Element(_tag='{%s}content' % nsmap_media, nsmap={'media': nsmap_media}, url=img, medium='image')
            alt = f"alt=\"{post['heroCaption']}\""  if hero_caption else ''
            content += f"<img src=\"{img}\" {alt}/>"

        if brief:
            item["description"] = brief
            content += brief

        if content_html:
            content += content_html
        
        if related_posts:
            relatedPost_html += relatedPost_prefix
            for related_post in related_posts:
                related_slug = related_post[FIELD_NAME['slug']]
                related_name = post[FIELD_NAME['name']]
                relatedPost_html += '<br/><a href="%s">%s</a>' % (base_url + related_slug, related_name)
        
        content += relatedPost_html
        content = re.sub(escapse_char, '', content)
        item["content:encoded"] = Element(_tag='{%s}encoded' % nsmap_content, nsmap={'content': nsmap_content})
        item["content:encoded"].text = stringWrapper('content', content)

        writers = post.get('writers', [])
        if writers:
            item["dc:creator"] = [parse_writer(w, nsmap_dcterms) for w in writers]

    return item


def gen_general_rss(posts, relatedPost_prefix, is_video: bool, rm_ytbiframe: bool= True, relatedPost_number: int = 3):
    
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
        "item": [parse_post_genral(post, relatedPost_prefix, is_video, rm_ytbiframe, relatedPost_number) for post in posts]
    }
    root = Element('rss', nsmap={'content': nsmap_content,
                   'media': nsmap_media, 'dcterms': nsmap_dcterms}, version='2.0')
    channel = sub(root, 'channel')

    recparse(channel, mainXML)
    return f'<?xml version="1.0" encoding="UTF-8" ?>{ET.tostring(root, encoding="unicode")}'