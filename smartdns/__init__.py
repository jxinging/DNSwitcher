# coding: utf8
__author__ = 'JinXing'

import sys
import time
from config import load_config
from checker import pick_fastest_ping
from updater import update_record
from utils import plog


def do_main(conf_file):
    conf = load_config(conf_file)
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

    sleep_time = conf.get("sleep") * 60
    plog(u"%dm 后执行下一次检查", conf.get("sleep"))
    time.sleep(sleep_time)


def main():
    try:
        while 1:
            do_main(sys.argv[1])
    except KeyboardInterrupt, _:
        sys.exit(0)

if __name__ == "__main__":
    main()
