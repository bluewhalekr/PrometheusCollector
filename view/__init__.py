"""
view init
"""
from view.allview import about
from view.allview import get_mysql
from view.allview import get_redis
from view.allview import get_mongodb, get_mongodb_isalive
from view.allview import view_docker_ps_cnt
from view.allview import view_containerd_cnt
from view.allview import view_docker_ps_abnormal_cnt
from view.allview import view_process_cnt
from view.allview import view_fd, view_fd_default
from view.allview import view_cpu, view_disk, view_memory, view_file_size
from view.allview import view_cert_validate_days
from view.allview import view_os_version
from view.allview import view_es_yesterday_index_length, view_es_current_index_length
from view.allview import view_rabbitmq_queue_item_cnt, view_rabbitmq_queue_item_cnt_root


def add_url_rules(app):
    """ add_url_rules """
    app.add_url_rule('/about', view_func=about)
    app.add_url_rule('/metric/mysql/<db_name>/<table_name>', view_func=get_mysql)
    app.add_url_rule('/metric/redis', view_func=get_redis)
    app.add_url_rule('/metric/mongodb', view_func=get_mongodb)
    app.add_url_rule('/metric/docker', view_func=view_docker_ps_cnt)
    app.add_url_rule('/metric/containerd', view_func=view_containerd_cnt)
    app.add_url_rule('/metric/docker-abnormal', view_func=view_docker_ps_abnormal_cnt)
    app.add_url_rule('/metric/process', view_func=view_process_cnt)
    app.add_url_rule('/metric/fd/<cmd_type>', view_func=view_fd)
    app.add_url_rule('/metric/fd', view_func=view_fd_default)
    app.add_url_rule('/metric/cpu', view_func=view_cpu)
    app.add_url_rule('/metric/disk', view_func=view_disk)
    app.add_url_rule('/metric/os/version', view_func=view_os_version)
    app.add_url_rule('/metric/memory', view_func=view_memory)
    app.add_url_rule('/metric/file_size/<file_name_path>', view_func=view_file_size)
    app.add_url_rule('/metric/mongodb/is_alive', view_func=get_mongodb_isalive)
    app.add_url_rule('/metric/ssl/validate/days', view_func=view_cert_validate_days)
    app.add_url_rule('/metric/es/idx_size/yesterday/<name>/<is_stream_idx>', view_func=view_es_yesterday_index_length)
    app.add_url_rule('/metric/es/idx_size/current/<name>/<is_stream_idx>', view_func=view_es_current_index_length)
    app.add_url_rule('/metric/rabbitmq/queue_item_cnt/<queue_name>/<vhost_name>', view_func=view_rabbitmq_queue_item_cnt)
    app.add_url_rule('/metric/rabbitmq/queue_item_cnt/<queue_name>', view_func=view_rabbitmq_queue_item_cnt_root)
