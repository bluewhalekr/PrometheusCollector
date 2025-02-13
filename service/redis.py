"""redis.py"""
from multiprocessing.managers import SyncManager

from prometheus_client import CollectorRegistry, Gauge, generate_latest

from lib.util import text_to_num

sync_manager: SyncManager = None


class SyncManager(SyncManager):
    """Wrapper class for SyncManager"""
    pass


syncdict = {}

redis_metric_keys = ["io_threads_active", "connected_clients",
                     "maxclients", "client_recent_max_input_buffer",
                     "client_recent_max_output_buffer",
                     "client_recent_max_output_buffer",
                     "blocked_clients", "tracking_clients",
                     "clients_in_timeout_table", "used_memory",
                     "used_memory_human", "used_memory_rss",
                     "used_memory_rss_human", "used_memory_peak",
                     "used_memory_peak_human", "used_memory_peak_perc",
                     "used_memory_overhead", "used_memory_dataset",
                     "used_memory_dataset_perc", "allocator_allocated",
                     "allocator_active", "allocator_resident",
                     "total_system_memory", "total_system_memory_human",
                     "used_memory_lua", "maxmemory_human",
                     "active_defrag_running", "lazyfree_pending_objects",
                     "current_fork_perc", "loading",
                     "current_save_keys_processed", "current_save_keys_total",
                     "total_connections_received", "total_commands_processed",
                     "total_net_input_bytes", "total_net_output_bytes",
                     "instantaneous_input_kbps", "instantaneous_output_kbps",
                     "expired_keys", "keyspace_hits",
                     "keyspace_misses", "latest_fork_usec",
                     "total_forks", "total_reads_processed",
                     "total_writes_processed", "reply_buffer_shrinks",
                     "role", "repl_backlog_size",
                     "used_cpu_sys", "used_cpu_user",
                     "used_cpu_sys_children", "used_cpu_user_children"]


def get_dict():
    """get_dict"""
    return syncdict


def init_shm_lock():
    """init sharedmemory lock"""
    global sync_manager
    from lib.syncmanager import init_redis_cron_lock_4_server
    sync_manager = init_redis_cron_lock_4_server(name="syncdict", get_dict=get_dict)


def fint_shm_lock():
    """finalize sharedmemory lock"""
    from lib.syncmanager import fint_redis_cron_lock
    fint_redis_cron_lock()


def get_redis_metric(resource_name: str, host_name: str) -> list:
    """get redis metric from shared memory"""
    metrics = []
    ayncdict_local = sync_manager.syncdict()
    for key in ayncdict_local.keys():
        metric = ayncdict_local.get(key)
        host, port, name = key.split(":")
        redis_addr = f"{host}:{port}"
        registry = CollectorRegistry()
        key_vals = {}
        for metric_key in redis_metric_keys:
            key_vals["redis_" + metric_key] =\
                [{"instance": "", "metric": metric_key,
                  "resource": resource_name, "service": redis_addr, "name": name},
                 metric[metric_key]]
        for metric_key in key_vals.keys():
            label = key_vals[metric_key][0]
            label["instance"] = host_name
            metric_num = key_vals[metric_key][1]
            gauge = Gauge(metric_key, metric_key, label.keys(), registry=registry)
            label_values = label.values()
            if metric_num is not None and type(metric_num) == str and metric_num.isdigit():
                metric_real_num = text_to_num(metric_num)
            else:
                metric_real_num = 0.0
            gauge.labels(*label_values).set(metric_real_num)
            metric = generate_latest(registry=registry)
            metrics.append(metric.decode('utf-8'))
    return metrics
