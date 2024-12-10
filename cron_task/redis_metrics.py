"""
collect redis metric by cron
"""
from redis import StrictRedis
from config import redis_hosts, redis_use_ssl
from lib.syncmanager import SMManagerPutDeco
import logging


def get_metric(host: str, port: int, user: str, passwd: str, is_ssl: bool = False):
    """collect metric"""
    with StrictRedis(socket_timeout=5, password=passwd,
                     host=host, port=port,
                     username=user if len(user) > 0 else None, ssl=is_ssl) as conn:
        infos = conn.info()
        conn.close()
        return infos


@SMManagerPutDeco
def synchronize_metric() -> dict:
    """collect metric and store to shared memory"""
    metrics = {}
    for redis_info in redis_hosts:
        if len(redis_info) > 4:
            redis = redis_info.split(":")
            logging.info(f'redis = {redis}, {redis_info}')
            if len(redis) == 5:
                key = f"{redis[2]}:{redis[3]}:{redis[4]}"
            else:
                key = f"{redis[2]}:{redis[3]}:Unknown"
            metrics[key] = get_metric(host=redis[2],
                                      port=int(redis[3]),
                                      user=redis[0],
                                      passwd=redis[1],
                                      is_ssl=redis_use_ssl)
    return metrics


def run():
    """main"""
    synchronize_metric()
