import logging
import threading

import ts3


class Notify:

    def __init__(self, ts3conn: ts3.query.TS3Connection, config, lock: threading.Lock):
        self.ts3conn = ts3conn
        self.config = config
        self.lock = lock

    def run(self):
        logging.info("Start Notify Bot ...")
        submitter = self.config['notify']['submitter'].split(',')
        recipient = self.config['notify']['recipient'].split(',')

        self.ts3conn.servernotifyregister(event="server")

        while True:
            event = self.ts3conn.wait_for_event()

            try:
                reasonid_ = event[0]["reasonid"]
            except KeyError:
                continue

            if reasonid_ == "0":
                logging.info("User joined Lobby:")
                logging.info(event[0])
                servergroups = event[0]['client_servergroups']
                guestname = event[0]['client_nickname']

                self.lock.acquire()

                if not set(servergroups.split(",")).isdisjoint(submitter):
                    admins = [client for client in list(self.ts3conn.clientlist(groups=True)) if
                              (not set(recipient).isdisjoint(client['client_servergroups'].split(",")))]

                    logging.info("Send notification to:")
                    logging.info(admins)
                    for c in admins:
                        self.ts3conn.sendtextmessage(msg="Guest {0} joined the lobby!".format(guestname),
                                                     target=c['clid'],
                                                     targetmode=1)
                self.lock.release()
