"""
check_mongod.py
"""
import os
from datetime import datetime, timedelta, timezone
from service.slack import send_msg as slack_send_msg
from collector_cron import logger

KST = timezone(timedelta(hours=9))

slack_msg_format = "[\n\tSystem = {system}\n\tLevel = {level}\n\tMsg = {msg}\n\tDate = {date}\n]"


def send_msg(system, slack_token):
    """
    send msg to slack
    """
    msg = 'Mongod is restarted by collector_cron.'
    slack_msg = slack_msg_format.format(system=system, level="info", msg=msg, date=datetime.now(KST))
    slack_send_msg(slack_msg=slack_msg, slack_token=slack_token)
    logger.info(f"Message is sent.{msg}")


def mongo_is_alive() -> int:
    """
    check mongo is alive
    """
    from pymongo import MongoClient
    from config import mongodb_uri
    import pymongo
    client = MongoClient(mongodb_uri, connectTimeoutMS=1000, timeoutMS=1000)
    is_alive = 1
    try:
        client.admin.command('ping')
        logger.info("Mongod is alive.")
    except pymongo.errors.ServerSelectionTimeoutError:
        logger.error("time out")
        is_alive = 0
    return is_alive


def check_and_run_task(slack_token) -> dict:
    """
    check_and_run_task
    """
    metric = mongo_is_alive()
    from config import service_name
    if metric == 0:
        import subprocess
        logger.info(f"check_and_run_task 2-0.[{service_name} : dead]")
        status = subprocess.check_output("systemctl restart mongod", shell=True)
        logger.info(status)
        send_msg(service_name, slack_token=slack_token)
        return {"status": status}
    logger.info(f"check_and_run_task 3-0.[{service_name} : normal]")
    return {"status": "OK"}


def run():
    """
    call back function of cron task
    """
    slack_token = os.environ["SLACK_API_TOKEN"]
    check_and_run_task(slack_token=slack_token)


if __name__ == "__main__":
    run()
