# DNSwitcher
监控同一域名下多台主机的网络情况，并调用 dnspod-api 自动切换 DNS 解析到网络较好的主机

## Install
```shell
git clone https://github.com/jinxingxing/DNSwitcher
cd DNSwitcher/
git submodule init && git submodule update
cd dnspod-python && python setup.py install && cd ..
python setup.py install
```

## Config
示例配置见：dnswitcher-example.json
```shell
{
  "email": "your_email@example.com",  # dnspod 用户名
  "password": "your_password",        # dnspod 密码
  "debug": true,  # 开启调试模式 (打印调试日志)
  "sleep": 30,    # 监控的间隔时间(分钟)
  "history": "dnswitcher-history.json",  # 记录历史数据的文件名
  "domains": [
    {
      "domain": "example.com",  # 监控的域名
      "hosts": [  # 域名对应的主机列表
        "s1.example.com",   # 配置的是域名，使用 CNAME 记录解析
        "127.0.0.1"         # 配置的是IP，使用 A 记录解析
      ]
    },
    {
      "domain": "example2.com", # 另一个监控的域名
      "hosts": [
        "s1.example2.com",
        "127.0.0.1"
      ]
    }
  ]
}
```

## Usage
1. `cp dnswitcher-example.json /etc/dnswitcher.json`
2. 编辑 `/etc/dnswitcher.json` 配置好 `email`、`password`、`domains` 
3. 启动：`dnswitcher /etc/dnswitcher.json`

## TODO
