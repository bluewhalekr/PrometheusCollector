""" os_util """
import platform
import socket
from prometheus_client import Gauge, CollectorRegistry, generate_latest
from lib.prometheus_metric_util import generate_gauge


def get_os_version():
    """ get_mongo_is_alive """
    from config import resource_name, service_name
    key = "os_version"
    host_name = socket.gethostname()

    os_ver = float(platform.freedesktop_os_release().get("VERSION_ID"))
    major_ver = int(os_ver)
    minor_ver = (os_ver * 100) % 100
    label = {"instance": host_name, "metric": "os_version", "resource": resource_name, "service": service_name, "major": major_ver, "minor": minor_ver}
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label, value=os_ver, registry=registry, host_name=host_name)
    return generate_latest(registry=registry)
