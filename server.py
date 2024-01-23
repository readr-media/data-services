from flask import Flask, request
from data_export import sheet2json, gql2json, upload_data
from rss_generator import gql2rss
from scheduled_update import status_update
from podcast import mirrorvoice_filter
from sitemap import generate_sitemap
import os
import json

app = Flask(__name__)
gql_endpoint = os.environ['GQL_ENDPOINT']

@app.route("/gql_to_json")
def generate_json_from_gql():
	gql_string = request.args.get('gql_string')
	bucket = request.args.get('bucket')
	dest_file = request.args.get('dest_file')
	alt_gql_endpoint = request.args.get('gql_endpoint')
	if alt_gql_endpoint:
		gql_endpoint = alt_gql_endpoint
	else:
		gql_endpoint = os.environ['GQL_ENDPOINT']
	json_data = gql2json(gql_endpoint, gql_string)
	upload_data(bucket, json.dumps(json_data, ensure_ascii=False).encode('utf8'), 'application/json', dest_file)
	return "ok"

@app.route("/sheet_to_json")
def generate_json_from_sheet():
	sheet_url = request.args.get('sheet_url')
	sheet_name = request.args.get('sheet_name')
	bucket = request.args.get('bucket')
	dest_file = request.args.get('dest_file')
	json_data = sheet2json(sheet_url, sheet_name)
	upload_data(bucket, json.dumps(json_data, ensure_ascii=False).encode('utf8'), 'application/json', dest_file)
	return "ok"
    
@app.route("/cron_update")
def scheduled_publish():
    return_message = status_update()
    return return_message

@app.route("/sitemap/generator")
def sitemap_generator():
    query = request.args.get('query')
    list_name = request.args.get('list_name')
    page = request.args.get('page')
    id_field = request.args.get('id_field')
    priority = request.args.get('priority')
    dest_file = request.args.get('dest_file')
    news_sitemap_dest = request.args.get('news_sitemap')
    
    BUCKET = os.environ['BUCKET']
    GQL_PREVIEW_ENDPOINT = os.environ.get('GQL_PREVIEW_ENDPOINT', 'http://localhost:3000/api/graphql')
    transport = RequestsHTTPTransport(url=GQL_PREVIEW_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    now = datetime.utcnow().isoformat(timespec='microseconds') + "Z"
    sitemap = ''
    with client as session:
        resp = session.execute(gql(query))
        if len(resp[list_name]) == 0:
            return 'No externals result'
        else:
            if list_name in resp:
                sitemap = generate_sitemap( page, resp[list_name], id_field, priority)
            else:
                print(resp)
            if news_sitemap_dest:
                news_sitemap_dest = generate_news_sitemap( page, resp[list_name], id_field, priority)
                upload_data(BUCKET, news_sitemap, "Application/xml", news_sitemap_dest)
    upload_data(BUCKET, sitemap, "Application/xml", dest_file)
    return "OK"

@app.route("/sitemap/posts")
def generate_posts_sitemap():
    BUCKET = os.environ['BUCKET']
    GQL_PREVIEW_ENDPOINT = os.environ.get('GQL_PREVIEW_ENDPOINT', 'http://localhost:3000/api/graphql')
    transport = RequestsHTTPTransport(url=GQL_PREVIEW_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    sitemap = ''
    with client as session:
        query = '''
			query Posts {
			  posts(take:3000, where: { state: { equals: "published"}}, orderBy: { id: desc}) {
				slug
				id
				style
				name
			  }
			}
		'''
        resp = session.execute(gql(query))
        if len(resp['posts']) == 0:
            return 'No externals result'
        else:
            if 'posts' in resp:
                sitemap = generate_sitemap( 'post', resp['posts'], 'id', "1.0")
                news_sitemap = generate_news_sitemap( 'story', resp['posts'][:700], 'slug', "1.0")
            else:
                print(resp)
    upload_data(BUCKET, sitemap, "Application/xml", "rss/posts.xml")
    upload_data(BUCKET, news_sitemap, "Application/xml", "rss/posts-news.xml")
    return "OK"

@app.route("/k6_to_rss")
def generate_rss_from_k6():
	gql_string = request.args.get('gql_string')
	bucket = request.args.get('bucket')
	schema_type = request.args.get('schema_type')
	dest_file = request.args.get('dest_file')
	relatedPost = request.args.get('relatedPost')
	rm_ytbiframe = request.args.get('rm_ytbiframe')
	relatedPost_number = request.args.get('relatedPost_number')
	rss_data = gql2rss(gql_endpoint, gql_string, schema_type, relatedPost, rm_ytbiframe, relatedPost_number)
	if rss_data:
		upload_data(bucket, rss_data, 'application/xml', dest_file)
		return "ok"
	return "fail"

@app.route("/mirrormedia_podcast")
def get_podcasts_from_mirrorvoice():
    feedurl = request.args.get('feed_url', default = 'https://feed.mirrorvoice.com.tw/rss/mnews.xml')
    bucket = request.args.get('bucket')
    dest_file = request.args.get('dest_file')
    author_filter = []
    podcast_json = mirrorvoice_filter(author_filter, feedurl)
    json_data = json.dumps(podcast_json, ensure_ascii=False).encode('utf8')
    upload_data(bucket, json_data, 'application/json', dest_file)
    return "ok"

if __name__ == "__main__":
    app.run()
