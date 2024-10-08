from prometheus_client import Gauge, CollectorRegistry, generate_latest
import os
from config import resource_name, service_name
from config import mysql_host, mysql_user, mysql_password
import socket

from lib.prometheus_metric_util import generate_registry, generate_gauge
from lib.sys_metric_util import get_fd_cnt_by_ps, get_fd_cnt_by_lsof

host_name: str = socket.gethostname()


def about():
    return "metric_collector for vm\n", 200


def get_mysql(db_name: str, table_name: str):
    from service.mysql import get_information_schema
    metrics = get_information_schema(rg_name=resource_name,
                                     host=mysql_host,
                                     user=mysql_user,
                                     password=mysql_password,
                                     table_name=table_name,
                                     db=db_name)
    
    if len(metrics) != 1:
        return "empty data", 404
    
    return "\n".join(metrics), 200


def get_machine_cpu():
    import psutil
    cpu = psutil.cpu_percent(interval=1, percpu=True)
    print(f'{cpu}')


def get_redis():
    from service.redis import get_redis_metric
    
    ret_val = get_redis_metric(resource_name=resource_name, host_name=host_name)
    
    if len(ret_val) > 0:
        return "\n".join(ret_val), 200
    return "empty data", 500


def get_mongodb():
    from service.mongodb import get_mongo_metrics
    ret_val = get_mongo_metrics(resource_name=resource_name, service_name=service_name, host_name=host_name)
    
    if len(ret_val) > 0:
        return "\n".join(ret_val), 200
    
    return "empty data", 500


def get_mongodb_isalive():
    from service.mongodb import get_mongo_is_alive
    metric = get_mongo_is_alive()
    return metric.decode('utf-8'), 200


def view_docker_ps_cnt():
    import subprocess
    cmd = "/usr/bin/ps -adef|/usr/bin/grep 'docker run'|/usr/bin/grep -Ewv 'ps|grep'|/usr/bin/wc -l"
    key = "azure_vm_docker_count"
    label = {"instance": "", "metric": "docker_count", "resource": resource_name, "service": service_name}
    
    metric_num = subprocess.check_output(cmd, shell=True, text=True)
    registry = CollectorRegistry()
    
    generate_gauge(key=key, label=label, value=metric_num, registry=registry, host_name=host_name)
    metric = generate_latest(registry=registry)
    
    return metric.decode('utf-8'), 200


def view_containerd_cnt():
    import subprocess
    cmd = "/usr/bin/ps -adef|/usr/bin/grep 'containerd-shim-runc-v2'|/usr/bin/grep -v 'grep'|/usr/bin/wc -l"
    key = "azure_vm_containerd_count"
    label = {"instance": "", "metric": "containerd_count", "resource": resource_name, "service": service_name}
    
    metric_num = subprocess.check_output(cmd, shell=True, text=True)
    registry = CollectorRegistry()
    
    generate_gauge(key=key, label=label, value=metric_num, registry=registry, host_name=host_name)
    
    metric = generate_latest(registry=registry)
    
    return metric.decode('utf-8'), 200


def view_docker_ps_abnormal_cnt():
    import subprocess
    cmd = "/usr/bin/docker ps --filter=status=exited --filter=status=created |/usr/bin/wc -l"
    key = "azure_vm_docker_abnormal_count"
    label = {"instance": "", "metric": "docker_abnormal_count", "resource": resource_name, "service": service_name}
    
    metric_num = subprocess.check_output(cmd, shell=True, text=True)
    registry = CollectorRegistry()
    
    generate_gauge(key=key, label=label, value=metric_num, registry=registry, host_name=host_name)
    metric = generate_latest(registry=registry)
    
    return metric.decode('utf-8'), 200


def view_process_cnt():
    import subprocess
    cmd = "/usr/bin/ps -adef|/usr/bin/grep -Ewv 'ps |grep' |/usr/bin/wc -l"
    key = "azure_vm_process_count"
    label = {"instance": "", "metric": "process_count", "resource": resource_name, "service": service_name}
    metric_num = subprocess.check_output(cmd, shell=True, text=True)
    registry = CollectorRegistry()
    
    generate_gauge(key=key, label=label, value=metric_num, registry=registry, host_name=host_name)
    metric = generate_latest(registry=registry)
    
    return metric.decode('utf-8'), 200


def view_fd_internal(cmd_type: int):
    key = "azure_vm_opened_fd_count"
    label = {"instance": "", "metric": "opened_fd_count", "resource": resource_name, "service": service_name, "cmd_type": cmd_type}
    
    if cmd_type == 1:
        metric_num = get_fd_cnt_by_lsof()
    else:
        metric_num = get_fd_cnt_by_ps()
    
    registry = CollectorRegistry()
    
    generate_gauge(key=key, label=label, value=metric_num, registry=registry, host_name=host_name)
    metric = generate_latest(registry=registry)
    
    return metric.decode('utf-8'), 200


def view_fd(cmd_type: int):
    try:
        return view_fd_internal(cmd_type)
    except Exception as e:
        return str(e), 500


def view_fd_default():
    try:
        return view_fd_internal(2)
    except Exception as e:
        return str(e), 500


def view_cpu():
    import psutil
    key = "azure_vm_cpu_percent"
    label = {"instance": "", "metric": "cpu_percent", "resource": resource_name, "service": service_name}
    # datas = {"azure_vm_cpu_percent": psutil.cpu_percent()}
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label, value=psutil.cpu_percent(), registry=registry, host_name=host_name)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_disk():
    import psutil
    
    keys = {"azure_vm_disk_total": {"instance": "", "device": "", "metric": "disk_total", "resource": resource_name, "service": service_name},
            "azure_vm_disk_used": {"instance": "", "device": "", "metric": "disk_used", "resource": resource_name, "service": service_name},
            "azure_vm_disk_used_percent": {"instance": "", "device": "", "metric": "disk_used_percent", "resource": resource_name, "service": service_name}}
    
    metrics = []
    
    for disk in psutil.disk_partitions():
        if disk.fstype and 'loop' not in disk.device:
            registry = CollectorRegistry()
            total = round(int(psutil.disk_usage(disk.mountpoint).total) / (1024.0 ** 3), 4)
            used = round(int(psutil.disk_usage(disk.mountpoint).used) / (1024.0 ** 3), 4)
            used_percent = (used / total) * 100
            
            datas = {"azure_vm_disk_total": total,
                     "azure_vm_disk_used": used,
                     "azure_vm_disk_used_percent": used_percent}
            for key in keys.keys():
                label = keys[key]
                label["instance"] = host_name
                label["device"] = disk.device
                metric_num = datas[key]
                gauge = Gauge(key, key, label.keys(), registry=registry)
                label_values = label.values()
                gauge.labels(*label_values).set(metric_num)
            metric = generate_latest(registry=registry)
            metrics.append(metric.decode('utf-8'))
    
    metric_str = "\n".join(metrics)
    return metric_str, 200


def view_memory():
    import psutil
    
    keys = {"azure_vm_mem_total": {"instance": "", "metric": "mem_total", "resource": resource_name, "service": service_name},
            "azure_vm_mem_used": {"instance": "", "metric": "mem_used", "resource": resource_name, "service": service_name},
            "azure_vm_mem_used_percent": {"instance": "", "metric": "mem_used_percent", "resource": resource_name, "service": service_name}}
    
    mem = psutil.virtual_memory()
    # total=950054912, available=117116928, percent=87.7, used=675012608, free=68538368
    # print(f'{mem.total}, {mem.available}, {mem.free}, {mem.used}')
    
    metrics = []
    
    total = mem.total
    used = mem.used
    used_percent = (used / total) * 100
    
    datas = {"azure_vm_mem_total": total,
             "azure_vm_mem_used": used,
             "azure_vm_mem_used_percent": used_percent}
    
    registry = generate_registry(datas=datas, keys=keys, host_name=host_name)
    
    metric = generate_latest(registry=registry)
    metrics.append(metric.decode('utf-8'))
    
    metric_str = "\n".join(metrics)
    return metric_str, 200


def view_file_size(file_name_path: str):
    file_name_path = file_name_path.replace("__", "/")
    file_size = os.path.getsize(file_name_path)
    key = "file_size"
    label = {"instance": "", "metric": "cpu_percent", "resource": resource_name, "service": service_name, "filename": file_name_path}
    
    registry = CollectorRegistry()
    
    generate_gauge(key=key, label=label, value=int(file_size), registry=registry, host_name=host_name)
    
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def view_cert():
    from config import cert_file_path
    import ssl
    from dateutil.parser import parse
    import datetime
    
    label = {"instance": "", "metric": "ssl_validate", "resource": resource_name, "service": service_name}
    key = "ssl_validate"

    try:
        cert_dict = ssl._ssl._test_decode_cert(cert_file_path)
        cert_after = parse(cert_dict['notAfter'])
        now = datetime.datetime.now()
        state_code = 200
        leaved = (cert_after - now).days
    except Exception as e:
        print(e)
        leaved = -1
        state_code = 500

    registry = CollectorRegistry()

    generate_gauge(key=key, label=label, value=leaved, registry=registry, host_name=host_name)
    
    metric = generate_latest(registry=registry)
    
    return metric.decode('utf-8'), state_code
