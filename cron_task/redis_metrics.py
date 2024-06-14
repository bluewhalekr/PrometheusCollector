from redis import StrictRedis
from config import redis_hosts, redis_use_ssl
from lib.syncmanager import SMManagerPutDeco


def get_metric(host: str, port: int, user: str, passwd: str, is_ssl: bool = False):
    with StrictRedis(socket_timeout=5, password=passwd, host=host, port=port, username=user if len(user) > 0 else None, ssl=is_ssl) as conn:
        infos = conn.info()
        conn.close()
        return infos


@SMManagerPutDeco
def synchronize_metric() -> dict:
    redis_list = redis_hosts.split(",")
    metrics = {}
    for redis_info in redis_list:
        redis = redis_info.split(":")
        metrics[f"{redis[2]}:{redis[3]}"] = get_metric(host=redis[2], port=int(redis[3]), user=redis[0], passwd=redis[1], is_ssl=redis_use_ssl)
    return metrics


def run():
    synchronize_metric()
