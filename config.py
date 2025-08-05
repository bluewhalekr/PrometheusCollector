"""
configuration
"""
resource_name = "eimmo-batch-vms"
service_name = "eimmo-batch-vms-worker3"
zombi_name = "containerd-shim-runc-v2"
check_interval_sec = 120
zombi_log_file = "zombi_kill.log"
mongodb_uri = "mongodb://test:******@localhost:37027"
one_minute_task = "redis_metrics"
twenty_seconds_task = "els_alarm"
redis_hosts = [":tester:localhost:6379:test-redis",]
redis_use_ssl = False
els_address = "http://localhost:9200"
els_index_prefix="backend-api-"
slack_channel_name = "alpha-eimmo"
mysql_host = "172.0.0.1"
mysql_user = "tester"
mysql_password = "******"
cert_file_path = ['/etc/ssl/cert.pem']
rabbitmq_info = {"addr": "localhost:15672",
                 "user": "monitor",
                 "passwd": "monitor"
                 }
