# coding: utf8
__author__ = 'JinXing'

import sys
from config import load_config
from checker import pick_fastest_ping
from updater import update_record
from utils import plog


def main(config_file=sys.argv[1]):
    c = load_config(config_file)
    for info in c.get("domains"):
        domain = info["domain"]
        hosts = info["hosts"]
        plog(u"检查域名: %s", domain)
        # pick domain fastest
        fastest_host = pick_fastest_ping(hosts)
        plog(u"响应最快的主机: %s", fastest_host)

        # update_recode
        new_value = update_record(domain, fastest_host)
        plog(u"新的记录值: %s", new_value)

if __name__ == "__main__":
    print sys.argv[0]
    main(sys.argv[1])
