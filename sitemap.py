import xml.etree.cElementTree as ET
import pytz
from datetime import datetime

def post_url(style, slug, id):
	if style = 'news' or style = 'review':
		return "https://www.readr.tw/post/{id}"
	if style = 'report': 
		return "https://www.readr.tw/project/{slug}"
	if style = 'project3': 
		return "https://www.readr.tw/project/3/{slug}"

def generate_sitemap( page, rows, uid = 'id', priority = '0.8', changefreq = 'weekly' ):

    _url = "https://www.mirrormedia.mg/"  # <-- Your website domain.
    dt = datetime.now().strftime("%Y-%m-%d")  # <-- Get current date and time.
    
    schema_loc = ("http://www.sitemaps.org/schemas/sitemap/0.9 "
                  "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")

    root = ET.Element("urlset")
    root.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    root.attrib['xsi:schemaLocation'] = schema_loc
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
    #root.attrib['xmlns:news'] = "http://www.sitemaps.org/schemas/sitemap-news/0.9"

    for slug in rows:
        if slug[uid] == '' or slug[uid] is None:
            next
        if "updatedAt" in slug and slug["updatedAt"] is not None:
            item_time = slug["updatedAt"]
        elif "createdAt" in slug and slug["createdAt"] is not None:
            item_time = slug["createdAt"]
        else:
            item_time = dt
        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = post_url(slug['style'], slug['slug'], slug['id'])
        ET.SubElement(doc, "lastmod").text = item_time
        #.replace(tzinfo=pytz.timezone('Asia/Taipei'))
        ET.SubElement(doc, "changefreq").text = changefreq
        ET.SubElement(doc, "priority").text = priority

            
    tree = ET.ElementTree(root)
    xml_string = ET.tostring(root, encoding='utf-8')
    return xml_string

def generate_news_sitemap( page, rows, uid = 'id', priority = '0.8', changefreq = 'weekly' ):

    _url = "https://www.readr.tw/"  # <-- Your website domain.
    dt = datetime.now().strftime("%Y-%m-%d")  # <-- Get current date and time.
    
    #schema_loc = ("http://www.sitemaps.org/schemas/sitemap/0.9 "
    #              "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")

    root = ET.Element("urlset")
    #root.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    #root.attrib['xsi:schemaLocation'] = schema_loc
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
    root.attrib['xmlns:news'] = "http://www.google.com/schemas/sitemap-news/0.9"

    for slug in rows:
        if slug[uid] == '' or slug[uid] is None:
            next
        if "updatedAt" in slug and slug["updatedAt"] is not None:
            item_time = slug["updatedAt"]
        elif "createdAt" in slug and slug["createdAt"] is not None:
            item_time = slug["createdAt"]
        else:
            item_time = dt
        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = post_url(slug['style'], slug['slug'], slug['id'])
        #ET.SubElement(doc, "lastmod").text = item_time
        #.replace(tzinfo=pytz.timezone('Asia/Taipei'))
        #ET.SubElement(doc, "changefreq").text = changefreq
        #ET.SubElement(doc, "priority").text = priority
        news_item = ET.SubElement(doc, "news:news")
        media = ET.SubElement(news_item, "news:publication")
        ET.SubElement(media, "news:name").text = "READr"
        ET.SubElement(media, "news:language").text = "zh-tw"
        ET.SubElement(news_item, "news:title").text = slug["title"]
        ET.SubElement(news_item, "news:publication_date").text = item_time

            
    tree = ET.ElementTree(root)
    xml_string = ET.tostring(root, encoding='utf-8')
    return xml_string

if __name__ == "__main__":
    result = generate_news_sitemap( "story", [ { "slug": "healthnews_d5f2db9d17756a72ca1b3d3380fb0931", "title": "123", "updatedAt": "2023-06-20T04:50:28.453Z" }, { "slug": "healthnews_1270bf939a8275e7de953525e5aca38a", "title": "456", "updatedAt": "2023-06-20T04:50:28.434Z"}], "slug" )
    print(result)
