from flask import Flask

from flask_apscheduler import APScheduler
from config import zombi_name, check_interval_sec, zombi_log_file
import subprocess
import daemon
import logging
from logging.handlers import RotatingFileHandler
import argparse

app = Flask(__name__)

scheduler = APScheduler()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
rfh = logging.handlers.RotatingFileHandler(
    filename=zombi_log_file,
    mode="a",
    maxBytes=5*1024*1024,
    backupCount=2,
    encoding=None,
    delay=False
)

logger.addHandler(rfh)


def get_docker_ps() -> list:
    cmd = "/usr/bin/docker ps"
    id_list = []
    try:
        all_lines = subprocess.check_output(cmd, shell=True, text=True)
        if len(all_lines) > 20:
            for line in all_lines.split("\n"):
                if len(line) > 10:
                    id_list.append(line.split(' ')[0])
        id_list.remove("CONTAINER")
    except subprocess.SubprocessError:
        pass
    finally:
        pass
    return id_list


def get_ps():
    pid_map = {}
    try:
        cmd = f"/usr/bin/ps aux | /usr/bin/grep '{zombi_name}' | /usr/bin/grep -v 'grep'"
        or_line = subprocess.check_output(cmd, shell=True, text=True)
        if len(or_line) > 0:
            lines = or_line.split("\n")
            cnt = 0
            for line in lines:
                if len(line) > 1:
                    ps_infos = line.split()
                    if len(ps_infos) > 1:
                        docker_id = ps_infos[14][0:12]
                        pid = ps_infos[1]
                        pid_map[docker_id] = pid
                cnt += 1
    except subprocess.SubprocessError:
        pass
    finally:
        pass
    return pid_map


def kill_zombi(pid):
    cmd = f"/usr/bin/kill -9 {pid}"
    subprocess.check_output(cmd, shell=True, text=True)


@scheduler.task('interval', id='check_zombi', seconds=check_interval_sec)
def check_zombi():
    logging.info(f'This job is executed every {check_interval_sec} seconds.[kill zombi of "{zombi_name}"]')
    id_list = get_docker_ps()
    pid_map = get_ps()
    kill_id_list = []
    keys = pid_map.keys()
    for key in keys:
        if key not in id_list:
            kill_id_list.append(pid_map.get(key))
    for kill_id in kill_id_list:
        logging.info(f'zombi_id = {kill_id}')
        kill_zombi(kill_id)


def main():
    scheduler.init_app(app)
    scheduler.start()
    app.run()


if __name__ == '__main__':
    file_name = f'python {__name__}'
    parser = argparse.ArgumentParser(
        prog=file_name,
        description='check daemon and kill it.')
    parser.add_argument('-d', '--daemon', type=int, default=1,
                        help='An integer which means daemon or not. Default values is 1.')
    args = parser.parse_args()

    if args.daemon == 1:
        with daemon.DaemonContext(files_preserve=[rfh.stream, ],):
            main()
    else:
        main()
