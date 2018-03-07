import logging
import time


class KeepAlive:
    def __init__(self, ts3conn):
        self.ts3conn = ts3conn

    def run(self):
        while True:
            logging.info("Send keep alive!")
            self.ts3conn.send_keepalive()
            time.sleep(300)
