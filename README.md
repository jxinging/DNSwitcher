# DNSwitcher
检查域名对应的多台主机的网络情况，并调用 dnspod-api 自动切换 DNS 解析到网络较好的主机

## Install
```shell
git clone https://github.com/jinxingxing/DNSwitcher
cd DNSwitcher/
git submodule init && git submodule update
cd dnspod-python && python setup.py install && cd ..
python setup.py install
```

## Usage
1. `cp dnswitcher-example.json /etc/dnswitcher.json`
2. 编辑 `/etc/dnswitcher.json` 的 `email` 和 `password` 字段，用于登陆 dnspod
3. dnswitcher /etc/dnswitcher.json

## TODO
