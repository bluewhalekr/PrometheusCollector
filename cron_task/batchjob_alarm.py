from elasticsearch import Elasticsearch
from datetime import datetime, timedelta, timezone
from config import els_address
from service.slack import send_msg
import logging

slack_token = ""

KST = timezone(timedelta(hours=9))

esl_query = {
        "bool": {
            "must": [{
                "match_phrase": {"message": {"query": "Finished: FAILURE"}},
            }],
            "filter": {
                "bool": {
                    "must": [{"range": {"@timestamp": {"gte": "now-30s", "lt": "now"}}}]
                }
            }
        }
    }

slack_msg_format = "[\n\tProjectName = {project_name}\n\tBuildHost = {build_host}\n\tBuildDuration = {build_duration}\n\tDate = {date}\n]"


def get_errors(els_uri: str) -> int:
    cnt = 0
    with Elasticsearch(els_uri) as es:
        results = es.search(index="jenkins-log2*",
                            query=esl_query,
                            sort="@timestamp:desc")
        logging.info(f"es result = {results}")
        if len(results['hits']['hits']) > 0:
            for log in results['hits']['hits']:
                logging.info(f"es log = {log}")
                project_name = log['_source']['data']['projectName']
                build_host = log['_source']['data']['buildHost']
                build_duration = log['_source']['data']['buildDuration']
                slack_msg = slack_msg_format.format(project_name=project_name, build_host=build_host, build_duration=build_duration, date=datetime.now(KST))
                send_msg(slack_msg=slack_msg, slack_token=slack_token)
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
