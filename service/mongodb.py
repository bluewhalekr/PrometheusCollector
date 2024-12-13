from pymongo import MongoClient
from config import mongodb_uri
from prometheus_client import Gauge, CollectorRegistry, generate_latest
from lib.prometheus_metric_util import generate_gauge


def get_mongo_metrics(resource_name, service_name, host_name):
    client = MongoClient(mongodb_uri)
    
    status = client.get_database('admin').command('serverStatus')
    
    mem_st = status['mem']
    connection_st = status['connections']
    extra_info_st = status['extra_info']
    network_st = status['network']
    opcounters_st = status['opcounters']
    oplatencies_st = status['opLatencies']
    
    key_vals = {
        "mongodb_mem_bits":
            [{"instance": "", "metric": "bits", "resource": resource_name, "service": service_name}, mem_st['bits']],
        "mongodb_mem_resident":
            [{"instance": "", "metric": "resident", "resource": resource_name, "service": service_name}, mem_st['resident']],
        "mongodb_mem_virtual": [
            {"instance": "", "metric": "virtual", "resource": resource_name, "service": service_name}, mem_st['virtual']],
        "mongodb_mem_supported": [
            {"instance": "", "metric": "supported", "resource": resource_name, "service": service_name}, mem_st['supported']],
        "mongodb_connections_current": [
            {"instance": "", "metric": "current", "resource": resource_name, "service": service_name}, connection_st['current']],
        "mongodb_connections_available": [
            {"instance": "", "metric": "available", "resource": resource_name, "service": service_name}, connection_st['available']],
        "mongodb_connections_totalCreated": [
            {"instance": "", "metric": "totalCreated", "resource": resource_name, "service": service_name}, connection_st['totalCreated']],
        # "mongodb_connections_rejected": [
        #     {"instance": "", "metric": "rejected", "resource": resource_name, "service": service_name}, connection_st['rejected']],
        "mongodb_connections_active": [
            {"instance": "", "metric": "active", "resource": resource_name, "service": service_name}, connection_st['active']],
        "mongodb_connections_threaded": [
            {"instance": "", "metric": "threaded", "resource": resource_name, "service": service_name}, connection_st['threaded']],
        "mongodb_network_bytesIn": [
            {"instance": "", "metric": "bytesIn", "resource": resource_name, "service": service_name}, network_st['bytesIn']],
        "mongodb_network_bytesOut": [
            {"instance": "", "metric": "bytesOut", "resource": resource_name, "service": service_name}, network_st['bytesOut']],
        "mongodb_network_physicalBytesIn": [
            {"instance": "", "metric": "physicalBytesIn", "resource": resource_name, "service": service_name}, network_st['physicalBytesIn']],
        "mongodb_network_physicalBytesOut": [
            {"instance": "", "metric": "physicalBytesOut", "resource": resource_name, "service": service_name}, network_st['physicalBytesOut']],
        "mongodb_network_numSlowDNSOperations": [
            {"instance": "", "metric": "numSlowDNSOperations", "resource": resource_name, "service": service_name}, network_st['numSlowDNSOperations']],
        "mongodb_network_numRequests": [
            {"instance": "", "metric": "numRequests", "resource": resource_name, "service": service_name}, network_st['numRequests']],
        "mongodb_opcounters_insert": [
            {"instance": "", "metric": "insert", "resource": resource_name, "service": service_name}, opcounters_st['insert']],
        "mongodb_opcounters_query": [
            {"instance": "", "metric": "query", "resource": resource_name, "service": service_name}, opcounters_st['query']],
        "mongodb_opcounters_update": [
            {"instance": "", "metric": "update", "resource": resource_name, "service": service_name}, opcounters_st['update']],
        "mongodb_opcounters_delete": [
            {"instance": "", "metric": "delete", "resource": resource_name, "service": service_name}, opcounters_st['delete']],
        "mongodb_opcounters_getmore": [
            {"instance": "", "metric": "getmore", "resource": resource_name, "service": service_name}, opcounters_st['getmore']],
        "mongodb_opcounters_command":
            [{"instance": "", "metric": "command", "resource": resource_name, "service": service_name}, opcounters_st['command']],
        "mongodb_extra_info_user_time_us": [
            {"instance": "", "metric": "user_time_us", "resource": resource_name, "service": service_name}, extra_info_st['user_time_us']],
        "mongodb_extra_info_system_time_us": [
            {"instance": "", "metric": "system_time_us", "resource": resource_name, "service": service_name}, extra_info_st['system_time_us']],
        "mongodb_extra_info_maximum_resident_set_kb": [
            {"instance": "", "metric": "maximum_resident_set_kb", "resource": resource_name, "service": service_name},
            extra_info_st['maximum_resident_set_kb']],
        "mongodb_extra_info_input_blocks": [
            {"instance": "", "metric": "input_blocks", "resource": resource_name, "service": service_name}, extra_info_st['input_blocks']],
        "mongodb_extra_info_output_blocks": [
            {"instance": "", "metric": "output_blocks", "resource": resource_name, "service": service_name}, extra_info_st['output_blocks']],
        "mongodb_extra_info_page_reclaims": [
            {"instance": "", "metric": "page_reclaims", "resource": resource_name, "service": service_name}, extra_info_st['page_reclaims']],
        "mongodb_extra_info_page_faults": [
            {"instance": "", "metric": "page_faults", "resource": resource_name, "service": service_name}, extra_info_st['page_faults']],
        "mongodb_extra_info_voluntary_context_switches": [
            {"instance": "", "metric": "voluntary_context_switches", "resource": resource_name, "service": service_name},
            extra_info_st['voluntary_context_switches']],
        "mongodb_extra_info_involuntary_context_switches": [
            {"instance": "", "metric": "involuntary_context_switches", "resource": resource_name, "service": service_name},
            extra_info_st['involuntary_context_switches']],
        #"mongodb_extra_info_threads":
        #    [{"instance": "", "metric": "threads", "resource": resource_name, "service": service_name}, extra_info_st['threads']],
        "mongodb_oplatencies_reads_latency":
            [{"instance": "", "metric": "reads_latency", "resource": resource_name, "service": service_name}, oplatencies_st['reads']['latency']],
        "mongodb_oplatencies_reads_ops":
            [{"instance": "", "metric": "reads_latency", "resource": resource_name, "service": service_name}, oplatencies_st['reads']['ops']],
        "mongodb_oplatencies_writes_latency":
            [{"instance": "", "metric": "writes_latency", "resource": resource_name, "service": service_name}, oplatencies_st['writes']['latency']],
        "mongodb_oplatencies_writes_ops":
            [{"instance": "", "metric": "writes_latency", "resource": resource_name, "service": service_name}, oplatencies_st['writes']['ops']],
    }
    
    metrics = []
    registry = CollectorRegistry()
    
    for key in key_vals.keys():
        label = key_vals[key][0]
        label["instance"] = host_name
        metric_num = key_vals[key][1]
        gauge = Gauge(key, key, label.keys(), registry=registry)
        label_values = label.values()
        gauge.labels(*label_values).set(metric_num)
        metric = generate_latest(registry=registry)
        metrics.append(metric.decode('utf-8'))

    return metrics


def get_mongo_is_alive():
    from pymongo import MongoClient
    import pymongo
    import socket

    client = MongoClient(mongodb_uri, connectTimeoutMS=1000, timeoutMS=1000)
    is_alive = 1
    try:
        client.admin.command('ping')
    except pymongo.errors.ServerSelectionTimeoutError:
        print('time outed.')
        is_alive = 0
        
    from config import resource_name, service_name
    key = "mongodb_is_alive"
    host_name = socket.gethostname()
    label = {"instance": host_name, "metric": "is_alive", "resource": resource_name, "service": service_name}
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label, value=is_alive, registry=registry, host_name=host_name)
    return generate_latest(registry=registry)
