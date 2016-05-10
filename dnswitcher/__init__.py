# coding: utf8
__author__ = 'JinXing'

import sys
import time
from config import load_config
from checker import pick_fastest_host, sys_ping, request_url_by_ss
from updater import update_record
from utils import plog
from functools import partial


def do_main(conf):
    check_type = conf.get('check_type', 'shadowsocks')
    if check_type == 'shadowsocks':
        ss_config = conf['shadowsocks']
        ss_checker = partial(request_url_by_ss,
                             server_port=int(ss_config['server_port']),
                             password=str(ss_config['password']),
                             method=str(ss_config['method']),
                             url=str(ss_config['check_url']),
                             timeout=int(ss_config.get('timeout', 5)))
        checker_func = ss_checker
    elif check_type == 'ping':
        ping_checker = partial(sys_ping, count=10, psize=512)
        checker_func = ping_checker
    else:
        raise ValueError('unknown check_type: %s' % check_type)

    for info in conf.get("domains"):
        domain = info["domain"]
        hosts = info["hosts"]
        plog(u"检查域名: %s", domain)
        fastest_host = pick_fastest_host(hosts, checker_func)
        plog(u"响应最快的主机: %s", fastest_host)

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
            import traceback
            traceback.print_exc()
            plog(str(e.message))
            time.sleep(60)


if __name__ == "__main__":
    main()
