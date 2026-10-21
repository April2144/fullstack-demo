# 第 8–9 章 · 服务器与部署 / 域名、HTTPS 与备案

对应笔记：`8.1 云服务器选购与初始化` / `8.2 Linux 基础命令` / `8.3 安装 Python 环境与 MySQL` /
`8.4 使用 Nginx 反向代理` / `8.5 进程管理与守护` / `8.6 Nginx 与 Uvicorn 部署 FastAPI` /
`9.1 域名注册与解析` / `9.2 HTTPS 证书申请与配置` / `9.3 网站备案流程` / `9.4 公安联网备案` / `9.5 上线后的基础监控`

> ⚠️ **这一章全部是只读参考**：配置文件与脚本是给你复制到服务器上用的，
> 不要在本机执行，也不要把这里的 `example.com` 当成真实域名去跑。

## 文件对照

| 笔记 | 文件 | 放到服务器的哪里 |
|---|---|---|
| 8.1 | 本文件「一、选购与初始化」 | — |
| 8.2 | `cheatsheet.md` | —（命令速查） |
| 8.3 | `scripts/install-python-mysql.sh` | 上传后 `sudo bash` 执行一次 |
| 8.4 | `nginx/fullstack.conf` | `/etc/nginx/sites-available/fullstack.conf` |
| 8.5 | `systemd/fullstack.service` | `/etc/systemd/system/fullstack.service` |
| 8.6 | `scripts/deploy.sh` | `/srv/fullstack/deploy.sh`（每次发版执行） |
| 9.1 | 本文件「四、域名与解析」 | — |
| 9.2 | `nginx/https.conf` | 替换 8.4 那份的对应 server 段 |
| 9.3 / 9.4 | 本文件「五、备案」 | — |
| 9.5 | `scripts/healthcheck.sh` | 配合 crontab 每 5 分钟跑一次 |

## 一、8.1 选购与初始化清单

| 项目 | 建议 | 说明 |
|---|---|---|
| 配置 | 2 核 2G 起步 | 1G 内存跑 MySQL + Python 会频繁 OOM；先小后升配比一步到位更省钱 |
| 带宽 | 按量 / 3–5 Mbps | 小站按固定带宽更可控；流量突增用按量计费 |
| 地域 | 靠近用户，且与备案接入商一致 | 国内服务器 + 域名必须备案才能用 80/443 |
| 系统 | Ubuntu 22.04 / 24.04 LTS | LTS 有 5 年支持；不要选非 LTS 图新 |
| 登录方式 | 密钥登录，禁用密码 | 密码登录每天都会被爆破 |
| 安全组 | 只开 22 / 80 / 443 | **8000 端口绝不要对公网开放** |
| 快照 | 装完环境先打一个 | 配崩了 10 分钟就能回到干净状态 |

初始化顺序（照做即可）：

```bash
# 1. 改 SSH 端口前先放行新端口，否则会把自己关在门外
sudo ufw allow 2222/tcp && sudo ufw allow OpenSSH

# 2. 时区（日志时间错了，排障会多看一倍日志）
sudo timedatectl set-timezone Asia/Shanghai

# 3. 建一个非 root 的部署账号
sudo adduser deploy && sudo usermod -aG sudo deploy

# 4. 关掉 root 密码登录（改 /etc/ssh/sshd_config）
#    PermitRootLogin no
#    PasswordAuthentication no
sudo systemctl restart ssh
```

## 二、8.6 一次完整部署的顺序

```text
① 跑 install-python-mysql.sh          → Python / MySQL / Nginx 就位
② git clone 到 /srv/fullstack         → 代码到位
③ 建 venv 并装 requirements.txt        → 依赖到位（脚本已做）
④ 写 db_config.json                   → 数据库连接串（不进 git）
⑤ 放 nginx/fullstack.conf 并 nginx -t  → 反向代理生效
⑥ 放 systemd/fullstack.service        → 守护进程生效
⑦ systemctl enable --now fullstack    → 服务常驻
⑧ bash deploy.sh                      → 之后的每次发版都走它
⑨ 配 healthcheck.sh + crontab          → 出问题有人知道
```

关键校验点，任何一步不过就别往下走：

```bash
sudo nginx -t                                  # 语法错误会在这里暴露，不会打断线上
curl -fsS localhost:8000/api/health            # 后端自己活着
curl -I http://example.com/api/health          # 经过 Nginx 也活着
systemctl status fullstack                     # active (running)
```

## 三、8.4 / 8.5 两份配置在看什么

- `nginx/fullstack.conf`：`proxy_pass` 结尾**有没有斜杠**决定路径前缀是否被吃掉，这是最高频的坑；
  四个 `X-Forwarded-*` 头不传，后端就拿不到真实客户端 IP
- `systemd/fullstack.service`：`Restart=always` + `User=www-data` + `--host 127.0.0.1` 是三条底线；
  `--workers 2` 会让「进程内内存状态」失效，本项目用 SQLite 文件，多 worker 并发写会锁表，
  真上线请换成第 6 章的 MySQL

## 四、9.1 域名与解析

| 记录类型 | 主机记录 | 值 | 用途 |
|---|---|---|---|
| A | `@` | 服务器公网 IP | 裸域 `example.com` |
| A | `www` | 服务器公网 IP | `www.example.com` |
| CNAME | 其他子域 | `example.com` | 以后换 IP 只改一处 |

- 解析生效有缓存，一般 10 分钟内，最长 TTL 时间；用 `dig example.com +short` 验证
- 国内服务器：**域名未备案，80/443 会被接入商拦截**，这不是 Nginx 的问题
- 证书要覆盖用到的所有名字：`example.com` 和 `www.example.com` 都要申请，否则一个会报证书不匹配

## 五、9.3 / 9.4 备案（以接入商与官方平台当期要求为准）

**ICP 备案（网站备案）**

1. 在服务器提供商的备案系统提交（谁给你服务器，就在谁那里备）
2. 准备材料：主体证件（企业营业执照 / 个人身份证）、域名证书、网站负责人信息、
   应急联系方式、网站服务内容说明
3. 接入商初审 → 短信/人脸核验 → 提交管局 → 管局审核（各省时长不同，通常 1–20 个工作日）
4. 通过后拿到备案号，按要求展示在网站页脚：
   `京ICP备XXXXXXXX号`（以实际下发为准）
5. **备案期间网站不要对外提供访问**，否则可能被驳回

**公安联网备案**

- 网站**开通后 30 日内**，到全国互联网安全管理服务平台（`beian.mps.gov.cn`）办理
- 需要先有 ICP 备案号；填写网站信息、负责人信息，审核通过后拿到公安备案号
- 同样要求展示在页脚，通常与 ICP 号并列

> 各地管局细则会变，以接入商后台的实时清单为准；上面是通用流程，不是承诺。

## 六、9.5 上线后先看什么

`scripts/healthcheck.sh` 检查五项，够小站用很久：

| 检查 | 失败通常意味着 |
|---|---|
| `/api/health` 探活 | 进程挂了 / 端口没起 / Nginx 转发错 |
| nginx、mysql、fullstack 三个服务 | 某个服务没设开机自启，重启机器后掉了 |
| 磁盘使用率 | 日志没清，`journalctl --vacuum-time=7d` 能救急 |
| 证书剩余天数 | 自动续期没生效，`certbot renew --dry-run` 查原因 |
| 近 5 分钟 500 条数 | 代码 bug 或数据库连不上 |

再补两个低成本但很有用的动作：

```bash
# 1. Nginx 日志按天切分（不切分会把磁盘写满）
#    /etc/logrotate.d/nginx 通常已自带，确认一下即可
cat /etc/logrotate.d/nginx

# 2. 数据库每天备份到另一块盘
#    0 3 * * * mysqldump -u fullstack -p'密码' fullstack_demo | gzip > /backup/db-$(date +\%F).sql.gz
```

## 七、部署阶段最常见的五个坑

1. **`proxy_pass` 多了个斜杠** → 后端收到的路径少了 `/api`，全是 404
2. **改了 unit 文件没 `daemon-reload`** → systemd 还在用旧配置，改了等于没改
3. **8000 端口对公网开放** → 绕过 Nginx 直接打后端，HTTPS、限流、日志全部失效
4. **用 root 跑业务进程** → 一旦有漏洞，整台机器都交出去了
5. **只在浏览器里测「打得开」** → 没测 404 页面、没测接口错误码、没测证书到期时间

## 八、与其它章节的关系

- 后端代码来自 `backend/ch07-api/`（FastAPI + Uvicorn）
- 数据库用第 6 章的 MySQL 版表结构；`db_config.json` 里的账号密码由 `install-python-mysql.sh` 生成
- 前端产物来自第 4 章的构建流程（`dist/`），Nginx 的 `root` 指向它
