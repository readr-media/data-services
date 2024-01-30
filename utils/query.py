import os
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

def gql_fetch(gql_endpoint, gql_string, gql_variable=None):
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport,
                        fetch_schema_from_transport=True)
    if gql_variable:
        json_data = gql_client.execute(gql(gql_string))
    else:
        json_data = gql_client.execute(gql(gql_string), variable_values=gql_variable)
    return json_data

gql_tv_allTags = """
query AllTags {
    items: allTags(sortBy: [updatedAt_DESC], where: {slug_not: null}) {
        id
        slug
        name
        updatedAt
        createdAt
    }
}
"""

gql_tv_allTopics = """
query AllTopics {
    items: allTopics(sortBy: [updatedAt_DESC], where: { slug_not: null, state: published }) {
        id
        slug
        updatedAt
        createdAt
    }
}
"""

gql_tv_allShows = """
query AllShows {
    items: allShows(sortBy: [updatedAt_DESC], where: { slug_not: null }) {
        id
        slug
        updatedAt
        createdAt
    }
}
"""

tv_object_mapping = {
    'show': gql_tv_allShows,
    'topic': gql_tv_allTopics,
    'tag': gql_tv_allTags
}