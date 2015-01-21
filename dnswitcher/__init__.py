# coding: utf8
__author__ = 'JinXing'

import sys
import time
from config import load_config
from checker import pick_fastest_ping
from updater import update_record
from utils import plog


def do_main(conf):
    for info in conf.get("domains"):
        domain = info["domain"]
        hosts = info["hosts"]
        plog(u"检查域名: %s", domain)
        # pick fastest domain
        fastest_host = pick_fastest_ping(hosts)
        plog(u"响应最快的主机: %s", fastest_host)

        # update_recode
        new_value = update_record(domain, fastest_host)
        plog(u"新的记录值: %s => %s", domain, new_value)


def main():
    conf_file = sys.argv[1]
    conf = load_config(conf_file)
    while 1:
        try:
            do_main(conf)
            sleep_minute = conf.get("sleep", 30)
            plog(u"%d 分钟后执行下一次检查", sleep_minute)
            time.sleep(sleep_minute * 60)
        except KeyboardInterrupt, _:
            sys.exit(0)
        except Exception, e:
            plog(e.message)
            time.sleep(60)


if __name__ == "__main__":
    main()
