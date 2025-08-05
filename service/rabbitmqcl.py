"""
rabbitmqctl.py
rabbitmq의 매트릭을 수집합니다.
"""
import socket
from pyrabbit2.api import Client
from lib.prometheus_metric_util import generate_gauge
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from config import rabbitmq_info, resource_name, service_name


def get_rabbitmq_queue_item_cnt(queue_name: str, vhost_name: str = "/"):
    """ get_rabbitmq_queue_item_cnt """
    client = Client(rabbitmq_info['addr'], scheme='http', user=rabbitmq_info['user'], passwd=rabbitmq_info['passwd'])
    if client.is_alive():
        vhost_names = [h['name'] for h in client.get_all_vhosts()]
        if vhost_name in vhost_names:
            queue_names = [q['name'] for q in client.get_queues(vhost_name)]
            if queue_name in queue_names:
                item_count = client.get_queue_depth(vhost_name, queue_name)
                host_name = socket.gethostname()
                key = "queue_item_cnt"
                label = {"instance": host_name,
                         "metric": key,
                         "resource": resource_name,
                         "service": service_name,
                         "vhost_name": vhost_name,
                         "queue_name": queue_name}
                registry = CollectorRegistry()
                generate_gauge(key=key, label=label, value=item_count, registry=registry, host_name=host_name)
                gauge = generate_latest(registry=registry)
                return gauge.decode(), 200
            return "illegal queue name", 400
        return "illegal vhosts", 400
    return "client is dead.", 500
