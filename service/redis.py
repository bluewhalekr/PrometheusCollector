from multiprocessing.managers import SyncManager

from prometheus_client import CollectorRegistry, Gauge, generate_latest

from lib.util import text_to_num

sync_manager: SyncManager = None


class SyncManager(SyncManager):
    pass


syncdict = {}


def get_dict():
    return syncdict


def init_redis_cron_lock():
    global sync_manager
    from lib.syncmanager import init_redis_cron_lock_4_server
    sync_manager = init_redis_cron_lock_4_server(name="syncdict", get_dict=get_dict)


def fint_redis_cron_lock():
    from lib.syncmanager import fint_redis_cron_lock
    fint_redis_cron_lock()


def get_redis_metric(resource_name: str, host_name: str) -> list:
    metrics = []
    ayncdict_local = sync_manager.syncdict()

    for key in ayncdict_local.keys():
        metric = ayncdict_local.get(key)
        registry = CollectorRegistry()
        key_vals = {
            "redis_io_threads_active":
                [{"instance": "", "metric": "io_threads_active", "resource": resource_name, "service": key}, metric['io_threads_active']],
            "redis_connected_clients": [
                {"instance": "", "metric": "connected_clients", "resource": resource_name, "service": key}, metric['connected_clients']],
            "redis_maxclients": [
                {"instance": "", "metric": "maxclients", "resource": resource_name, "service": key}, metric['maxclients']],
            "redis_client_recent_max_input_buffer": [
                {"instance": "", "metric": "client_recent_max_input_buffer", "resource": resource_name, "service": key}, metric['client_recent_max_input_buffer']],
            "redis_client_recent_max_output_buffer": [
                {"instance": "", "metric": "client_recent_max_output_buffer", "resource": resource_name, "service": key}, metric['client_recent_max_output_buffer']],
            "redis_blocked_clients": [
                {"instance": "", "metric": "blocked_clients", "resource": resource_name, "service": key}, metric['blocked_clients']],
            "redis_tracking_clients": [
                {"instance": "", "metric": "tracking_clients", "resource": resource_name, "service": key}, metric['tracking_clients']],
            "redis_clients_in_timeout_table": [
                {"instance": "", "metric": "clients_in_timeout_table", "resource": resource_name, "service": key}, metric['clients_in_timeout_table']],
            "redis_used_memory": [
                {"instance": "", "metric": "used_memory", "resource": resource_name, "service": key}, metric['used_memory']],
            "redis_used_memory_human": [
                {"instance": "", "metric": "used_memory_human", "resource": resource_name, "service": key}, metric['used_memory_human']],
            "redis_used_memory_rss": [
                {"instance": "", "metric": "used_memory_rss", "resource": resource_name, "service": key}, metric['used_memory_rss']],
            "redis_used_memory_rss_human": [
                {"instance": "", "metric": "used_memory_rss_human", "resource": resource_name, "service": key}, metric['used_memory_rss_human']],
            "redis_used_memory_peak": [
                {"instance": "", "metric": "used_memory_peak", "resource": resource_name, "service": key}, metric['used_memory_peak']],
            "redis_used_memory_peak_human": [
                {"instance": "", "metric": "used_memory_peak_human", "resource": resource_name, "service": key}, metric['used_memory_peak_human']],
            "redis_used_memory_peak_perc": [
                {"instance": "", "metric": "used_memory_peak_perc", "resource": resource_name, "service": key}, metric['used_memory_peak_perc']],
            "redis_used_memory_overhead": [
                {"instance": "", "metric": "used_memory_overhead", "resource": resource_name, "service": key}, metric['used_memory_overhead']],
            "redis_used_memory_dataset": [
                {"instance": "", "metric": "used_memory_dataset", "resource": resource_name, "service": key}, metric['used_memory_dataset']],
            "redis_used_memory_dataset_perc": [
                {"instance": "", "metric": "used_memory_dataset_perc", "resource": resource_name, "service": key}, metric['used_memory_dataset_perc']],
            "redis_allocator_allocated": [
                {"instance": "", "metric": "allocator_allocated", "resource": resource_name, "service": key}, metric['allocator_allocated']],
            "redis_allocator_active": [{"instance": "", "metric": "allocator_active", "resource": resource_name, "service": key}, metric['allocator_active']],
            "redis_allocator_resident": [{"instance": "", "metric": "allocator_resident", "resource": resource_name, "service": key},
                                         metric['allocator_resident']],
            "redis_total_system_memory": [
                {"instance": "", "metric": "total_system_memory", "resource": resource_name, "service": key}, metric['total_system_memory']],
            "redis_total_system_memory_human": [
                {"instance": "", "metric": "total_system_memory_human", "resource": resource_name, "service": key}, metric['total_system_memory_human']],
            "redis_used_memory_lua": [
                {"instance": "", "metric": "used_memory_lua", "resource": resource_name, "service": key}, metric['used_memory_lua']],
            "redis_maxmemory": [
                {"instance": "", "metric": "maxmemory", "resource": resource_name, "service": key}, metric['maxmemory']],
            "redis_maxmemory_human": [
                {"instance": "", "metric": "maxmemory_human", "resource": resource_name, "service": key}, metric['maxmemory_human']],
            "redis_active_defrag_running": [
                {"instance": "", "metric": "active_defrag_running", "resource": resource_name, "service": key}, metric['active_defrag_running']],
            "redis_lazyfree_pending_objects": [
                {"instance": "", "metric": "lazyfree_pending_objects", "resource": resource_name, "service": key}, metric['lazyfree_pending_objects']],
            "redis_loading": [
                {"instance": "", "metric": "loading", "resource": resource_name, "service": key}, metric['loading']],
            "redis_current_fork_perc": [
                {"instance": "", "metric": "current_fork_perc", "resource": resource_name, "service": key}, metric['current_fork_perc']],
            "redis_current_save_keys_processed":
                [{"instance": "", "metric": "current_save_keys_processed", "resource": resource_name, "service": key}, metric['current_save_keys_processed']],
            "redis_current_save_keys_total":
                [{"instance": "", "metric": "current_save_keys_total", "resource": resource_name, "service": key}, metric['current_save_keys_total']],
            "redis_total_connections_received":
                [{"instance": "", "metric": "total_connections_received", "resource": resource_name, "service": key}, metric['total_connections_received']],
            "redis_total_commands_processed":
                [{"instance": "", "metric": "total_commands_processed", "resource": resource_name, "service": key}, metric['total_commands_processed']],
            "redis_total_net_input_bytes":
                [{"instance": "", "metric": "total_net_input_bytes", "resource": resource_name, "service": key}, metric['total_net_input_bytes']],
            "redis_total_net_output_bytes":
                [{"instance": "", "metric": "total_net_output_bytes", "resource": resource_name, "service": key}, metric['total_net_output_bytes']],
            "redis_instantaneous_input_kbps":
                [{"instance": "", "metric": "instantaneous_input_kbps", "resource": resource_name, "service": key}, metric['instantaneous_input_kbps']],
            "redis_instantaneous_output_kbps":
                [{"instance": "", "metric": "instantaneous_output_kbps", "resource": resource_name, "service": key}, metric['instantaneous_output_kbps']],
            "redis_expired_keys":
                [{"instance": "", "metric": "expired_keys", "resource": resource_name, "service": key}, metric['expired_keys']],
            "redis_keyspace_hits":
                [{"instance": "", "metric": "keyspace_hits", "resource": resource_name, "service": key}, metric['keyspace_hits']],
            "redis_keyspace_misses":
                [{"instance": "", "metric": "keyspace_misses", "resource": resource_name, "service": key}, metric['keyspace_misses']],
            "redis_latest_fork_usec":
                [{"instance": "", "metric": "latest_fork_usec", "resource": resource_name, "service": key}, metric['latest_fork_usec']],
            "redis_total_forks":
                [{"instance": "", "metric": "total_forks", "resource": resource_name, "service": key}, metric['total_forks']],
            "redis_total_reads_processed":
                [{"instance": "", "metric": "total_reads_processed", "resource": resource_name, "service": key}, metric['total_reads_processed']],
            "redis_total_writes_processed":
                [{"instance": "", "metric": "total_writes_processed", "resource": resource_name, "service": key}, metric['total_writes_processed']],
            "redis_reply_buffer_shrinks":
                [{"instance": "", "metric": "reply_buffer_shrinks", "resource": resource_name, "service": key}, metric['reply_buffer_shrinks']],
            "redis_role":
                [{"instance": "", "metric": "role", "resource": resource_name, "service": key}, metric['role'] == 'master'],
            "redis_repl_backlog_size":
                [{"instance": "", "metric": "repl_backlog_size", "resource": resource_name, "service": key}, metric['repl_backlog_size']],
            "redis_used_cpu_sys":
                [{"instance": "", "metric": "used_cpu_sys", "resource": resource_name, "service": key}, metric['used_cpu_sys']],
            "redis_used_cpu_user":
                [{"instance": "", "metric": "used_cpu_user", "resource": resource_name, "service": key}, metric['used_cpu_user']],
            "redis_used_cpu_sys_children":
                [{"instance": "", "metric": "used_cpu_sys_children", "resource": resource_name, "service": key}, metric['used_cpu_sys_children']],
            "redis_used_cpu_user_children":
                [{"instance": "", "metric": "used_cpu_user_children", "resource": resource_name, "service": key}, metric['used_cpu_user_children']],
            "redis_used_cpu_sys_children":
                [{"instance": "", "metric": "used_cpu_sys_children", "resource": resource_name, "service": key}, metric['used_cpu_sys_children']],
        }
        for metric_key in key_vals.keys():
            label = key_vals[metric_key][0]
            label["instance"] = host_name
            metric_num = key_vals[metric_key][1]
            gauge = Gauge(metric_key, metric_key, label.keys(), registry=registry)
            label_values = label.values()
            
            if type(metric_num) == str:
                metric_num = text_to_num(metric_num)

            gauge.labels(*label_values).set(metric_num)
            metric = generate_latest(registry=registry)
            metrics.append(metric.decode('utf-8'))
    
    return metrics
