// ===== 对应笔记 2.4 DOM 操作与事件处理 =====
// 本文件只操作 index.html 里的「新增笔记」区块。

/* ---------- 1. 选中元素 ---------- */
// querySelector 返回第一个匹配项；getElementById 更快，但只能按 id 找
const form = document.getElementById('noteForm');
const input = document.getElementById('noteInput');
const list = document.getElementById('noteList');
const countHint = document.getElementById('countHint');

// 页面没有这些元素时跳过（本文件也可能被别的页面引用）
// ⚠️ 脚本顶层不允许 return，所以后面统一用「可选链 + 函数内守卫」，
//    而不是只打一行 warn 就继续往下执行 —— 那样会在 form.addEventListener 处抛 TypeError。
if (!form || !input || !list || !countHint) {
    console.warn('[2.4] 当前页面没有笔记区块，已跳过');
}

/* ---------- 2. 渲染：用 createElement 而不是拼 innerHTML ---------- */
// 拼 innerHTML 会把用户输入当成 HTML 解析，存在 XSS 风险；
// createElement + textContent 才是安全的写法。
function addNoteItem(text) {
    if (!list) return;                // 守卫：目标列表不存在时直接不做事
    const li = document.createElement('li');
    li.className = 'note-item';

    const span = document.createElement('span');
    span.className = 'note-text';
    span.textContent = text;          // 纯文本，不会被当成标签

    const del = document.createElement('button');
    del.type = 'button';
    del.className = 'note-del';
    del.textContent = '删除';

    li.append(span, del);
    list.append(li);
    updateCount();
}

function updateCount() {
    if (!countHint || !list) return;  // 守卫：元素不全时直接返回
    countHint.textContent = `共 ${list.children.length} 条`;
}

/* ---------- 3. 事件：提交表单 ---------- */
form?.addEventListener('submit', (event) => {   // ?. 守卫：form 不存在时不会抛错
    event.preventDefault();           // 阻止表单默认的整页刷新

    const text = input.value.trim();
    if (!text) {
        input.focus();
        return;
    }

    addNoteItem(text);
    input.value = '';                 // 清空输入框
    input.focus();
});

/* ---------- 4. 事件委托：删除按钮统一在父级监听 ---------- */
// 列表项是动态创建的，逐个绑定监听会漏掉新增项；
// 绑在父级上，通过 event.target 判断点到了谁，更省事也更稳。
list?.addEventListener('click', (event) => {
    if (!event.target.classList.contains('note-del')) return;

    const item = event.target.closest('.note-item');
    if (item) item.remove();
    updateCount();
});

/* ---------- 5. 初始状态 ---------- */
['先写结构，再写样式，最后加交互', '语义化标签比 div 更好维护'].forEach(addNoteItem);
updateCount();

/* ---------- 6. 补充：显示与隐藏（对应笔记 2.4 十、10.1） ---------- */
const toggleBtn = document.getElementById('toggleBtn');
const togglePanel = document.getElementById('togglePanel');

// 页面可能没有这块内容，先判空再绑定，避免报错
if (toggleBtn && togglePanel) {
    toggleBtn.addEventListener('click', () => {
        const willShow = togglePanel.hidden;   // 当前是隐藏的，点一下就显示

        togglePanel.hidden = !willShow;
        // 状态变了，按钮文案和无障碍属性都要跟着改
        toggleBtn.setAttribute('aria-expanded', String(willShow));
        toggleBtn.textContent = willShow ? '收起面板' : '展开面板';
    });
}

/* ---------- 7. 补充：实时搜索（对应笔记 2.4 十、10.3） ---------- */
// 这里用独立的一份数据，不干扰上面的「新增笔记」列表
const searchInput = document.getElementById('searchInput');
const searchList = document.getElementById('searchList');
const searchHint = document.getElementById('searchHint');
const searchEmpty = document.getElementById('searchEmpty');

const searchSource = [
    '语义化标签让结构自己说话',
    'CSS 变量改一处全站生效',
    'DOM 查询优先用 querySelector',
    '事件委托绑在父级上更稳',
    'fetch 必须判断 response.ok',
];

/** 按关键词过滤并重新渲染搜索结果 */
function renderSearch(keyword) {
    const kw = keyword.trim().toLowerCase();
    const matched = kw
        ? searchSource.filter((text) => text.toLowerCase().includes(kw))
        : searchSource;

    searchList.textContent = '';                  // 先清空，避免旧结果残留

    const fragment = document.createDocumentFragment();
    matched.forEach((text) => {
        const li = document.createElement('li');
        li.className = 'note-item';
        li.textContent = text;
        fragment.append(li);
    });
    searchList.append(fragment);

    searchHint.textContent = `共 ${matched.length} 条`;
    // 没有结果时才显示空状态提示
    searchEmpty.hidden = matched.length > 0;
}

if (searchInput && searchList) {
    // 逐字符过滤：写法最直白，数据量大时要加防抖（第 3 章 3.4）
    searchInput.addEventListener('input', () => renderSearch(searchInput.value));
    renderSearch('');                             // 初始显示全部
}
