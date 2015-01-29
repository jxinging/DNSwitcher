# coding: utf8
__author__ = 'JinXing'

import sys
import os
import re
import threading
import Queue
import tempfile

from utils import pdebug
from config import get
import time

try:
    import json
except ImportError, _:
    import samplejson as json


def net_score(loss, rtt):
    """根据丢包率和延时得到一个网络质量的评分，值越小越好"""
    return int(loss*10 + rtt/10)


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


class QueueWrap(object):
    def __init__(self, queue):
        self.queue = queue
        self.func = None

    def wrap(self, *args, **kwargs):
        item = [args[0]]
        item.extend(self.func(*args, **kwargs))
        self.queue.put(item)

    def __call__(self, func):
        self.func = func
        return self.wrap


def pick_fastest_ping(hosts):
    history_data = load_history()
    fastest_score = sys.maxint
    fastest_host = None
    curr_data = {"time": int(time.time())}

    queue = Queue.Queue()
    m_sys_ping = QueueWrap(queue)(sys_ping)
    threads = []
    for host in hosts:
        # 调用系统命令，不需要 root 权限即可进行 ping 测试
        t = threading.Thread(name=host, target=m_sys_ping, args=(host,),
                             kwargs={"count": 10, "psize": 512})
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    while queue.qsize() > 0:
        try:
            r = queue.get()
            host, loss, artt = r
        except Queue.Empty, _:
            continue

        if artt is None:
            artt = 9999

        score = net_score(loss, artt)
        overall_score = calc_overall_score(host, score, history_data)
        pdebug("%s, loss: %d%%, rtt: %d, score: %d, overall_score: %d",
               host, loss, artt, score, overall_score)
        curr_data[host] = {"loss": loss, "rtt": artt, "score": score}
        if overall_score < fastest_score:
            fastest_host = host
            fastest_score = overall_score

    history_data.append(curr_data)
    if len(history_data) > 10:
        history_data.pop(0)
    dump_history(history_data)

    return fastest_host


def calc_overall_score(host, curr_score, history_data):
    percent = 0.9
    history_score = 0
    for data in history_data[-1:-10:-1]:    # 从尾部开始取最后9个
        history_score += data.get(host, {}).get("score", 0) * percent
        percent -= 0.1

    return int(history_score + curr_score)


def load_history():
    history_file = os.path.join(tempfile.gettempdir(), get("history"))
    if not os.path.exists(history_file):
        return []

    pdebug("load data from %s", history_file)
    return json.load(open(history_file))


def dump_history(data):
    history_file = os.path.join(tempfile.gettempdir(), get("history"))
    indent = 4 if get("debug") else None
    json.dump(data, open(history_file, "wb"), indent=indent)

