#!/usr/bin/env python3

import configparser
import logging
import threading
import time

import ts3

__all__ = ["notify_bot"]

logging.basicConfig(filename='data/logs/ts3bot.log',
                    level=logging.INFO,
                    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
                    )

logging.getLogger().addHandler(logging.StreamHandler())


def notify_bot(ts3conn, config, lock):
    logging.info("Start Notify Bot ...")
    submitter = config['notify']['submitter'].split(',')
    recipient = config['notify']['recipient'].split(',')

    lock.acquire()
    ts3conn.servernotifyregister(event="server")
    lock.release()

    while True:
        event = ts3conn.wait_for_event()

        try:
            reasonid_ = event[0]["reasonid"]
        except KeyError:
            continue

        if reasonid_ == "0":
            logging.info("User joined Lobby:")
            logging.info(event[0])
            servergroups = event[0]['client_servergroups']
            guestname = event[0]['client_nickname']
            lock.acquire()
            if (not set(servergroups.split(",")).isdisjoint(submitter)):
                admins = [client for client in list(ts3conn.clientlist(groups=True)) if
                          (not set(recipient).isdisjoint(client['client_servergroups'].split(",")))]

                logging.info("Send notification to:")
                logging.info(admins)
                for c in admins:
                    ts3conn.sendtextmessage(msg="Guest {0} joined the lobby!".format(guestname), target=c['clid'],
                                            targetmode=1)
            lock.release()
    return None


def keep_alive(ts3conn, lock):
    while True:
        logging.info("Send keep alive!")
        lock.acquire()
        ts3conn.send_keepalive()
        lock.release()
        time.sleep(300)


if __name__ == "__main__":
    logging.info("Start TS Bot ...")

    config = configparser.ConfigParser()
    config.sections()
    config.read("data/config/ts3bot.ini")

    logging.info("Config loaded!")

    HOST = config['server']['url']
    PORT = config['server']['query_port']
    USER = config['server']['query_user']
    PASS = config['server']['query_pw']
    SID = config['server']['sid']
    NAME = config['bot']['name']

    logging.info("Connecting to query interface ...")

    try:
        with ts3.query.TS3Connection(HOST, PORT) as ts3conn:
            ts3conn.login(client_login_name=USER, client_login_password=PASS)
            ts3conn.use(sid=SID)
            ts3conn.clientupdate(client_nickname=NAME)
            logging.info("Connected!")

            lock = threading.Lock()

            notify_thread = threading.Thread(target=notify_bot, args=(ts3conn, config, lock), daemon=True, name="notify")
            keep_alive_thread = threading.Thread(target=keep_alive, args=(ts3conn, lock), daemon=True, name="keep_alive")

            notify_thread.start()
            keep_alive_thread.start()

            keep_alive_thread.join()
            notify_thread.join()

    except KeyboardInterrupt:
        logging.info("TS Bot terminated by user!")
    finally:
        ts3conn.close()
