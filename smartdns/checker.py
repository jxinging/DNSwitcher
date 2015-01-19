# coding: utf8
__author__ = 'JinXing'

import sys
import os
import re
from utils import pdebug


def net_score(loss, rtt):
    """根据丢包率和延时得到一个网络质量的评分，值越小越好"""
    return int(loss*10 + rtt/10)


def ping_cmd_str(count, psize, timeout):
    if os.name == "nt":
        return "ping -n %d -l %d -w %d" % (count, psize, timeout*1000)
    else:
        return "ping -c %d -s %d -W %d" % (count, psize, timeout)


def parse_ping_result(res):
    loss = 100
    rtt = None

    m = re.search("([0-9]+)%", res)
    if not m:
        return loss, rtt
    loss = int(m.group(1))

    if os.name == "nt":
        m = re.search("([0-9]+)[ \t]*ms$", res)
    else:
        m = re.search("([0-9\.]+)/([0-9\.]+)/([0-9\.]+)[ \t]*ms", res)
    if m:
        rtt = int(float(m.group(1)))

    return loss, rtt


def sys_ping(dest, count=4, psize=64, timeout=2):
    """调用系统命令进行 ping 测试

    :returns: loss%, avg_rtt
    """

    if os.name == "nt":
        cmd = "ping -n %d -l %d -w %d %s" % (count, psize, timeout*1000, dest)
    else:
        cmd = "ping -c %d -s %d -W %d %s" % (count, psize, timeout, dest)

    res = os.popen(cmd).read()
    return parse_ping_result(res)


def pick_fastest_ping(hosts):
    fastest_score = sys.maxint
    fastest_host = None
    for host in hosts:
        # 调用系统命令，不需要 root 权限即可进行 ping 测试
        loss, artt = sys_ping(host, count=5, psize=512)
        if artt is None:
            artt = 9999

        score = net_score(loss, artt)
        pdebug("%s, loss: %d%%, rtt: %d, score: %d", host, loss, artt, score)
        if score < fastest_score:
            fastest_host = host
            fastest_score = score

    return fastest_host