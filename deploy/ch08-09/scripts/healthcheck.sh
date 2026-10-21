#!/usr/bin/env bash
# ===== 对应笔记 9.5 上线后的基础监控 =====
#
# ⚠️ 只读参考：在服务器上执行；不要在本机跑（检查的是服务器状态）
#
# 用途：最朴素的「有问题就告警」，比装一整套监控系统更适合刚上线的小站
# 用法：
#   手动：bash healthcheck.sh
#   定时：crontab -e 加一行，每 5 分钟查一次，只在失败时发邮件
#         */5 * * * * /srv/fullstack/deploy/ch08-09/scripts/healthcheck.sh || mail -s "站点异常" you@example.com
#
# 输出约定：每行一个检查项，FAIL 会累加退出码，任何一项失败退出码为 1

set -uo pipefail   # 注意：这里不用 -e，单检查失败要继续跑完其余项

DOMAIN="${DOMAIN:-example.com}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/api/health}"
DISK_LIMIT="${DISK_LIMIT:-85}"      # 磁盘告警阈值（百分比）
CERT_DAYS="${CERT_DAYS:-14}"        # 证书剩余天数告警阈值
fail=0

pass() { echo "PASS  $1"; }
warn() { echo "WARN  $1"; }
bad()  { echo "FAIL  $1"; fail=1; }

# ---------- 1. 接口探活 ----------
# -f：HTTP >= 400 视为失败；--max-time：避免脚本卡死
body="$(curl -fsS --max-time 5 "${HEALTH_URL}" 2>/dev/null || true)"
if [ -z "${body}" ]; then
    bad "接口无响应：${HEALTH_URL}"
elif echo "${body}" | grep -q '"status":"ok"'; then
    pass "接口正常：${body}"
else
    bad "接口返回异常：${body}"
fi

# ---------- 2. 进程状态 ----------
for svc in nginx mysql fullstack; do
    if systemctl is-active --quiet "${svc}"; then
        pass "服务运行中：${svc}"
    else
        bad "服务未运行：${svc}（journalctl -u ${svc} -n 50）"
    fi
done

# ---------- 3. 磁盘 ----------
# 取根分区使用率，去掉百分号后比较
usage="$(df -P / | awk 'NR==2 {gsub("%", "", $5); print $5}')"
if [ "${usage}" -ge "${DISK_LIMIT}" ]; then
    bad "磁盘使用率 ${usage}%（阈值 ${DISK_LIMIT}%）—— 先清日志：journalctl --vacuum-time=7d"
elif [ "${usage}" -ge $((DISK_LIMIT - 10)) ]; then
    warn "磁盘使用率 ${usage}%，接近阈值"
else
    pass "磁盘使用率 ${usage}%"
fi

# ---------- 4. 证书到期 ----------
# 只在域名能解析时才查，本地测试环境跳过
if command -v openssl >/dev/null 2>&1 && getent hosts "${DOMAIN}" >/dev/null 2>&1; then
    end_date="$(echo | openssl s_client -servername "${DOMAIN}" -connect "${DOMAIN}:443" 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)"
    if [ -n "${end_date}" ]; then
        end_ts="$(date -d "${end_date}" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "${end_date}" +%s 2>/dev/null)"
        days=$(( (end_ts - $(date +%s)) / 86400 ))
        if [ "${days}" -lt "${CERT_DAYS}" ]; then
            bad "证书只剩 ${days} 天，执行：sudo certbot renew"
        else
            pass "证书剩余 ${days} 天"
        fi
    else
        warn "证书信息读取失败（443 不通或证书未配置）"
    fi
else
    warn "跳过证书检查（域名 ${DOMAIN} 无法解析）"
fi

# ---------- 5. 最近 5 分钟错误日志条数 ----------
# 5xx 才是真问题；404 多半是扫描器，不用管
errors="$(journalctl -u fullstack --since '5 min ago' --no-pager 2>/dev/null | grep -c ' 500 ' || true)"
if [ "${errors}" -gt 0 ]; then
    bad "近 5 分钟出现 ${errors} 条 500，去看：journalctl -u fullstack --since '5 min ago'"
else
    pass "近 5 分钟无 500"
fi

echo "----"
[ "${fail}" -eq 0 ] && echo "全部检查通过" || echo "存在失败项"
exit "${fail}"
