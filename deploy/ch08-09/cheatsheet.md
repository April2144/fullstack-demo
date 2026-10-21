# 8.2 Linux 基础命令速查

> 只列上服务器后真正会用到的那几十条。每条都给「什么时候用」，命令本身可以复制。

## 一、连上去

```bash
ssh root@1.2.3.4                       # 第一次用密码登录
ssh-keygen -t ed25519 -C "me@example.com"   # 本机生成密钥（比 RSA 更短更安全）
ssh-copy-id root@1.2.3.4               # 把公钥装到服务器，之后免密
ssh -p 2222 deploy@1.2.3.4             # 改过端口就这样连
```

改过 SSH 端口后，务必先 `ufw allow 2222` 再重启 sshd，否则会把自己关在门外。

```bash
scp app.tar.gz root@1.2.3.4:/srv/      # 传单个文件
rsync -avz --progress ./dist/ root@1.2.3.4:/srv/fullstack/frontend/dist/   # 传目录（增量，快）
```

## 二、看目录和磁盘

```bash
pwd                        # 我在哪
ls -lah                    # 列表：含隐藏文件、人类可读大小
cd -                       # 回到上一个目录
du -sh * | sort -h         # 当前目录谁最占空间（排障第一步）
df -h                      # 磁盘还剩多少
find /var/log -name "*.log" -size +100M    # 找大日志文件
```

## 三、看日志（最常用）

```bash
tail -f /var/log/nginx/error.log                 # 实时跟，Ctrl+C 退出
tail -n 200 /var/log/nginx/access.log            # 最后 200 行
grep -n "500" /var/log/nginx/access.log | tail   # 找 5xx
journalctl -u fullstack -f                       # 实时看服务日志
journalctl -u fullstack --since "10 min ago" --no-pager
journalctl -u fullstack -p err -n 100            # 只看 error 级别
journalctl --vacuum-time=7d                      # 清 7 天前的日志（磁盘满了先做这个）
```

## 四、进程与服务

```bash
ps aux | grep uvicorn      # 进程在不在
top                        # 谁在吃 CPU / 内存（q 退出）
free -h                    # 内存使用
systemctl status fullstack # 服务状态 + 最近几行日志
systemctl restart fullstack
systemctl enable --now fullstack    # 开机自启 + 立刻启动
kill -15 <pid>             # 优雅停止（先试这个，让程序处理完在途请求）
kill -9 <pid>              # 强杀（最后手段，可能丢数据）
```

## 五、端口与网络

```bash
ss -tlnp                   # 哪些端口在监听、被哪个进程占用（比 netstat 快）
lsof -i:8000               # 谁占用了 8000
curl -I https://example.com          # 只看响应头（验证 HTTPS、301 跳转）
curl -fsS localhost:8000/api/health  # 静默探活，失败返回非 0
dig example.com +short               # 域名解析到哪个 IP
ping -c 4 example.com
```

## 六、权限

```bash
chmod 644 file      # rw-r--r--  普通文件
chmod 755 dir       # rwxr-xr-x  目录、可执行脚本
chown -R www-data:www-data /srv/fullstack   # 改属主（Nginx / systemd 跑 www-data）
sudo -u www-data bash deploy.sh             # 以 www-data 身份执行
umask               # 看新建文件的默认权限
```

权限数字的含义：`4 读 / 2 写 / 1 执行`，三位分别是「自己 / 同组 / 其他」。

## 七、装软件

```bash
apt update && apt upgrade -y
apt install -y nginx mysql-server
apt list --installed | grep nginx
dpkg -l | grep mysql
```

## 八、定时任务

```bash
crontab -e            # 编辑当前用户的定时任务
crontab -l            # 查看
# 每 5 分钟探活，失败才发邮件
*/5 * * * * /srv/fullstack/deploy/ch08-09/scripts/healthcheck.sh || mail -s "站点异常" you@example.com
```

> 排障顺序建议：**先看服务状态 → 再看日志 → 再查端口 → 最后查磁盘/内存**。
> 90% 的「网站打不开」在前两步就能定位。
