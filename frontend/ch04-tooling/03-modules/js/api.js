// ===== 对应笔记 4.3 代码规范与模块化：接口层 =====
// 约定：所有网络请求都收在这一层。
// 页面逻辑不直接写 fetch，这样接口地址变了只改这里一处。

const DATA_DIR = 'data';   // 相对「文档地址」，不是相对本文件

/**
 * 统一请求函数：负责查状态码、解析 JSON、抛错。
 * @param {string} url
 * @param {RequestInit} options
 */
async function request(url, options = {}) {
    const response = await fetch(url, options);

    // fetch 只在网络层失败时 reject；404 / 500 依然 resolve，必须自己判断
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    if (response.status === 204) return null;

    return response.json();
}

/**
 * 拉取笔记列表。
 * 后端结构可能是 { items: [] } 也可能直接是数组，这里统一成数组再返回，
 * 上层就不用关心后端怎么包的。
 */
export async function fetchNotes() {
    const data = await request(`${DATA_DIR}/notes.json`);
    return Array.isArray(data) ? data : (data.items || []);
}
