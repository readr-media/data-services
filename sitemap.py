import xml.etree.cElementTree as ET
import pytz
import os
from urllib.parse import quote
from datetime import datetime

BASE_URL = os.environ.get('BASE_URL', None)
BUCKET   = os.environ.get('BUCKET', None)

tv_field_mapping = {
    'show': 'slug',
    'topic': 'slug',
    'tag': 'name'
}

app_mapping = {
    'tv': {
        'field_mapping': tv_field_mapping,
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

def generate_sitemaps(rows, app: str, object_name: str, chunk_size: int=1000):
    '''
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
    
    field_mapping = app_mapping[app]['field_mapping']
    field = field_mapping[object_name]

    for start_index in range(0, len(rows), chunk_size):
        end_index = min(start_index+chunk_size, len(rows))
        current_chunk = rows[start_index: end_index]

        root = ET.Element('urlset')
        root.attrib['xmlns'] = schema_loc
        for row in current_chunk:
            name = row.get(field, None)
            updatedAt = row.get('updatedAt', None)
            if field==None or updatedAt==None:
                continue
            timestamp_datetime_utc  = datetime.strptime(updatedAt, "%Y-%m-%dT%H:%M:%S.%f%z")
            timestamp_datetime_utc8 = timestamp_datetime_utc.astimezone(target_timezone)
            formatted_date = timestamp_datetime_utc8.strftime("%Y-%m-%d")
            
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, 'loc').text = BASE_URL + object_name + '/' + quote(name)
            ET.SubElement(doc, 'lastmod').text = formatted_date
        xml_strings.append(ET.tostring(root, encoding='utf-8'))
    return xml_strings
