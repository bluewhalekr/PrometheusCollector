from prometheus_client import Gauge, CollectorRegistry, generate_latest
from lib.prometheus_metric_util import generate_gauge
import socket
from elasticsearch import Elasticsearch
from config import els_address
from config import els_index_prefix
from config import resource_name, service_name
from datetime import datetime, timedelta

def get_index_size(els_addr="", index_name="", is_stream_idx=True, is_yesterday=False):
    """
    Elasticsearch 인덱스의 크기를 바이트 단위로 반환합니다.
    Args:
    Returns:
        int: 인덱스의 크기 (바이트 단위), 오류 발생 시 None을 반환합니다.
    """
    try:
        if len(els_addr) == 0:
            els_addr = els_address
        if len(index_name) == 0:
            index_name = els_index_prefix
        with Elasticsearch(els_addr) as es:
            if is_yesterday:
                day = (datetime.now() - timedelta(1)).strftime('-%Y.%m.%d') if is_stream_idx else ""
            else:
                day = datetime.now().strftime('-%Y.%m.%d') if is_stream_idx else ""
            index_name = f"{index_name}{day}"
            response = es.indices.stats(index=index_name, metric="store")
            size_in_bytes = response['indices'][index_name]['total']['store']['size_in_bytes']
            return size_in_bytes
    except Exception as e:
        print(f"get_index_size : Error getting index size: {e}")
        return -1


def view_es_index_length(name="", is_stream_idx="1", is_yesterday=False):
    """ view_es_index_length_common """
    host_name = socket.gethostname()

    print(f'name={name}, is_stream_idx={is_stream_idx}, is_yesterday={is_yesterday}')

    key = "es_yesterday_index_size" if is_yesterday else "es_current_index_size"

    is_stream_idx_lo=True if is_stream_idx=="1" else False
    print(f'name={name}, is_stream_idx={is_stream_idx_lo}, is_yesterday={is_yesterday}')
    metric_num = get_index_size(els_addr=els_address,
                                index_name=name,
                                is_stream_idx=is_stream_idx_lo,
                                is_yesterday=is_yesterday)
    label = {"instance": host_name,
             "metric": key,
             "resource": resource_name,
             "service": service_name,
             "index_name": name}
    registry = CollectorRegistry()
    gauge = Gauge(key, key, label.keys(), registry=registry)
    label_values = label.values()
    gauge.labels(*label_values).set(metric_num)
    metric = generate_latest(registry=registry)
    return metric.decode('utf-8'), 200


def get_index_size_matrix(index_name, is_stream_idx):
    """ get_index_size_matrix """
    key = "index_size"
    host_name = socket.gethostname()

    idx_size = get_index_size(els_addr=els_address, index_name=index_name, is_stream_idx=is_stream_idx)

    label = {"instance": host_name,
             "metric": key,
             "resource": resource_name,
             "service": service_name,
             "index_name": index_name}
    registry = CollectorRegistry()
    generate_gauge(key=key, label=label, value=idx_size, registry=registry, host_name=host_name)
    return generate_latest(registry=registry)


if __name__=="__main__":
    index_name_pref = "backend-api-"
    index_size = get_index_size(els_addr="http://localhost:9200", index_name_pref=index_name_pref)
    if index_size is not None:
        print(f"인덱스 '{index_name_pref}'의 크기: {index_size} 바이트")
