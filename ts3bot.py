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

    config = configparser.ConfigParser()
    config.sections()
    config.read("data/config/ts3bot.ini")

    logging.info("Config loaded!")
    logging.info("Connecting to query interface ...")

    try:
        with ts3.query.TS3Connection(config['server']['url'], config['server']['query_port']) as ts3conn:
            ts3conn.login(client_login_name=config['server']['query_user'],
                          client_login_password=config['server']['query_pw'])
            ts3conn.use(sid=config['server']['sid'])
            ts3conn.clientupdate(client_nickname=config['bot']['name'])
            logging.info("Connected!")

            notify = Notify(ts3conn, config)
            keep_alive = KeepAlive(ts3conn)

            notify_thread = threading.Thread(target=notify.run, daemon=True, name="notify")
            keep_alive_thread = threading.Thread(target=keep_alive.run, daemon=True, name="keep_alive")

            notify_thread.start()
            keep_alive_thread.start()

            keep_alive_thread.join()
            notify_thread.join()

    except KeyboardInterrupt:
        logging.INFO(60 * "=")
        logging.info("TS Bot terminated by user!")
        logging.INFO(60 * "=")
    finally:
        ts3conn.close()
