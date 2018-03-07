import logging
import threading
import time

import ts3


class KeepAlive:
    def __init__(self, ts3conn: ts3.query.TS3Connection, lock: threading.Lock):
        self.ts3conn = ts3conn
        self.lock = lock

    def run(self):
        while True:
            logging.info("Send keep alive!")
            self.lock.acquire()
            self.ts3conn.send_keepalive()
            self.lock.release()
            time.sleep(5)
