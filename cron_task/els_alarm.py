from elasticsearch import Elasticsearch
from datetime import datetime, timedelta, timezone
from config import els_address
from service.slack import send_msg

slack_token = ""

KST = timezone(timedelta(hours=9))

esl_query = {
    "bool": {
        "must": {
            "match": {
                "log.level": "ERROR"
            }
        },
        "filter": {
            "range": {
                "@timestamp": {
                    "gte": "now-30s", "lt": "now"
                }
            }
        }
    }
}


slack_msg_format = "[\n\tSystem = {system}\n\tLevel = {level}\n\tMsg = {msg}\n\tDate = {date}\n]"


def get_errors(els_uri: str) -> int:
    cnt = 0
    with Elasticsearch(els_uri) as es:
        results = es.search(index="file*",
                            query=esl_query,
                            sort="@timestamp:desc")
        if len(results['hits']['hits']) > 0:
            for log in results['hits']['hits']:
                system = log['_source']['host']['hostname']
                level = log['_source']['log']['level']
                msg_parts = log['_source']['log']['log'].split(level + "  ")
                slack_msg = slack_msg_format.format(system=system, level=level, msg=msg_parts[1], date=datetime.now(KST))
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
