from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import slack_channel_name
import logging


def send_msg(slack_msg: str, slack_token: str):
    client = WebClient(token=slack_token)
    try:
        response = client.chat_postMessage(
            channel=slack_channel_name,
            text=slack_msg)
        logging.info(f'{response}')
    except SlackApiError as e:
        logging.error(f'{e}')
