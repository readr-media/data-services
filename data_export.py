import os
import json

import pygsheets
from gql.transport.aiohttp import AIOHTTPTransport
from gql import gql, Client
from google.cloud import storage


def sheet2json( url, sheet ):
    gc = pygsheets.authorize(service_account_env_var = 'GDRIVE_API_CREDENTIALS')
    sht = gc.open_by_url( url )

    sheet_titles = sheet.split(',')
    sheets_obj = {}
    for sheet_title in sheet_titles:
        try:
            meta_sheet = sht.worksheet_by_title(sheet_title)
        except Exception as e:
            print("Exception: {}".format(type(e).__name__))
            print("Exception message: {}".format(e))
            continue

        meta_data = meta_sheet.get_all_values()
        field_names = [field_name for field_name in meta_data[0] if field_name != '']
        all_rows = []
        sheet_title_lower = sheet_title.lower()
        if sheet_title_lower in {'pageinfo', 'partners'}:
            all_rows = {}
        
        for i in range(1, len(meta_data)):
            row = meta_data[i]
            if not row[0]:
                continue

            values = {field_name:value for field_name, value in zip(field_names[0:], row[1:])}
            if sheet_title_lower == 'pageinfo':
                all_rows[row[0]] = values
            elif sheet_title_lower == 'partners':
                if row[0] in all_rows:
                    all_rows[row[0]].append(values)
                else:
                    all_rows[row[0]] = [values]
            elif len(field_names) == 1:
                all_rows.append(row[0])
            else:
                values = {field_name:value for field_name, value in zip(field_names, row)}
                new_values = {}
                for f in values:
                    s = f.split(":")
                    if len(s) > 1:
                        if s[0] not in new_values:
                            new_values[s[0]] = {}
                        new_values[s[0]][s[1]] = values[f]
                    else:
                        new_values[f] = values[f]
                all_rows.append(new_values)

        sheets_obj[sheet_title] = all_rows
    return sheets_obj

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
    if bucket_name:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        # blob.content_encoding = 'gzip'
        # try:
        #       data=bytes(data, encoding='utf-8'),
        # except:
        #     print(data)
        blob.upload_from_string(
            # data=gzip.compress(data=data, compresslevel=9),
            # data=bytes(data, encoding='utf-8'),
            data,
            content_type=content_type, client=storage_client)
        blob.content_language = 'zh'
        blob.cache_control = 'max-age=30,public'
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
