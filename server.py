from flask import Flask, request
from data_export import gql2json, upload_data
import os

app = Flask(__name__)

@app.route("/gql_to_json")
def generate_json_from_gql():
	gql_endpoint = request.args.get('gql_endpoint')
	gql_string = request.args.get('gql_string')
	gcs_path = request.args.get('bucket')
	dest_file = request.args.get('dest_file')
	json_data = gql2json(gql_endpoint, gql_string)
	upload_data(bucket, json.dumps(json_data, ensure_ascii=False).encode('utf8'), 'application/json', gcs_path + dest_file)
	return "ok"

if __name__ == "__main__":
    app.run()
