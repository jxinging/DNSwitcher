# coding: utf8
__author__ = 'JinXing'

import sys
from ping import quiet_ping


def net_score(loss, rtt):
    """根据丢包率和延时得到一个网络质量的评分，值越小越好"""
    return int(loss*10 + rtt/10)


def pick_fastest_ping(hosts, debug=False):
    fastest_score = sys.maxint
    fastest_host = None
    for host in hosts:
        loss, _, artt = quiet_ping(host, count=10, psize=512)
        if artt is None:
            artt = 1000
        score = net_score(loss, artt)

        if debug:
            print "%s, loss: %d%%, rtt: %d, score: %d" \
                  % (host, loss, artt, score)

        if score < fastest_score:
            fastest_host = host
            fastest_score = score

    return fastest_host