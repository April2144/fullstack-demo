/* ===== 4.5 现场演示：只负责把配置渲染到页面上 ===== */

/**
 * 职责边界：环境判断在 config.js（resolveEnv），
 * 这里只做「取配置 → 写 DOM」，不重复写判断逻辑。
 */
(function () {
    'use strict';

    var select = document.getElementById('envSelect');

    // 页面上没有这个下拉框时直接退出，避免别的页面引用时报错
    if (!select) {
        return;
    }

    var els = {
        label: document.getElementById('envLabel'),
        timeout: document.getElementById('envTimeout'),
        debug: document.getElementById('envDebug'),
        apiBase: document.getElementById('envApiBase'),
        source: document.getElementById('envSource')
    };

    var queryEnv = new URLSearchParams(window.location.search).get('env');
    var initialEnv = resolveEnv(window.location.search, window.location.hostname);

    // 判断初始环境是「URL 指定的」「域名匹配的」还是「兜底默认值」，
    // 用 config.js 的规则反查，不在这里重写一遍判断逻辑
    var defaultEnv = resolveEnv('', '');
    var hostEnv = resolveEnv('', window.location.hostname);
    var initialSource;
    if (queryEnv && getConfig(queryEnv).env === queryEnv) {
        initialSource = 'URL 参数 ?env=' + queryEnv;
    } else if (hostEnv !== defaultEnv) {
        initialSource = '域名判断：' + window.location.hostname;
    } else {
        initialSource = window.location.hostname
            ? '默认值（域名 ' + window.location.hostname + ' 未匹配任何环境）'
            : '默认值（本地文件打开，无域名）';
    }

    select.value = initialEnv;

    /** @param {string} env @param {string} sourceText */
    function render(env, sourceText) {
        var config = getConfig(env);

        els.label.textContent = config.label;
        els.timeout.textContent = config.timeout / 1000 + ' 秒';
        els.debug.textContent = config.debug ? '开启' : '关闭';
        els.apiBase.textContent = config.apiBase;
        els.source.textContent = '当前环境来源：' + sourceText;
    }

    select.addEventListener('change', function () {
        render(select.value, '手动切换（只在本次浏览生效，不改 URL）');
    });

    render(initialEnv, initialSource);
})();
