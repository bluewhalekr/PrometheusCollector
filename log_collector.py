import time
import os
import logging
import argparse
import json
import sys

log_format = "%(levelname)s %(asctime)s = %(message)s"

logging.basicConfig(stream=sys.stdout, filemode="a", format=log_format, level=logging.INFO)
logger = logging.getLogger()

ignore_lines = ["No drop-pending idents have expired",
                "Removing historical entries older than",
                "Slow query",
                "Received interrupt request for unknown op",
                "Scanning sessions",
                "running TTL job for index",
                "Completed unstable checkpoint.",
                "Finished checkpoint, updated iteration counter",
                "WiredTiger message",
                "Checkpoint thread sleeping",
                "Deleted expired documents using index",
                "cleaning up unused lock buckets of the global lock manager",
                "Collection does not exist. Using EOF plan",
                "WiredTigerSizeStorer::store",
                "Using idhack",
                "Connection ended",
                "Received first command on ingress connection since session start or auth handshake",
                "Checking authorization failed",
                "User assertion",
                "Terminating session due to error",
                "Ending session",
                "Session from remote encountered a network error during SourceMessage",
                "Assertion while executing command",
                "Command not found in registry",
                "Interrupted operation as its client disconnected",
                "client metadata",
                "Auth metrics report",
                "Only one plan is available",
                ]

exclude_cmds = ['hello',
                'ping',
                'ismaster',
                'getLog',
                'isMaster',
                'getParameter',
                'isClusterMember',
                'aggregate',
                'buildInfo',
                'saslStart',
                'saslContinue',
                'endSessions',
                'connectionStatus',
                'listCollections',
                'listDatabases',
                'hostInfo',
                'top',
                'replSetUpdatePosition',
                'replSetHeartbeat',
                'getMore',
                'serverStatus',
                'dbStats',
                'getCmdLineOpts',
                ]

retry_count = 0

api_server_url_pre = "http://eimmo-infra-manager.koreacentral.cloudapp.azure.com:8080/mongodb/user/put"


def send_data(data, api_url):
    import requests
    headers = {'Content-type': 'application/json'}
    date = data['date']
    if date.endswith('Z'):
        date = date.replace('Z', '')
        data['date'] = date
        print(f'data = {data}')
        try:
            r = requests.post(api_url, json=data, headers=headers)
            logging.info(f'result = {r}')
        except Exception as e:
            logging.error(f'Exception: {e}')


def send_user_access(date: str, ctx: str, cmd: str, client: str, user: str, db: str):
    data = {'date': date, 'ctx': ctx, 'cmd': cmd, 'client': client, 'user': user, 'db': db}
    api_url = api_server_url_pre + "/access"
    send_data(data=data, api_url=api_url)


def send_user_command(date: str, ctx: str, cmd: str, client: str, table_name: str, db: str):
    data = {'date': date, 'ctx': ctx, 'cmd': cmd, 'client': client, 'table': table_name, 'db': db}
    api_url = api_server_url_pre + "/command"
    send_data(data=data, api_url=api_url)


def check_command(log_dict):
    cmd_info = log_dict["attr"]["commandArgs"]
    cmd_keys = list(cmd_info.keys())
    cmd = cmd_keys[0]
    client = log_dict["attr"]["client"]
    if cmd not in exclude_cmds and len(client) > 0:
        table = cmd_info.get(cmd)
        db = log_dict["attr"]["db"]
        date = log_dict["t"]["$date"]
        ctx = log_dict["ctx"]
        logging.info(f'=== {date} ctx = {ctx}, cmd = {cmd}, client = {client}, table = {table}, db = {db}')
        send_user_command(date=date, ctx=ctx, cmd=cmd, client=client, table_name=table, db=db)
        return
    if "speculativeAuthenticate" in cmd_info.keys:
        auth_info = cmd_info['speculativeAuthenticate']
        db = auth_info['db']
        user = "userdb.won@aimmo.co.kr".replace(db+".", "")
        ctx = log_dict["ctx"]
        date = log_dict["t"]["$date"]
        send_user_access(date=date, ctx=ctx, cmd=cmd, client=client, user=user, db=db)


def check_accept_state(log_dict):
    pass

def check_authenticated(log_dict):
    date = log_dict["t"]["$date"]
    client = log_dict["attr"]["client"]
    user = log_dict["attr"]["user"]
    db = log_dict["attr"]["db"]
    ctx = log_dict["ctx"]
    logging.info(f'=== {date} ctx = {ctx}, cmd = AUTH, client = {client}, user = {user}, db = {db}')
    send_user_access(date=date, ctx=ctx, cmd="AUTH", client=client, user=user, db=db)


def check_connection_ended(log_dict):
    date = log_dict["t"]["$date"]
    client = log_dict["attr"]["remote"]
    ctx = log_dict["ctx"]
    logging.info(f'=== {date} ctx = {ctx}, cmd = DISCON, client = {client}')


def check_returning_user_from_cache(log_dict):
    pass


monitoring_lines = {"Connection accepted": check_accept_state,
                    "Returning user from cache": check_returning_user_from_cache,
                    "About to run the command": check_command,
                    "Successfully authenticated": check_authenticated,
                    "Connection ended": check_connection_ended,
                    }


def trace_log(thefile):
    global retry_count
    logging.info(f'start follow - {thefile}')
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            try:
                os.stat(thefile.name)
            except FileNotFoundError as e:
                logging.info('trace_log retry_count = {retry_count}')
                log_monitor(thefile.name)
                continue

                # print(f'\n\n*** lines = {line}')%
        if line.startswith('{'):
            log_dict = json.loads(line)
            if log_dict["msg"] in monitoring_lines.keys():
                monitoring_lines.get(log_dict["msg"])(log_dict)
                # print(f'line = {log_dict["t"]["$date"]} {log_dict["msg"]}')
    logging.info(f'end follow - {thefile}')


def get_arg_logpath():
    parser = argparse.ArgumentParser(description='Mongodb Log Monitoring.')
    parser.add_argument('--filepath', dest='filepath', action='store', default="")
    args = parser.parse_args()
    return args.filepath


def log_monitor(fileName: str):
    global retry_count
    try:
        with open(mongodb_log_path, "rt") as fd:
            logging.info(f'success to open file {fd}')
            retry_count = 0
            trace_log(fd)
            fd.close()
    except FileNotFoundError as e:
        logging.error(f'trace_log retry_count = {retry_count}')
        time.sleep(0.1)
        if retry_count < 300:
            retry_count += 1
            log_monitor(fileName)


if __name__ == "__main__":
    try:
        mongodb_log_path = os.environ['MONGO_LOG']
    except Exception as e:
        mongodb_log_path = get_arg_logpath()
    
    logging.info(f'log_path = {mongodb_log_path}')
    log_monitor(mongodb_log_path)
