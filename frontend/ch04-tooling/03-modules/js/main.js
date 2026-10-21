// ===== 对应笔记 4.3 代码规范与模块化：页面逻辑 =====
// 这一层只做三件事：拿数据 → 调工具处理 → 渲染到 DOM。
// 它不写 fetch 细节（在 api.js），也不写格式化细节（在 utils.js）。

import { fetchNotes } from './api.js';
import { formatDate, truncate, sortByDateDesc } from './utils.js';

const listEl = document.getElementById('moduleList');
const statusEl = document.getElementById('moduleStatus');

/** 渲染列表：只用 createElement + textContent，不拼 innerHTML */
function render(items) {
    listEl.textContent = '';

    const fragment = document.createDocumentFragment();
    items.forEach((item) => {
        const li = document.createElement('li');
        li.className = 'note-item';

        const text = document.createElement('span');
        text.className = 'note-text';
        text.textContent = truncate(item.title, 24);

        const meta = document.createElement('span');
        meta.className = 'note-meta';
        meta.textContent = formatDate(item.date);

        li.append(text, meta);
        fragment.append(li);
    });
    listEl.append(fragment);
}

async function init() {
    statusEl.textContent = '加载中…';
    try {
        const notes = await fetchNotes();
        const sorted = sortByDateDesc(notes);
        render(sorted);
        statusEl.textContent = `共 ${sorted.length} 条（数据来自 api.js）`;
    } catch (error) {
        // 直接双击打开（file://）时会走到这里：ES Module 与 fetch 都需要 HTTP
        console.error('[4.3] 加载失败', error);
        statusEl.textContent = '加载失败：请用 HTTP 打开本页（见 README）';
    }
}

init();
