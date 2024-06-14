import pymysql
from prometheus_client import CollectorRegistry, Gauge, generate_latest

from lib.util import text_to_num


def get_information_schema(rg_name: str, host: str, user: str, password: str, table_name: str, db: str) -> []:
    metrics = []
    results = []
    
    sql = f'select * from information_schema.tables where table_name="{table_name}" and table_schema="{db}"'
    
    con = pymysql.connect(host = host, user=user, password=password, db=db)
    cursor = con.cursor()
    cursor.execute(sql)

    for cur in cursor:
        result = {"version": cur[5],
                  "table_rows": cur[7],
                  "avg_row_length": cur[8],
                  "data_length": cur[9],
                  "max_data_length": cur[10],
                  "index_length": cur[11],
                  "data_free": cur[12],
                  "auto_increment": cur[13]}
        results.append(result)

    for result in results:
        for key in result.keys():
            registry = CollectorRegistry()
            label = {"resource": rg_name, "db_addr": host, "db_name": db, "table_name": table_name, "metric": key}
            gauge = Gauge(key, key, label.keys(), registry=registry)
            metric_num = result[key]
            if type(metric_num) == str:
                metric_num = text_to_num(metric_num)
            labels_values = label.values()
            gauge.labels(*labels_values).set(metric_num)
            metric = generate_latest(registry=registry)
            metrics.append(metric.decode('utf-8'))
    cursor.close()
    con.close()
            
    return metrics
