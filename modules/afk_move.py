import logging
import threading
import time

import ts3


class AfkMove:
    def __init__(self, ts3conn: ts3.query.TS3Connection, config, lock: threading.Lock):
        self.ts3conn = ts3conn
        self.config = config
        self.lock = lock

    def run(self):
        max_idle_time = int(self.config['afk']['max_idle_time'])
        ignored_groups = self.config['afk']['ignored_groups'].split(',')
        afk_channel_id = '2'

        while True:
            logging.info("afk move")

            self.lock.acquire()
            clients = list(self.ts3conn.clientlist(groups=True, away=True, times=True, info=True))
            self.lock.release()

            try:
                clients = [c for c in clients if set(ignored_groups).isdisjoint(c['client_servergroups'].split(','))]
            except KeyError:
                continue

            logging.info(clients)

            for c in clients:
                if int(c['client_idle_time']) / 1000 / 60 > int(max_idle_time):
                    logging.info("move")
                    self.lock.acquire()
                    self.ts3conn.clientmove(clid=c['clid'], cid=afk_channel_id)
                    self.lock.release()

            logging.info(clients)
            time.sleep(10)
