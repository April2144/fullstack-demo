/* ===== 对应笔记 7.5 前后端联调实战 ===== */

(function () {
    'use strict';

    // 同源：页面由 FastAPI 自己托管，用相对路径即可。
    // 如果把本页放到 8080 的静态服务上，这里要改成 'http://127.0.0.1:8000'，才会触发跨域
    var API_BASE = '';

    var els = {
        list: document.getElementById('noteList'),
        listHint: document.getElementById('listHint'),
        filter: document.getElementById('filter'),
        reload: document.getElementById('reloadBtn'),
        title: document.getElementById('title'),
        status: document.getElementById('statusInput'),
        create: document.getElementById('createBtn'),
        formHint: document.getElementById('formHint')
    };

    if (!els.list) {
        return;
    }

    /**
     * 统一请求入口：把「HTTP 错误」和「业务错误」都收敛成一个 Error。
     * 调用方只需要 catch 一次，不用每处都判断 res.ok。
     */
    function request(path, options) {
        var init = options || {};
        init.headers = init.headers || {};

        if (init.body) {
            init.headers['Content-Type'] = 'application/json';
            init.body = JSON.stringify(init.body);
        }

        return fetch(API_BASE + path, init).then(function (res) {
            // 204：删除成功，没有响应体，不能调 res.json()
            if (res.status === 204) {
                return null;
            }

            return res.json().then(function (payload) {
                if (!res.ok) {
                    var error = new Error(payload.message || ('HTTP ' + res.status));
                    error.status = res.status;
                    error.payload = payload;
                    throw error;
                }
                return payload.data;
            });
        });
    }

    function setHint(el, text, isError) {
        el.textContent = text;
        el.className = isError ? 'hint error' : 'hint';
    }

    /** 用 DOM API 逐个节点创建，标题一律走 textContent —— 用户输入绝不拼进 innerHTML */
    function buildItem(note) {
        var li = document.createElement('li');

        var main = document.createElement('div');
        main.className = 'note-main';

        var title = document.createElement('div');
        title.className = 'note-title';
        title.textContent = note.title;

        var tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = note.status === 'published' ? '已发布' : '草稿';
        title.appendChild(tag);

        var meta = document.createElement('div');
        meta.className = 'note-meta';
        meta.textContent = '#' + note.id + ' · 创建于 ' + note.created_at.replace('T', ' ');

        main.appendChild(title);
        main.appendChild(meta);

        var del = document.createElement('button');
        del.type = 'button';
        del.className = 'ghost';
        del.textContent = '删除';
        del.addEventListener('click', function () {
            removeNote(note.id, del);
        });

        li.appendChild(main);
        li.appendChild(del);
        return li;
    }

    function renderNotes(data) {
        els.list.innerHTML = '';
        data.items.forEach(function (note) {
            els.list.appendChild(buildItem(note));
        });

        if (data.items.length === 0) {
            setHint(els.listHint, '没有符合条件的笔记');
            return;
        }
        setHint(els.listHint, '共 ' + data.total + ' 条，本页 ' + data.items.length + ' 条');
    }

    function loadNotes() {
        setHint(els.listHint, '加载中…');
        var query = els.filter.value ? '?status=' + encodeURIComponent(els.filter.value) : '';

        request('/api/notes' + query).then(renderNotes).catch(function (error) {
            setHint(els.listHint, '加载失败：' + error.message, true);
        });
    }

    function createNote() {
        els.create.disabled = true;
        setHint(els.formHint, '提交中…');

        request('/api/notes', {
            method: 'POST',
            body: {
                title: els.title.value.trim(),
                status: els.status.value
            }
        }).then(function (note) {
            els.title.value = '';
            setHint(els.formHint, '已创建 #' + note.id);
            loadNotes();
        }).catch(function (error) {
            // 422 时把字段级错误也打出来，方便对照 7.2 的统一错误格式
            var detail = error.status === 422 && error.payload && error.payload.data
                ? '（' + error.payload.data.errors[0].msg + '）'
                : '';
            setHint(els.formHint, '创建失败：' + error.message + detail, true);
        }).then(function () {
            els.create.disabled = false;
        });
    }

    function removeNote(id, button) {
        button.disabled = true;

        request('/api/notes/' + id, { method: 'DELETE' }).then(function () {
            loadNotes();
        }).catch(function (error) {
            button.disabled = false;
            setHint(els.listHint, '删除失败：' + error.message, true);
        });
    }

    els.create.addEventListener('click', createNote);
    els.reload.addEventListener('click', loadNotes);
    els.filter.addEventListener('change', loadNotes);

    loadNotes();
})();
