from flask import Flask
import daemon
import argparse

app = Flask(__name__)

from view import add_url_rules


def main():
    add_url_rules(app)
    app.run(host="0.0.0.0", port=5001)


if __name__ == '__main__':
    file_name = f'python {__name__}'
    parser = argparse.ArgumentParser(
        prog=file_name,
        description='collect the system metrics')
    parser.add_argument('-d', '--daemon', type=int, default=1,
                        help='An integer which means daemon or not. Default values is 1.')
    parser.add_argument('-c', '--redis_cron', type=int, default=0,
                        help='An integer which means to use cron daemon. Default values is 0.')
    args = parser.parse_args()
    
    if args.redis_cron == 1:
        from service.redis import init_redis_cron_lock
        
        init_redis_cron_lock()
    
    if args.daemon == 1:
        with daemon.DaemonContext():
            main()
    else:
        main()
    
    if args.redis_cron == 1:
        from service.redis import fint_redis_cron_lock
        
        fint_redis_cron_lock()
