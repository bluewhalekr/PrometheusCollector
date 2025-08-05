"""Generate View Page"""
import os
from prometheus_client import Gauge, CollectorRegistry, generate_latest
from config import resource_name, service_name
from config import mysql_host, mysql_user, mysql_password
import socket

from lib.prometheus_metric_util import generate_registry, generate_gauge
from lib.sys_metric_util import get_fd_cnt_by_ps, get_fd_cnt_by_lsof

disk_metric_keys = ["disk_total", "disk_used", "disk_used_percent"]
mem_metric_keys = ["mem_total", "mem_used", "mem_used_percent"]


host_name: str = socket.gethostname()


def about():
    """about view"""
    return "metric_collector for vm\n", 200


def get_mysql(db_name: str, table_name: str):
    """get mysql metric"""
    from service.mysql import get_information_schema
    metrics = get_information_schema(rg_name=resource_name,
                                     host=mysql_host,
                                     user=mysql_user,
                                     password=mysql_password,
                                     table_name=table_name,
                                     db=db_name)
    if len(metrics) == 0:
        return "empty data", 404
    return "\n".join(metrics), 200


def get_machine_cpu():
    """get machine cpu metric"""
    import psutil
    cpu = psutil.cpu_percent(interval=1, percpu=True)
    print(f'{cpu}')


def get_redis():
    """get redis metric"""
    from service.redis import get_redis_metric
    ret_val = get_redis_metric(resource_name=resource_name,
                               host_name=host_name)
    if len(ret_val) > 0:
        return "\n".join(ret_val), 200
    return "empty data", 500


def get_mongodb():
    """get mongodb metric"""
    from service.mongodb import get_mongo_metrics
    ret_val = get_mongo_metrics(resource_name=resource_name,
                                service_name=service_name,
                                host_name=host_name)
    if len(ret_val) > 0:
        return "\n".join(ret_val), 200
    return "empty data", 500


def get_mongodb_isalive():
    """get mongodb is alive"""
    from service.mongodb import get_mongo_is_alive
    metric = get_mongo_is_alive()
    return metric.decode('utf-8'), 200


def view_rabbitmq_queue_item_cnt(queue_name="", vhost_name="/"):
    """ view_rabbitmq_queue_item_cnt """
    from service.rabbitmqcl import get_rabbitmq_queue_item_cnt
    return get_rabbitmq_queue_item_cnt(queue_name=queue_name, vhost_name=vhost_name)


def view_rabbitmq_queue_item_cnt_root(queue_name=""):
    """ view_rabbitmq_queue_item_cnt_root """
    from service.rabbitmqcl import get_rabbitmq_queue_item_cnt
    return get_rabbitmq_queue_item_cnt(queue_name=queue_name, vhost_name='/')


def view_es_yesterday_index_length(name="", is_stream_idx="1"):
    """ view_es_yesterday_index_length """
    from service.es import view_es_index_length
    return view_es_index_length(name=name, is_stream_idx=is_stream_idx, is_yesterday=True)


def view_es_current_index_length(name="", is_stream_idx="1"):
    """ view_es_current_index_length """
    from service.es import view_es_index_length
    return view_es_index_length(name=name, is_stream_idx=is_stream_idx, is_yesterday=False)


def view_es_index_length(name, is_stream_idx=1):
    """ view_es_index_length """
    from service.es import get_index_size_matrix
    metric = get_index_size_matrix(index_name=name, is_stream_idx=True if is_stream_idx else False)
    return metric.decode('utf-8'), 200


def view_os_version():
    """ view_os_version """
    from service.os_util import get_os_version
    metric = get_os_version()
    return metric.decode('utf-8'), 200


def view_docker_ps_cnt():
    """docker ps cnt view"""
    import subprocess
    cmd = "/usr/bin/ps -adef|/usr/bin/grep 'docker run'|/usr/bin/grep -Ewv 'ps|grep'|/usr/bin/wc -l"
    key = "azure_vm_docker_count"
    label = {"instance": "",
             "metric": "docker_count",
             "resource": resource_name,
             "service": service_name}
    metric_num = subprocess.check_output(cmd,
                                         shell=True,
                                         text=True)
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label,
                   value=metric_num,
                   registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_containerd_cnt():
    """container cnt view"""
    import subprocess
    cmd = "/usr/bin/ps -adef|/usr/bin/grep "\
          "'containerd-shim-runc-v2'|/usr/bin/grep -v "\
          "'grep'|/usr/bin/wc -l"
    key = "azure_vm_containerd_count"
    label = {"instance": "",
             "metric": "containerd_count",
             "resource": resource_name,
             "service": service_name}
    metric_num = subprocess.check_output(cmd, shell=True, text=True)
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label,
                   value=metric_num, registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_docker_ps_abnormal_cnt():
    """docker ps abnormal cnt view"""
    import subprocess
    cmd = "/usr/bin/docker ps --filter=status=exited --filter=status=created |/usr/bin/wc -l"
    key = "azure_vm_docker_abnormal_count"
    label = {"instance": "",
             "metric": "docker_abnormal_count",
             "resource": resource_name,
             "service": service_name}
    metric_num = subprocess.check_output(cmd,
                                         shell=True,
                                         text=True)
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label,
                   value=metric_num, registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_process_cnt():
    """process cnt view"""
    import subprocess
    cmd = "/usr/bin/ps -adef|/usr/bin/grep -Ewv 'ps |grep' |/usr/bin/wc -l"
    key = "azure_vm_process_count"
    label = {"instance": "",
             "metric": "process_count",
             "resource": resource_name,
             "service": service_name}
    metric_num = subprocess.check_output(cmd, shell=True, text=True)
    registry = CollectorRegistry()
    generate_gauge(key=key,
                   label=label,
                   value=metric_num,
                   registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_fd_internal(cmd_type: int):
    """internal of fd view"""
    key = "azure_vm_opened_fd_count"
    label = {"instance": "",
             "metric": "opened_fd_count",
             "resource": resource_name,
             "service": service_name,
             "cmd_type": cmd_type}
    if cmd_type == 1:
        metric_num = get_fd_cnt_by_lsof()
    else:
        metric_num = get_fd_cnt_by_ps()
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label,
                   value=metric_num,
                   registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_fd(cmd_type: int):
    """fd cnt view"""
    try:
        return view_fd_internal(cmd_type)
    except Exception as e:
        return str(e), 500


def view_fd_default():
    """fd default view"""
    try:
        return view_fd_internal(2)
    except Exception as e:
        return str(e), 500


def view_cpu():
    """cpu view"""
    import psutil
    key = "azure_vm_cpu_percent"
    label = {"instance": "",
             "metric": "cpu_percent",
             "resource": resource_name,
             "service": service_name}
    # datas = {"azure_vm_cpu_percent": psutil.cpu_percent()}
    registry = CollectorRegistry()
    generate_gauge(key=key,
                   label=label,
                   value=psutil.cpu_percent(),
                   registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_disk():
    """disk view page"""
    import psutil
    keys = {}
    for metric_key in disk_metric_keys:
        keys["azure_vm_" + metric_key] = {
            "instance": "",
            "device": "",
            "metric": metric_key,
            "resource": resource_name,
            "service": service_name
        }

    metrics = []
    for disk in psutil.disk_partitions():
        if disk.fstype and 'loop' not in disk.device:
            registry = CollectorRegistry()
            disk_usage = psutil.disk_usage(disk.mountpoint)
            total = round(int(disk_usage.total) / (1024.0 ** 3), 4)
            used = round(int(disk_usage.used) / (1024.0 ** 3), 4)
            used_percent = (used / total) * 100
            datas = {"azure_vm_disk_total": total,
                     "azure_vm_disk_used": used,
                     "azure_vm_disk_used_percent": used_percent}
            for key in keys.keys():
                label = keys[key]
                label["instance"] = host_name
                label["device"] = disk.device
                metric_num = datas[key]
                gauge = Gauge(key, key,
                              label.keys(),
                              registry=registry)
                label_values = label.values()
                gauge.labels(*label_values).set(metric_num)
            metric = generate_latest(registry=registry)
            metrics.append(metric.decode('utf-8'))
    metric_str = "\n".join(metrics)
    return metric_str, 200


def view_memory():
    """memory view"""
    import psutil
    keys = {}
    for key in mem_metric_keys:
        keys["azure_vm_" + key] = {
            "instance": "",
            "metric": key,
            "resource": resource_name,
            "service": service_name}
    mem = psutil.virtual_memory()
    metrics = []
    total = mem.total
    used = mem.used
    used_percent = (used / total) * 100
    datas = {"azure_vm_mem_total": total,
             "azure_vm_mem_used": used,
             "azure_vm_mem_used_percent": used_percent}
    registry = generate_registry(datas=datas,
                                 keys=keys,
                                 host_name=host_name)
    metric = generate_latest(registry=registry)
    metrics.append(metric.decode('utf-8'))
    metric_str = "\n".join(metrics)
    return metric_str, 200


def view_file_size(file_name_path: str):
    """file size view"""
    file_name_path = file_name_path.replace("__", "/")
    file_size = os.path.getsize(file_name_path)
    key = "file_size"
    label = {"instance": "",
             "metric": "cpu_percent",
             "resource": resource_name,
             "service": service_name,
             "filename": file_name_path}
    registry = CollectorRegistry()
    generate_gauge(key=key,
                   label=label,
                   value=int(file_size),
                   registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def get_ssl_valid_days(cert_file_path: str):
    """view for ssl valid days"""
    import ssl
    from dateutil.parser import parse
    import datetime
    label = {"instance": "",
             "metric": "ssl_validate",
             "resource": resource_name,
             "service": service_name}
    key = "ssl_validate"
    try:
        cert_dict = ssl._ssl._test_decode_cert(cert_file_path)
        cert_after = parse(cert_dict['notAfter'])
        now = datetime.datetime.now()
        leaved = (cert_after.date() - now.date()).days
    except Exception as e:
        print(e)
        leaved = -1
    registry = CollectorRegistry()
    filepaths = cert_file_path.split('/')
    label['dns'] = filepaths[len(filepaths) - 2]
    generate_gauge(key=key,
                   label=label,
                   value=leaved,
                   registry=registry,
                   host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8')


def view_cert_validate_days():
    """cert validate days view"""
    from config import cert_file_path as cert_file_paths
    metrics = []
    for cert_file_path in cert_file_paths:
        metric = get_ssl_valid_days(cert_file_path)
        metrics.append(metric)
    return "\n".join(metrics), 200
