# -*- coding: utf-8 -*-
import os
import re
import json
import pytz
import lxml.etree as ET
from datetime import datetime
from dateutil import parser
from lxml.etree import CDATA, Element
from utils.draft_converter import convert_draft_to_html
from configs import escapse_char

PROJECT_NAME = os.environ['PROJECT_NAME']
FIELD_NAME = json.loads(os.environ['FIELD_NAME_MAPPING'])


def parse_writer(writer, nsmap_dcterms):
    creator = Element(_tag='{%s}creator' % nsmap_dcterms, nsmap={
        'creator': nsmap_dcterms})
    creator.text = stringWrapper('author', writer['name'])
    return creator


def tsConverter(s):
    timeorigin = parser.parse(s)
    timediff = timeorigin - datetime(1970, 1, 1, tzinfo=pytz.utc)
    return round(timediff.total_seconds() * 1000)


def sub(parentItem, tag, content=None):
    element = ET.SubElement(parentItem, tag)
    if content:
        element.text = stringWrapper(tag, content)
    return element


# Can not accept structure contains 'array of array'
def recparse(parentItem, obj):
    t = type(obj)
    if t is dict:
        for name, value in obj.items():
            subt = type(value)
            # print(name, value)
            if subt is dict:
                thisItem = ET.SubElement(parentItem, name)
                recparse(thisItem, value)
            elif subt is list:
                for item in value:
                    if type(item) is ET._Element:
                        thisItem = parentItem.append(item)
                    else:
                        thisItem = ET.SubElement(parentItem, name)
                        recparse(thisItem, item)
            elif subt is ET._Element:
                thisItem = parentItem.append(value)
            elif subt is not str:
                thisItem = ET.SubElement(parentItem, name)
                thisItem.text = str(value)
            else:
                thisItem = ET.SubElement(parentItem, name)
                thisItem.text = stringWrapper(name, value)
    elif t is list:
        raise Exception('unsupported structure')
    elif t is str:
        parentItem.text = obj
    return


def stringWrapper(name, s):
    if name in ['title', 'content', 'author', 'writer', 'brief']:
        try:
            return CDATA(s)
        except UnicodeEncodeError:
            print(s.encode('utf-8', 'surrogateescape').decode('utf-8'))
            return f"<![CDATA[{s}]]>"
    else:
        return s


def parse_basic_field(post, is_video):
    if is_video:
        slug = post.get(FIELD_NAME['video_slug'])
        name = post.get(FIELD_NAME['video_name'])
    else:
        slug = post.get(FIELD_NAME['slug'])
        name = post.get(FIELD_NAME['name'])
    name = re.sub(escapse_char, '', name)
    publishedDate = post[FIELD_NAME['publishedDate']
                         ] if FIELD_NAME['publishedDate'] else post['createdAt']
    updated = post.get('updatedAt', publishedDate)
    if updated is None:
        updated = publishedDate
    return slug, name, publishedDate, updated


def parse_field(post, rm_ytbiframe, relatedPost_prefix, relatedPost_number:int):
    categories = post.get(FIELD_NAME['categories'], [])
    hero_image = post.get('heroImage', None)
    if hero_image:
        if hero_image.get('resize', None) and hero_image['resize'].get('original', None):
            pass
        elif 'urlOriginal' in hero_image and hero_image['urlOriginal']:
            hero_image['resize']['original'] = hero_image['urlOriginal']

    hero_caption = post.get('heroCaption', None)
    
    brief = post.get(FIELD_NAME['brief'], '')
    if brief:
        brief = re.sub(escapse_char, '', convert_draft_to_html(brief))
    
    post_content = post.get('content', '')
    content_html = ''
    if post_content:
        content_html = convert_draft_to_html(post_content)
        if rm_ytbiframe:
            content_html = re.sub(
                '<iframe.*?src="https://www.youtube.com/embed.*?</iframe>', '', content_html)

    related_posts = post.get(FIELD_NAME['relatedPosts'], [])
    if relatedPost_prefix and isinstance(related_posts, list) and len(related_posts) > 0:
        related_posts = related_posts[:relatedPost_number]
    else:
        related_posts = []
    return categories, hero_image, hero_caption, brief, content_html, related_posts
