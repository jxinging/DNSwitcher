# coding: utf8
__author__ = 'JinXing'

import inspect
import config
from dnspod.apicn import DomainId, RecordList, RecordModify


def _auto_auth(func):
    """
    1. 自动添加认证信息
    2. 自动调用 __call__() """
    def wrap(*args, **kwargs):
        kwargs.update({
            "email": config.get("email"),
            "password": config.get("password")
        })
        o = func(*args, **kwargs)
        return o()
    return wrap


def dnspod_api_patch():
    from dnspod import apicn
    for name in dir(apicn):
        if name == 'ApiCn':
            continue

        attr = getattr(apicn, name)
        if inspect.isclass(attr):
            new_attr = _auto_auth(attr)
            setattr(apicn, name, new_attr)
            globals()[name] = new_attr

# dnspod_api_patch()
DomainId = _auto_auth(DomainId)
RecordList = _auto_auth(RecordList)
RecordModify = _auto_auth(RecordModify)


def update_record(domain, value, type_=None, ttl=600):
    """更新一条 DNS 记录

    type: DNS 记录类型, 默认的，当 host 为IP时使用 A 记录，
    当 host 为域名使用使用 CNAME 记录 """
    domain_arr = domain.split(".")
    top_domain = ".".join(domain_arr[-2:])
    record_name = domain_arr[0]
    if type_:
        record_type = type_
    elif value[0].isalpha():
        # 域名不可以数字开头
        record_type = 'CNAME'
    else:
        record_type = 'A'

    # domain id
    domain_id = DomainId(top_domain).get("domains", {})["id"]

    # record id
    record_list = RecordList(domain_id=domain_id)
    records = filter(lambda x: x["name"] == record_name,
                     record_list.get("records"))
    if not records:
        raise ValueError('Can\'t find record_name "%s", response:\n%s'
                         % (record_name, str(record_list)))

    record = records[0]
    if record.get("value") == value:
        return value
    record_id = record["id"]

    # update
    res = RecordModify(record_id, domain_id=domain_id, sub_domain=record_name,
                       record_type=record_type,
                       record_line=u"默认".encode("utf8"),
                       value=value, ttl=ttl)

    return res.get("record", {}).get("value")