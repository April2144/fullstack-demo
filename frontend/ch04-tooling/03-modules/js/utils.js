// ===== 对应笔记 4.3 代码规范与模块化：工具层 =====
// 约定：这一层只放纯函数 —— 给同样的输入就出同样的输出。
// 不发请求、不读 DOM、不碰 localStorage，所以可以直接复制到任何项目里用。

/**
 * 把 ISO 日期格式化成「2026-10-21」。
 * @param {string} iso 形如 2026-10-21T10:00:00
 * @returns {string}
 */
export function formatDate(iso) {
    if (!iso) return '';
    // slice 比 new Date() 更稳：不涉及时区换算，也不会因为格式不合法变成 Invalid Date
    return String(iso).slice(0, 10);
}

/**
 * 超出长度就截断并加省略号。
 * @param {string} text
 * @param {number} max
 */
export function truncate(text, max = 20) {
    const value = String(text ?? '');
    return value.length > max ? `${value.slice(0, max)}…` : value;
}

/**
 * 按日期倒序，返回新数组（不改原数组）。
 * @param {Array<{date: string}>} items
 */
export function sortByDateDesc(items) {
    // 用展开运算符复制：sort 会原地修改，直接排会污染调用方的数据
    return [...items].sort((a, b) => String(b.date).localeCompare(String(a.date)));
}
