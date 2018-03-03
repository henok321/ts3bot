#!/usr/bin/env python3

import configparser

import ts3

__all__ = ["notify_bot"]


def notify_bot(ts3conn, config):
    print("Start Notify Bot ...")
    submitter = config['notify']['submitter'].split(',')
    recipient = config['notify']['recipient'].split(',')

    ts3conn.servernotifyregister(event="server")
    while True:
        event = ts3conn.wait_for_event()

        try:
            reasonid_ = event[0]["reasonid"]
        except KeyError:
            continue

        if reasonid_ == "0":
            print("User joined Lobby:")
            print(event[0])
            servergroups = event[0]['client_servergroups']
            guestname = event[0]['client_nickname']
            if (not set(servergroups.split(",")).isdisjoint(submitter)):
                admins = [client for client in list(ts3conn.clientlist(groups=True)) if
                          (not set(recipient).isdisjoint(client['client_servergroups'].split(",")))]

                print("Send notification to:")
                print(admins)
                for c in admins:
                    ts3conn.sendtextmessage(msg="Guest {0} joined the lobby!".format(guestname), target=c['clid'],
                                            targetmode=1)
    return None


if __name__ == "__main__":
    print("Start TS Bot ...")

    config = configparser.ConfigParser()
    config.sections()
    config.read("config/ts3bot.ini")

    print("Config loaded!")

    HOST = config['server']['url']
    PORT = config['server']['query_port']
    USER = config['server']['query_user']
    PASS = config['server']['query_pw']
    SID = config['server']['sid']
    NAME = config['bot']['name']

    print("Connecting to query interface ...")

    try:
        with ts3.query.TS3Connection(HOST, PORT) as ts3conn:
            ts3conn.login(client_login_name=USER, client_login_password=PASS)
            ts3conn.use(sid=SID)
            ts3conn.clientupdate(client_nickname=NAME)
            print("Connected!")

            notify_bot(ts3conn, config)
            ts3conn.close()
    except KeyboardInterrupt:
        print("TS Bot terminated by user!")
