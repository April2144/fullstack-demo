// ===== 对应笔记 3.2 样式与主题设计（二）主题切换逻辑 =====
// 职责单一：只负责「读 / 存 / 切」主题，不碰页面其它逻辑。

const THEME_KEY = 'demo-theme';           // localStorage 的键名，统一在这里定义
const root = document.documentElement;    // 就是 <html>

/**
 * 取当前生效的主题。
 * 优先级：用户手动选过 > 系统偏好。
 * 返回 'dark' | 'light'
 */
function getTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'dark' || saved === 'light') return saved;

    // 没存过就跟随系统
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
}

/** 应用主题：只改 html 上的 data-theme，样式全部由 CSS 变量接管 */
function applyTheme(theme) {
    root.dataset.theme = theme;
    localStorage.setItem(THEME_KEY, theme);
    updateToggleText(theme);
}

/** 按钮文案跟着当前主题走，避免用户点了不知道切到哪 */
function updateToggleText(theme) {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.textContent = theme === 'dark' ? '☀ 切到浅色' : '☾ 切到深色';
    btn.setAttribute('aria-label', btn.textContent);
}

/* ---------- 初始化 ---------- */
// 注意：防闪烁的关键一步在 02-theme.html 的 <head> 内联脚本里，
// 那里在 CSS 生效前就把 data-theme 设好了，这里只负责同步按钮文案。
updateToggleText(getTheme());

/* ---------- 绑定切换 ---------- */
const toggle = document.getElementById('themeToggle');
if (toggle) {
    toggle.addEventListener('click', () => {
        const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
        applyTheme(next);
    });
}

/* ---------- 跟随系统变化 ---------- */
// 用户没手动选过时，系统切换深浅色，页面要跟着走
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
    if (localStorage.getItem(THEME_KEY)) return;   // 用户已手动选过，不覆盖
    applyTheme(event.matches ? 'dark' : 'light');
});
