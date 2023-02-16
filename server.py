from flask import Flask, request
from data_export import sheet2json, gql2json, upload_data
import os
import json

app = Flask(__name__)

@app.route("/gql_to_json")
def generate_json_from_gql():
	gql_endpoint = request.args.get('gql_endpoint')
	gql_string = request.args.get('gql_string')
	bucket = request.args.get('bucket')
	dest_file = request.args.get('dest_file')
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
    

if __name__ == "__main__":
    app.run()
