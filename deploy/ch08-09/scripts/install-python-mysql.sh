#!/usr/bin/env bash
# ===== 对应笔记 8.3 安装 Python 环境与 MySQL =====
#
# ⚠️ 只读参考：这是新服务器上的初始化脚本，不要在本机执行
#
# 目标系统：Ubuntu 22.04 / 24.04（Debian 系通用）
# 用法：sudo bash install-python-mysql.sh
#
# 脚本做四件事：
#   1. 装基础软件（Python、venv、MySQL、Nginx、git）
#   2. 建库 + 建专用账号（不用 root 连业务库）
#   3. 建虚拟环境并装依赖
#   4. 打印后续手工步骤（MySQL 安全初始化必须交互，不能自动化）

set -euo pipefail   # 出错立即退出 / 未定义变量报错 / 管道任一段失败即失败

DB_NAME="${DB_NAME:-fullstack_demo}"
DB_USER="${DB_USER:-fullstack}"
APP_DIR="${APP_DIR:-/srv/fullstack}"

echo "==> 1/4 更新软件源并安装依赖"
export DEBIAN_FRONTEND=noninteractive   # 避免 apt 中途弹交互框卡住
apt-get update
apt-get install -y \
    python3 python3-venv python3-pip \
    mysql-server \
    nginx \
    git curl ufw

echo "==> 2/4 启动并设置开机自启"
systemctl enable --now mysql
systemctl enable --now nginx

echo "==> 3/4 创建数据库与专用账号"
# 密码用 openssl 随机生成，不要用 123456 这种；生成后自己存到密码管理器
DB_PASS="$(openssl rand -base64 18 | tr -d '/+=' | cut -c1-16)"
mysql <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT SELECT, INSERT, UPDATE, DELETE ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "    数据库：${DB_NAME}"
echo "    账号：  ${DB_USER}"
echo "    密码：  ${DB_PASS}   <-- 立刻保存，脚本不会再次显示"

echo "==> 4/4 创建虚拟环境并安装依赖"
mkdir -p "${APP_DIR}"
cd "${APP_DIR}"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
if [ -f backend/ch07-api/requirements.txt ]; then
    .venv/bin/pip install -r backend/ch07-api/requirements.txt
else
    echo "    未找到 backend/ch07-api/requirements.txt，跳过依赖安装（代码还没拉下来时属正常）"
fi

cat <<'TIPS'

---------- 还需要手工做的几件事 ----------
1. MySQL 安全初始化（交互式，无法脚本化）：
     sudo mysql_secure_installation
   依次回答：设 root 密码 → 删匿名用户 y → 禁止 root 远程登录 y → 删 test 库 y → 重载权限 y

2. 防火墙只放 22 / 80 / 443，8000 端口不要对外开放：
     sudo ufw allow OpenSSH
     sudo ufw allow 'Nginx Full'
     sudo ufw enable
     sudo ufw status verbose

3. 确认时区（日志时间对不上，排查会多花一倍时间）：
     timedatectl set-timezone Asia/Shanghai
     timedatectl

4. 把数据库密码写进应用的 db_config.json（不要提交到 git）：
     /srv/fullstack/backend/ch06-database/db_config.json
TIPS
