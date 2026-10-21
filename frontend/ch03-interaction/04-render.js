// ===== 对应笔记 3.4 动态交互与数据渲染（二）渲染逻辑 =====
// 数据流：fetch 一次 → 存进 state.allItems → 每次改条件只重算 filtered → 重渲染列表

const listEl = document.getElementById('itemList');
const pagerEl = document.getElementById('pager');
const statusEl = document.getElementById('statusHint');
const emptyEl = document.getElementById('emptyState');
const keywordEl = document.getElementById('keyword');
const categoryEl = document.getElementById('category');
const sortEl = document.getElementById('sortBy');

const PAGE_SIZE = 6;

/* ---------- 1. 状态集中放一处，避免散落全局变量 ---------- */
const state = {
    allItems: [],      // 全量数据，fetch 一次后不再变
    keyword: '',
    category: '',
    sortBy: 'date-desc',
    page: 1,
    totalPages: 1,
};

/* ---------- 2. 防抖：连续输入只执行最后一次 ---------- */
function debounce(fn, delay = 250) {
    let timer = null;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

/* ---------- 3. 安全渲染：不用 innerHTML 拼用户内容 ---------- */
/**
 * 把文本追加到父节点；命中关键词的部分用 <mark> 包起来。
 * 全程只用 createTextNode / textContent —— 即使标题里有 <script> 也只会当文字显示。
 */
function appendHighlighted(parent, text, keyword) {
    const kw = (keyword || '').trim();
    if (!kw) {
        parent.append(document.createTextNode(text));
        return;
    }

    const lowerText = text.toLowerCase();
    const lowerKw = kw.toLowerCase();
    let cursor = 0;
    let hit = lowerText.indexOf(lowerKw, cursor);

    if (hit === -1) {
        parent.append(document.createTextNode(text));
        return;
    }

    while (hit !== -1) {
        if (hit > cursor) parent.append(document.createTextNode(text.slice(cursor, hit)));

        const mark = document.createElement('mark');
        mark.className = 'hl';
        mark.textContent = text.slice(hit, hit + kw.length);
        parent.append(mark);

        cursor = hit + kw.length;
        hit = lowerText.indexOf(lowerKw, cursor);
    }

    if (cursor < text.length) parent.append(document.createTextNode(text.slice(cursor)));
}

/** 生成一条列表项 */
function createItemNode(item) {
    const li = document.createElement('li');
    li.className = 'note-item';

    const textWrap = document.createElement('div');
    textWrap.style.flex = '1';
    textWrap.style.minWidth = '0';

    const title = document.createElement('div');
    title.className = 'note-text';
    appendHighlighted(title, item.title, state.keyword);

    const meta = document.createElement('div');
    meta.className = 'note-meta';
    meta.textContent = `${item.date} · ${item.views} 次浏览`;

    textWrap.append(title, meta);

    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = item.category.toUpperCase();

    li.append(textWrap, tag);
    return li;
}

/* ---------- 4. 计算：筛选 → 排序 → 分页 ---------- */
function getVisibleItems() {
    const kw = state.keyword.trim().toLowerCase();

    let items = state.allItems.filter((item) => {
        const matchKeyword = !kw || item.title.toLowerCase().includes(kw);
        const matchCategory = !state.category || item.category === state.category;
        return matchKeyword && matchCategory;
    });

    // 排序：用 slice 复制一份，避免 sort 改动原数组顺序
    items = items.slice().sort((a, b) => {
        if (state.sortBy === 'views-desc') return b.views - a.views;
        if (state.sortBy === 'date-asc') return a.date.localeCompare(b.date);
        return b.date.localeCompare(a.date);           // date-desc 默认
    });

    state.totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
    if (state.page > state.totalPages) state.page = state.totalPages;

    const start = (state.page - 1) * PAGE_SIZE;
    return {
        pageItems: items.slice(start, start + PAGE_SIZE),
        total: items.length,
    };
}

/* ---------- 5. 渲染列表：DocumentFragment 一次性插入 ---------- */
function render() {
    const { pageItems, total } = getVisibleItems();

    // 先清空：textContent = '' 比 removeChild 循环更快
    listEl.textContent = '';

    if (total === 0) {
        emptyEl.classList.remove('is-hidden');
        statusEl.textContent = '共 0 条';
        pagerEl.textContent = '';
        return;
    }

    emptyEl.classList.add('is-hidden');

    // 关键：先在内存里拼好，再一次性挂到页面上，只触发一次布局
    const fragment = document.createDocumentFragment();
    pageItems.forEach((item) => fragment.append(createItemNode(item)));
    listEl.append(fragment);

    const from = (state.page - 1) * PAGE_SIZE + 1;
    const to = Math.min(state.page * PAGE_SIZE, total);
    statusEl.textContent = `共 ${total} 条，当前显示第 ${from}–${to} 条`;

    renderPager();
}

/* ---------- 6. 渲染分页 ---------- */
function renderPager() {
    pagerEl.textContent = '';

    const makeBtn = (label, page, { disabled = false, current = false } = {}) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = label;
        btn.disabled = disabled;
        if (current) btn.classList.add('is-current');
        btn.addEventListener('click', () => {
            state.page = page;
            render();
        });
        return btn;
    };

    pagerEl.append(makeBtn('上一页', state.page - 1, { disabled: state.page === 1 }));

    for (let page = 1; page <= state.totalPages; page += 1) {
        pagerEl.append(makeBtn(String(page), page, { current: page === state.page }));
    }

    pagerEl.append(makeBtn('下一页', state.page + 1, { disabled: state.page === state.totalPages }));
}

/* ---------- 7. 事件绑定 ---------- */
// 搜索：防抖 250ms。控制台能看到实际触发次数，和输入次数对比
let searchCount = 0;
const onSearch = debounce(() => {
    searchCount += 1;
    console.log(`[3.4] 第 ${searchCount} 次真正执行搜索：` + (keywordEl.value || '(空)'));
    state.keyword = keywordEl.value;
    state.page = 1;                     // 换关键词必须回到第一页
    render();
}, 250);

keywordEl.addEventListener('input', onSearch);

categoryEl.addEventListener('change', () => {
    state.category = categoryEl.value;
    state.page = 1;
    render();
});

sortEl.addEventListener('change', () => {
    state.sortBy = sortEl.value;
    state.page = 1;
    render();
});

/* ---------- 8. 启动：只请求一次数据 ---------- */
async function loadItems() {
    try {
        const response = await fetch('data/items.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        state.allItems = Array.isArray(data) ? data : (data.items || []);
        render();
    } catch (error) {
        // 本地直接双击（file://）打开时会走到这里，提示改用 HTTP 访问
        console.error('[3.4] 数据加载失败', error);
        statusEl.textContent = '数据加载失败：请用 HTTP 方式打开本页（见 README）';
    }
}

loadItems();
