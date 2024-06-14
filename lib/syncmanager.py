from multiprocessing.managers import SyncManager

sync_auth_key = b'aimmopc12'
sync_svc_port = 4600
sync_name = "syncdict"


class SharedMemManager(SyncManager):
    def shutdown(self) -> None:
        pass


sm_manager: SharedMemManager = None


def init_redis_cron_lock_4_client(name: str):
    global sm_manager
    SharedMemManager.register(name)
    
    sm_manager = SharedMemManager(("127.0.0.1", sync_svc_port), authkey=sync_auth_key)
    sm_manager.connect()
    
    return sm_manager


def init_redis_cron_lock_4_server(name: str, get_dict: object):
    global sm_manager
    SharedMemManager.register(name, get_dict)
    sm_manager = SharedMemManager(("127.0.0.1", sync_svc_port), authkey=sync_auth_key)
    sm_manager.start()
    
    return sm_manager


def fint_redis_cron_lock():
    global sm_manager
    sm_manager.shutdown()


def SMManagerPutDeco(origin_func):
    def wrapper_func(*args, **kwargs):
        
        with init_redis_cron_lock_4_client(name=sync_name) as manager:
            metrics = origin_func(*args, **kwargs)
            syncdict = sm_manager.syncdict()
            for key in metrics.keys():
                syncdict.update([(key, metrics[key])])
            fint_redis_cron_lock()
    
    return wrapper_func
