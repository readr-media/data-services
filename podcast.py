import podcastparser
import urllib.request
import pytz
from datetime import datetime, timedelta
from data_export import upload_data

tz = pytz.timezone('Asia/Taipei')
def mirrorvoice_filter(author_filter, feedurl):
    parsed = podcastparser.parse(feedurl, urllib.request.urlopen(feedurl))

    #author_filter = os.environ['PODCAST_FILTER'].encode('utf8')
    all_eps = []
    if 'episodes' in parsed and isinstance(parsed['episodes'], list):
        for ep in parsed['episodes']:
            item = {}
            localtime = datetime.fromtimestamp(ep['published']).replace(tzinfo=tz)
            #+ timedelta(hours = 8)
            item['published'] = localtime.strftime("%m/%d/%Y, %H:%M:%S")
            item['author'] = ep['itunes_author']
            item['description'] = ep['description']
            item['heroImage'] = ep['episode_art_url']
            item['enclosures'] = ep['enclosures']
            item['link'] = ep['link']
            item['guid'] = ep['guid']
            item['title'] = ep['title']
            item['duration'] = str(timedelta(seconds=ep['total_time']))
            item['category'] = '新聞議題記者現場'
            all_eps.append(item)
    return all_eps


if __name__ == "__main__":  
    author_filter = []
    feedurl = 'https://feed.mirrorvoice.com.tw/rss/mnews.xml'
    podcasts = mirrorvoice_filter(author_filter, feedurl)
    print(podcasts)
    #print(json.dumps(podcasts, ensure_ascii=False))
