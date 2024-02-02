import xml.etree.cElementTree as ET
import pytz
import os
from urllib.parse import quote
from datetime import datetime

BASE_URL = os.environ.get('BASE_URL', None)
BUCKET   = os.environ.get('BUCKET', None)

mnews_field_mapping = {
    'show': 'slug',
    'topic': 'slug',
    'tag': 'name',
    'post': 'slug'
}

app_mapping = {
    'mnews': {
        'field_mapping': mnews_field_mapping,
        'publisher_name': '鏡電視',
    }
    ### TODO: mapping for other app, eg. Readr
}

def generate_sitemap_index(sitemap_files):
    '''
    Input:
        sitemap_files - All the urls of sitemap file that you'd like to submit to Google Search Console
    Output:
        xml_string - sitemap_index.xml
    '''
    schema_loc = "http://www.sitemaps.org/schemas/sitemap/0.9"
    root = ET.Element('sitemapindex')
    root.attrib['xmlns'] = schema_loc
    for info in sitemap_files:
        filename = info['filename']
        doc = ET.SubElement(root, "sitemap")
        ET.SubElement(doc, 'loc').text = f'https://storage.googleapis.com/{BUCKET}/{filename}'
        ET.SubElement(doc, 'lastmod').text = info['lastmod']
    xml_string = ET.tostring(root, encoding='utf-8')
    return xml_string

def generate_web_sitemaps(rows, app: str, object_name: str, chunk_size: int=1000):
    '''
    Description:
        Generate the url sitemaps inside our website
    Input:
        rows        - The json returned from gql query
        app         - readr, tv, ...etc
        object_name - tag, show, topic, ...etc
        chunk_size  - Split number of rows into multiple sitemaps by chunk_size
    Output:
        [xml_string] - The array of xml_string format after encoding='utf-8'
    Note:
        Google would ignore "changefreq" and "priority", don't need to provide them now
    '''
    xml_strings = []
    target_timezone = pytz.timezone('Asia/Taipei')
    schema_loc = "http://www.sitemaps.org/schemas/sitemap/0.9"
    
    app_info = app_mapping[app]
    field = app_info['field_mapping'][object_name]

    for start_index in range(0, len(rows), chunk_size):
        end_index = min(start_index+chunk_size, len(rows))
        current_chunk = rows[start_index: end_index]

        root = ET.Element('urlset')
        root.attrib['xmlns'] = schema_loc
        for row in current_chunk:
            slug = row.get(field, None) # slug is a appended string behind website url
            updatedAt = row.get('updatedAt', None)
            if slug==None or updatedAt==None:
                continue
            timestamp_datetime_utc  = datetime.strptime(updatedAt, "%Y-%m-%dT%H:%M:%S.%f%z")
            timestamp_datetime_utc8 = timestamp_datetime_utc.astimezone(target_timezone)
            formatted_date = timestamp_datetime_utc8.strftime("%Y-%m-%d")
            
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, 'loc').text = BASE_URL + object_name + '/' + quote(slug)
            ET.SubElement(doc, 'lastmod').text = formatted_date
        xml_strings.append(ET.tostring(root, encoding='utf-8'))
    return xml_strings

def generate_news_sitemaps(rows, app: str, language: str='zh-tw', chunk_size: int=1000):
    '''
    Description:
        Generate the url sitemaps of stories(post news)
    Input:
        rows        - The json returned from gql query
        app         - readr, tv, ...etc
        language    - languge of publication, eg. en, zh-tw and so on
        chunk_size  - Split number of rows into multiple sitemaps by chunk_size
    Output:
        [xml_string] - The array of xml_string format after encoding='utf-8'
    Note:
        Google would ignore "changefreq" and "priority", don't need to provide them now
    '''
    xml_strings = []
    object_name = "post"
    target_timezone = pytz.timezone('Asia/Taipei')
    schema_loc      = "http://www.sitemaps.org/schemas/sitemap/0.9"
    schema_news_loc = "http://www.google.com/schemas/sitemap-news/0.9"
    
    app_info = app_mapping[app]
    field = app_info['field_mapping'][object_name]
    publisher_name = app_info['publisher_name']

    for start_index in range(0, len(rows), chunk_size):
        end_index = min(start_index+chunk_size, len(rows))
        current_chunk = rows[start_index: end_index]

        root = ET.Element('urlset')
        root.attrib['xmlns'] = schema_loc
        root.attrib['xmlns:news'] = schema_news_loc
        for row in current_chunk:
            slug = row.get(field, None) # slug is a appended string behind website url
            title = row.get('name', None)
            publishTime = row.get('publishTime', None)
            if slug==None or publishTime==None or title==None:
                continue
            timestamp_datetime_utc  = datetime.strptime(publishTime, "%Y-%m-%dT%H:%M:%S.%f%z")
            timestamp_datetime_utc8 = timestamp_datetime_utc.astimezone(target_timezone)
            formatted_date = timestamp_datetime_utc8.strftime("%Y-%m-%d")
            
            ### Create <url> tag
            url = ET.SubElement(root, "url")
            ET.SubElement(url, 'loc').text = BASE_URL + 'story' + '/' + quote(slug)
            
            ### Create <news:news> tag
            news = ET.SubElement(url, "news:news")
            publication = ET.SubElement(news, "news:publication")
            ET.SubElement(publication, 'news:name').text = publisher_name
            ET.SubElement(publication, 'news:language').text = language
            ET.SubElement(news, "news:publication_date").text = formatted_date
            ET.SubElement(news, "news:title").text = title
        xml_strings.append(ET.tostring(root, encoding='utf-8'))
    return xml_strings
