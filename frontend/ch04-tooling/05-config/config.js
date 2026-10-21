/* ===== 对应笔记 4.5 配置管理 ===== */

/**
 * 三种环境的差异全部集中在这一张表里。
 * 别处任何代码都不许再写死接口地址 —— 只从 getConfig() 拿。
 */
var ENV_CONFIG = {
    development: {
        label: '开发',
        apiBase: 'http://localhost:3000/api',
        timeout: 10000,
        debug: true,
        logLevel: 'debug'
    },
    staging: {
        label: '预发',
        apiBase: 'https://staging.example.com/api',
        timeout: 8000,
        debug: true,
        logLevel: 'info'
    },
    production: {
        label: '生产',
        apiBase: 'https://api.example.com/api',
        timeout: 5000,
        debug: false,
        logLevel: 'error'
    }
};

var DEFAULT_ENV = 'development';

/**
 * 决定当前用哪套配置，优先级从高到低：
 *   1. URL 上的 ?env=production —— 临时验证某个环境用
 *   2. 域名判断                 —— 线上真实做法，部署到哪个域名就是哪个环境
 *   3. 默认 development         —— 本地直接打开文件时兜底
 *
 * @param {string} search   例如 location.search，可传空
 * @param {string} hostname 例如 location.hostname，本地文件打开时为空
 * @returns {string} development / staging / production
 */
function resolveEnv(search, hostname) {
    var fromQuery = new URLSearchParams(search || '').get('env');
    if (fromQuery && ENV_CONFIG[fromQuery]) {
        return fromQuery;
    }

    var host = hostname || '';
    if (host === 'api.example.com' || host === 'www.example.com') {
        return 'production';
    }
    if (host.indexOf('staging.') === 0) {
        return 'staging';
    }

    return DEFAULT_ENV;
}

/**
 * 取配置。传入不认识的环境名时退回默认值，
 * 避免 ?env=abc 这种手误把页面搞崩。
 * @param {string} env
 */
function getConfig(env) {
    var key = ENV_CONFIG[env] ? env : DEFAULT_ENV;
    var preset = ENV_CONFIG[key];

    return {
        env: key,
        label: preset.label,
        apiBase: preset.apiBase,
        timeout: preset.timeout,
        debug: preset.debug,
        logLevel: preset.logLevel
    };
}
