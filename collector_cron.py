from flask import Flask

from flask_apscheduler import APScheduler
from config import one_minute_task, twenty_seconds_task
import daemon
import logging
from logging.handlers import RotatingFileHandler
import argparse
from importlib.util import spec_from_file_location, module_from_spec


app = Flask(__name__)

scheduler = APScheduler()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
rfh = logging.handlers.RotatingFileHandler(
    filename="collector_cron.log",
    mode="a",
    maxBytes=5 * 1024 * 1024,
    backupCount=2,
    encoding=None,
    delay=False
)

logger.addHandler(rfh)


def class_from_file(file_path: str) -> []:
    spec = spec_from_file_location('service.name', file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    run_op = getattr(module, "run")
    return run_op


def one_minute_task_01_internal():
    logging.info(f'one_minute_task_01 : started')
    task_list = one_minute_task.split(',')
    
    for task in task_list:
        if len(task) > 0:
            run_op = class_from_file(f"./cron_task/{task}.py")
            run_op()


def twenty_seconds_task_01_internal():
    logging.info(f'twenty_seconds_task_01 : started')
    task_list = twenty_seconds_task.split(',')
    
    for task in task_list:
        if len(task) > 0:
            run_op = class_from_file(f"./cron_task/{task}.py")
            run_op()


@scheduler.task('interval', id='twenty_seconds_task_01', seconds=30)
def twenty_seconds_task_01():
    twenty_seconds_task_01_internal()


@scheduler.task('interval', id='one_minute_task_01', seconds=60)
def one_minute_task_01():
    one_minute_task_01_internal()


def once_calling():
    one_minute_task_01()


def main():
    scheduler.init_app(app)
    scheduler.start()
    app.run()


if __name__ == '__main__':
    file_name = f'python {__name__}'
    parser = argparse.ArgumentParser(
        prog=file_name,
        description='metric collector cron task.')
    parser.add_argument('-d', '--daemon', type=int, default=1,
                        help='An integer which means daemon or not or once calling. Default values is 1.')
    args = parser.parse_args()
    
    import os
    
    if args.daemon == 1:
        with daemon.DaemonContext(files_preserve=[rfh.stream, ], working_directory=os.getcwd()):
            main()
    else:
        if args.daemon == 2:
            once_calling()
        else:
            main()
