# coding: utf8
__author__ = 'JinXing'

import sys
import os
import re
import threading
import Queue
import tempfile

from utils import logger
from config import get
import time

try:
    import json
except ImportError, _:
    import samplejson as json


def net_score(loss, rtt):
    """根据丢包率和延时得到一个网络质量的评分，值越小越好"""
    return int(loss * 10 + rtt / 10)


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
    loss, rtt = parse_ping_result(res)
    if rtt is None:
        score = None
    else:
        score = net_score(loss, rtt)
    logger.info("%s, loss: %d%%, rtt: %s, score: %s", dest, loss, rtt, score)
    return score


def request_url_by_ss(server_host, server_port, password, method, url, timeout=5):
    from ssclient import SimpleSSClient
    cli = SimpleSSClient(server_host, server_port, password, method, timeout=timeout)
    try:
        st = time.time()
        cli.get(url)
        cost_time = time.time() - st
        return cost_time
    except Exception as e:
        logger.error("%s: %s", server_host, e)
        import traceback
        logger.debug("%s: %s", server_host, traceback.format_exc())
        return None


class QueueWrap(object):
    def __init__(self, queue):
        self.queue = queue
        self.func = None

    def wrap(self, *args, **kwargs):
        item = [args[0], self.func(*args, **kwargs)]
        self.queue.put(item)

    def __call__(self, func):
        self.func = func
        return self.wrap


def pick_fastest_host(hosts, checker):
    history_data = load_history()
    fastest_score = sys.maxint
    fastest_host = None
    curr_data = {"time": int(time.time())}

    queue = Queue.Queue()
    wrapped_checker = QueueWrap(queue)(checker)
    threads = []
    for host in hosts:
        t = threading.Thread(name=host, target=wrapped_checker, args=(host,))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    while queue.qsize() > 0:
        try:
            host, score = queue.get()
        except Queue.Empty, _:
            continue

        if score is None:
            score = 9999

        overall_score = calc_overall_score(host, score, history_data)
        logger.info("%s, score: %.2f, overall_score: %.2f", host, score, overall_score)
        curr_data[host] = {"score": score}
        if overall_score < fastest_score:
            fastest_host = host
            fastest_score = overall_score

    history_data.append(curr_data)
    history_len = 1440 / get("sleep")  # 记录24小时的数据
    if len(history_data) > history_len:
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

    logger.info("load data from %s", history_file)
    return json.load(open(history_file))


def dump_history(data):
    history_file = os.path.join(tempfile.gettempdir(), get("history"))
    indent = 4 if get("debug") else None
    json.dump(data, open(history_file, "wb"), indent=indent)

