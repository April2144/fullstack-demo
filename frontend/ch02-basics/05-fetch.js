// ===== 对应笔记 2.5 前后端数据交互初探（fetch） =====
// 读取同目录下的 data/notes.json，把结果渲染到「远程笔记」区块。
// ⚠️ 必须通过 HTTP 打开（python3 -m http.server），
//    直接双击 file:// 打开会被浏览器的同源策略拦截。

const remoteList = document.getElementById('remoteList');
const remoteHint = document.getElementById('remoteHint');

async function loadRemoteNotes() {
    if (!remoteList || !remoteHint) return;

    remoteHint.textContent = '加载中…';

    try {
        // fetch 返回的是 Response 对象，要再调用 json() 解析
        const response = await fetch('data/notes.json');

        // fetch 只有网络失败才 reject；404/500 依然会 resolve
        // 所以必须自己检查 response.ok
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        // 后端返回的结构可能不统一，先兜底成数组
        const notes = Array.isArray(data) ? data : (data.items || []);

        renderNotes(notes);
        remoteHint.textContent = `共 ${notes.length} 条（来自 data/notes.json）`;
    } catch (error) {
        console.error('[2.5] 加载失败', error);
        remoteHint.textContent = '加载失败：请用 HTTP 方式打开本页（见 README）';
    }
}

function renderNotes(notes) {
    remoteList.textContent = '';   // 先清空，避免重复渲染

    if (!notes.length) {
        const empty = document.createElement('li');
        empty.className = 'note-item';
        empty.textContent = '暂无数据';
        remoteList.append(empty);
        return;
    }

    notes.forEach((note) => {
        const li = document.createElement('li');
        li.className = 'note-item';

        const title = document.createElement('span');
        title.className = 'note-text';
        title.textContent = note.title || '(无标题)';

        const meta = document.createElement('span');
        meta.className = 'note-meta';
        meta.textContent = note.chapter || '';

        li.append(title, meta);
        remoteList.append(li);
    });
}

loadRemoteNotes();

/* ---------- 补充 1：POST / PUT / DELETE 怎么写（对应 2.5 五、六） ---------- */
// 本页没有后端，这段只演示「请求怎么构造」并打印出来，不实际发送。
// 真正发送时把返回的对象丢给 fetch 即可。
function buildWriteRequest(method, url, body) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' },   // 发 JSON 必须声明，否则后端解析不到
    };

    // DELETE 一般不带请求体，所以这里允许 body 为空
    if (body !== undefined) {
        options.body = JSON.stringify(body);               // 对象要序列化成字符串
    }

    return { url, options };
}

console.log('[2.5] POST   ', buildWriteRequest('POST', '/api/notes', { title: '新笔记' }));
console.log('[2.5] PUT    ', buildWriteRequest('PUT', '/api/notes/1', { title: '改后的标题' }));
console.log('[2.5] DELETE ', buildWriteRequest('DELETE', '/api/notes/1'));

// 实际发送时的写法（这三行是注释，页面不会执行）：
// const res = await fetch(url, options);
// if (!res.ok) throw new Error(`HTTP ${res.status}`);
// const data = res.status === 204 ? null : await res.json();

/* ---------- 补充 2：封装请求函数（对应 2.5 七） ---------- */
// 把「发请求 + 查状态码 + 解析 JSON」收敛到一个函数里，调用处只管拿数据。
async function request(url, options = {}) {
    const response = await fetch(url, options);

    // fetch 只在网络层失败时 reject，404/500 仍然 resolve，必须手动判断
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    // 204 No Content 没有响应体，调 json() 会抛错
    if (response.status === 204) return null;

    return response.json();
}

// 用法示例（与上面的 loadRemoteNotes 等价，只是更短）：
// const data = await request('data/notes.json');
// console.log('[2.5] 封装后的调用结果', data.items.length);

/* ---------- 补充 3：跨域（对应 2.5 九） ---------- */
// 同源策略是浏览器执行的，不是服务器拒绝了你 —— 所以后端日志里可能一条记录都没有。
// 开发期两种解法：后端返回 CORS 头，或前端开发服务器做代理。
// 生产环境通常在 Nginx 里把 /api 反代到后端，让前后端同源。详细见第 7 章 7.3。
