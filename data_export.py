import os
import re
import json
import sys
import codecs
import pygsheets
from gql.transport.aiohttp import AIOHTTPTransport
from gql import gql, Client
from datetime import datetime, timedelta
from google.cloud import datastore
from google.oauth2 import service_account
from google.cloud import storage

def sheet2json( url, sheet ):

	gc = pygsheets.authorize(service_account_env_var = 'GDRIVE_API_CREDENTIALS')
	sht = gc.open_by_url( url )

	meta_sheet = sht.worksheet_by_title(sheet)
	meta_data = meta_sheet.get_all_values()
	#if sheet_name == 'translateurl_for_website':
	#    field_shift = 1
	#else:
	#    field_shift = 0

		#get the field name
	field_name = []
	for f in meta_data[0]:
		if f != '':
			field_name.append(f)
	all_rows = []
	for row in range(1, len(meta_data)):
		if meta_data[row][1] != '':
			values = {}
			for field in range(0, len(field_name)):
				if field < len(meta_data[row]):
					values[field_name[field]] = meta_data[row][field]
				else:
					values[field_name[field]] = ''
			all_rows.append(values)

	return all_rows
	

def gql2json(gql_endpoint, gql_string):
    #bucket = os.environ['BUCKET']
    #destination = os.environ('DEST']
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport,
                        fetch_schema_from_transport=False)
    # sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    query = gql(gql_string)
    json_data = gql_client.execute(query)
    #upload_data(bucket, json.dumps(json_data, ensure_ascii=False).encode('utf8'), 'application/json', gcs_path + DEST)
    return json_data

def upload_data(bucket_name: str, data: str, content_type: str, destination_blob_name: str):
    '''Uploads a file to the bucket.'''
    # bucket_name = 'your-bucket-name'
    # data = 'storage-object-content'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    # blob.content_encoding = 'gzip'
    try:
        data=bytes(data, encoding='utf-8'),
    except:
        print(data)
    blob.upload_from_string(
        # data=gzip.compress(data=data, compresslevel=9),
        #data=bytes(data, encoding='utf-8'),
        data=bytes(data),
        content_type=content_type, client=storage_client)
    blob.content_language = 'zh'
    blob.cache_control = 'max-age=300,public'
    blob.patch()

if __name__ == "__main__":  
    gql_string = """
query { allPosts(where: { tags_every: {name_in: "疫苗"}, state: published }, orderBy: "publishTime_DESC", first: 3) {
    style
    title: name
	slug
    brief
    briefApiData
    contentApiData
    publishTime
    heroImage {
      tiny: urlTinySized
      mobile: urlMobileSized
      tablet: urlTabletSized
      desktop: urlDesktopSized
    } 
    updatedAt
    source
    isAdult
  }
}
"""
    #gql_endpoint = "https://api-dev.example.com"
    #gql2json(gql_endpoint, gql_string)
    keyfile = { }
    os.environ['GDRIVE_API_CREDENTIALS'] = json.dumps(keyfile)
    sheet_content = sheet2json("https://docs.google.com/spreadsheets/d/19Z9vgm9nIV1ZltljKQIzHDR_HhVp3WO0N4K2dCYzmrY/edit#gid=1662192222", "Content")
    print(sheet_content)
