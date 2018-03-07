#!/usr/bin/env python3

import configparser
import logging
import threading

import ts3

from modules.keep_alive import KeepAlive
from modules.notify import Notify

logging.basicConfig(filename='data/logs/ts3bot.log',
                    level=logging.INFO,
                    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
                    )

logging.getLogger().addHandler(logging.StreamHandler())

if __name__ == "__main__":
    logging.info("Start TS Bot ...")

    # parse config file
    config = configparser.ConfigParser()
    config.sections()
    config.read("data/config/ts3bot.ini")

    logging.info("Config loaded!")
    logging.info("Connecting to query interface ...")

    try:
        # connect via telnet
        with ts3.query.TS3Connection(config['server']['url'], config['server']['query_port']) as ts3conn:
            ts3conn.login(client_login_name=config['server']['query_user'],
                          client_login_password=config['server']['query_pw'])
            # server parameter
            ts3conn.use(sid=config['server']['sid'])
            ts3conn.clientupdate(client_nickname=config['bot']['name'])
            logging.info("Connected!")

            # init modules
            notify = Notify(ts3conn, config)
            keep_alive = KeepAlive(ts3conn)

            modules = [notify, keep_alive]

            # init threads
            module_threads = []

            for m in modules:
                module_threads.append(threading.Thread(target=m.run, daemon=True, name=m.__class__.__name__))

            for t in module_threads:
                t.start()

            for t in module_threads:
                t.join()

    except KeyboardInterrupt:
        logging.info("TS Bot terminated by user!")
    finally:
        ts3conn.close()
