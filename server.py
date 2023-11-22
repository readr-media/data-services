from flask import Flask, request
from data_export import sheet2json, gql2json, upload_data
from rss_generator import gql2rss
from scheduled_update import status_update
from podcast import mirrorvoice_filter
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
    podcast_json = mirrorvoice_filter(author_filter, feedurl)
    #print(podcast_json)
    json_data = json.dumps(podcast_json, ensure_ascii=False).encode('utf8')
    upload_data(bucket, json_data, 'application/json', dest_file)
    return "ok"

if __name__ == "__main__":
    app.run()
