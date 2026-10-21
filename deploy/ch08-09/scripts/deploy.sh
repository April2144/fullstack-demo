#!/usr/bin/env bash
# ===== 对应笔记 8.6 Nginx 与 Uvicorn 部署 FastAPI =====
#
# ⚠️ 只读参考：在服务器上手动执行，不要在本机跑
#
# 用法：sudo -u www-data bash deploy.sh [分支名]
# 做的事：拉代码 → 装依赖 → 重启服务 → 健康检查 → 失败就告诉你回滚命令
#
# 关键原则：
#   * 部署脚本必须「要么成功，要么能回到上一版」，不能停在半路
#   * 每一步都有 echo，日志就是你的排障依据

set -euo pipefail

APP_DIR="${APP_DIR:-/srv/fullstack}"
BRANCH="${1:-main}"
SERVICE="fullstack"
HEALTH_URL="http://127.0.0.1:8000/api/health"

echo "==> 0/5 记录当前版本（回滚时用）"
cd "${APP_DIR}"
PREVIOUS_COMMIT="$(git rev-parse --short HEAD)"
echo "    当前版本：${PREVIOUS_COMMIT}"

echo "==> 1/5 拉取最新代码"
git fetch --all --prune
git checkout "${BRANCH}"
# --ff-only：只允许快进合并。服务器上有本地改动时直接报错停下，
# 而不是悄悄产生一个合并提交（那种情况通常意味着有人手工改过线上文件）
git pull --ff-only
NEW_COMMIT="$(git rev-parse --short HEAD)"
echo "    目标版本：${NEW_COMMIT}"

if [ "${PREVIOUS_COMMIT}" = "${NEW_COMMIT}" ]; then
    echo "    代码没有变化，继续重启以保证配置生效"
fi

echo "==> 2/5 安装依赖"
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r backend/ch07-api/requirements.txt --quiet

echo "==> 3/5 重启服务"
# systemctl restart 会先停再起；只改代码时也可以 reload，但 restart 更彻底、更可预期
systemctl restart "${SERVICE}"

echo "==> 4/5 健康检查（最多重试 10 次，每次 1 秒）"
ok=0
for i in $(seq 1 10); do
    if curl -fsS --max-time 2 "${HEALTH_URL}" >/dev/null 2>&1; then
        ok=1
        break
    fi
    sleep 1
done

if [ "${ok}" -eq 1 ]; then
    echo "==> 5/5 部署成功，当前版本 ${NEW_COMMIT}"
    curl -s "${HEALTH_URL}" | head -c 200
    echo
    exit 0
fi

echo "!! 健康检查失败，服务可能没起来。先看日志："
echo "     journalctl -u ${SERVICE} -n 100 --no-pager"
echo "   确认要回滚时执行："
echo "     cd ${APP_DIR} && git checkout ${PREVIOUS_COMMIT} && systemctl restart ${SERVICE}"
exit 1

# 说明：这里没有做「自动回滚」。自动回滚看着高级，但会掩盖真正的问题 ——
# 首次失败就停下来看日志，比反复重启更快找到原因。
# 等积累了足够多的部署经验，再考虑接 CI/CD 做自动化（第 13 章）。
