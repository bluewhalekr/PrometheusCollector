from elasticsearch import Elasticsearch
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta, timezone
from config import els_address, slack_channel_name

slack_token = ""

KST = timezone(timedelta(hours=9))

esl_query = [
    {
        "bool": {
            "must": {"match_phrase": {"message": {"query": "Finished: FAILURE"}},
                     "filter": {"range": {"@timestamp": {"gte": "now-30s", "lt": "now"}}}}
        }
    },
    ]


slack_msg_format = "[\n\tProjectName = {project_name}\n\tBuildHost = {build_host}\n\tBuildDuration = {build_duration}\n\tDate = {date}\n]"


def send_msg(project_name: str, build_host: str, build_duration: str):
    with WebClient(token=slack_token) as client:
        try:
            text = slack_msg_format.format(project_name=project_name, build_host=build_host, build_duration=build_duration, date=datetime.now(KST))
            response = client.chat_postMessage(
                channel=slack_channel_name,
                text=text)
            print(response)
        except SlackApiError as e:
            assert e.response["error"]


def get_errors(els_uri: str) -> int:
    cnt = 0
    with Elasticsearch(els_uri) as es:
        results = es.search(index="file*",
                            query=esl_query,
                            sort="@timestamp:desc")
        if len(results['hits']['hits']) > 0:
            for log in results['hits']['hits']:
                project_name = log['_source']['data']['projectName']
                build_host = log['_source']['data']['buildHost']
                build_duration = log['_source']['data']['buildDuration']
                send_msg(project_name=project_name,
                         build_host=build_host,
                         build_duration=build_duration)
                cnt += 1
    return cnt


def synchronize_metric() -> dict:
    get_errors(els_address)
    return {}


def run():
    import os
    global slack_token
    slack_token = os.environ["SLACK_API_TOKEN"]
    synchronize_metric()
