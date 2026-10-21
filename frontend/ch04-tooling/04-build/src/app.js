/**
 * 构建演示的入口脚本。
 *
 * 依赖 src/utils.js 里的 formatSize —— 构建时按顺序合并，
 * 所以 utils.js 必须排在 app.js 前面，否则运行时会报 formatSize is not defined。
 */
(function () {
    'use strict';

    var box = document.getElementById('buildDemo');

    // 页面上没有这个元素时直接退出，避免在别的页面引用时报错
    if (!box) {
        return;
    }

    // 演示数据：模拟一次构建前后的体积
    var beforeBytes = 12 * 1024 + 512;
    var afterBytes = 4 * 1024 + 768;

    var savedPercent = ((beforeBytes - afterBytes) / beforeBytes * 100).toFixed(1);

    var html = [
        '<p>构建前：<strong>' + formatSize(beforeBytes) + '</strong></p>',
        '<p>构建后：<strong>' + formatSize(afterBytes) + '</strong></p>',
        '<p>减少：<strong>' + savedPercent + '%</strong>，耗时 ' + formatDuration(120) + '</p>'
    ].join('');

    box.innerHTML = html;
})();
