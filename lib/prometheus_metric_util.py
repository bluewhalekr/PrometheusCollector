from prometheus_client import CollectorRegistry, Gauge


def generate_gauge(key: str, label: dict, value: any, registry: CollectorRegistry, host_name: str = "localhost") -> Gauge:
    if "instance" in label:
        label["instance"] = host_name
    gauge = Gauge(key, key, label.keys(), registry=registry)
    print(f'value = {value}')
    gauge.labels(*label.values()).set(value=value[''])
    return gauge


def generate_registry(datas, keys, host_name) -> CollectorRegistry:
    registry = CollectorRegistry()
    
    for key in keys.keys():
        generate_gauge(key=key, label=keys[key], value=datas[key], registry=registry, host_name=host_name)
    return registry
