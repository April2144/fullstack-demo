// ===== 对应笔记 3.3 表单与用户输入（二）校验与提交 =====
// 职责：只处理这个表单的校验、提示与提交，不碰页面其它区块。

const form = document.getElementById('profileForm');
const result = document.getElementById('formResult');

/* ---------- 1. 校验规则表：字段 id → 校验函数 ---------- */
// 返回空字符串表示通过，返回文案表示不通过。
// 这样新增字段只要往表里加一行，校验逻辑不用改。
const rules = {
    'f-username': (value) => {
        if (!value.trim()) return '请填写用户名';
        if (value.trim().length < 3) return '用户名至少 3 个字符';
        return '';
    },
    'f-password': (value) => {
        if (!value) return '请填写密码';
        if (value.length < 8) return '密码至少 8 位';
        return '';
    },
    'f-email': (value) => {
        if (!value.trim()) return '请填写邮箱';
        // 只做格式的粗校验，真正的有效性要靠后端发验证邮件
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '邮箱格式不正确';
        return '';
    },
    'f-age': (value) => {
        if (!value) return '';                       // 选填：不填就跳过
        const age = Number(value);
        if (Number.isNaN(age) || age < 18 || age > 120) return '年龄需在 18 ~ 120 之间';
        return '';
    },
    'f-phone': (value) => {
        if (!value) return '';                       // 选填
        if (!/^1\d{10}$/.test(value)) return '手机号需为 11 位数字，且以 1 开头';
        return '';
    },
    'f-bio': (value) => {
        if (value.length > 120) return '简介不能超过 120 字';
        return '';
    },
};

/* ---------- 2. 错误提示的显示与清除 ---------- */
function getErrorEl(fieldId) {
    return document.querySelector(`[data-error-for="${fieldId}"]`);
}

function setError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorEl = getErrorEl(fieldId);
    if (!field || !errorEl) return;

    errorEl.textContent = message;
    // 用 class 控制红框，不写内联样式，换主题时样式仍然统一
    field.classList.toggle('is-invalid', Boolean(message));
    // 无障碍：让读屏软件知道这个框当前是无效状态
    message ? field.setAttribute('aria-invalid', 'true') : field.removeAttribute('aria-invalid');
}

/** 校验单个字段，返回是否通过 */
function validateField(fieldId) {
    const rule = rules[fieldId];
    if (!rule) return true;

    const field = document.getElementById(fieldId);
    const message = rule(field.value);
    setError(fieldId, message);
    return !message;
}

/* ---------- 3. 失焦校验：离开输入框时才报错，不打断输入 ---------- */
Object.keys(rules).forEach((fieldId) => {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.addEventListener('blur', () => validateField(fieldId));

    // 已经有错误提示的字段，边改边复验；没错的字段不打扰
    field.addEventListener('input', () => {
        if (field.classList.contains('is-invalid')) validateField(fieldId);
    });
});

/* ---------- 4. 字符计数 ---------- */
const bio = document.getElementById('f-bio');
const bioCounter = document.getElementById('bioCounter');

bio.addEventListener('input', () => {
    bioCounter.textContent = `${bio.value.length} / 120`;
    // 接近上限时变色提醒，属于「实时反馈」，不是校验
    bioCounter.classList.toggle('hint-ok', bio.value.length >= 100 && bio.value.length <= 120);
});

/* ---------- 5. 密码显示切换 ---------- */
const pwd = document.getElementById('f-password');
const showPwd = document.getElementById('f-showPwd');

showPwd.addEventListener('change', () => {
    pwd.type = showPwd.checked ? 'text' : 'password';
});

/* ---------- 6. 提交：先全校验，再收集数据 ---------- */
form.addEventListener('submit', (event) => {
    event.preventDefault();              // 阻止整页刷新

    // every 会短路：发现第一个不通过的字段就停下，但这里需要全部标红，
    // 所以先 map 全部校验，再用 every 判断结果
    const results = Object.keys(rules).map((fieldId) => validateField(fieldId));
    const allPassed = results.every(Boolean);

    if (!allPassed) {
        // 把焦点移到第一个出错的字段，用户不用自己找
        const firstInvalid = form.querySelector('.is-invalid');
        if (firstInvalid) firstInvalid.focus();

        showResult('请先修正标红的字段', true);
        return;
    }

    // FormData 会自动收集 name 属性；同名的复选/单选要用 getAll
    const data = new FormData(form);
    const payload = {
        username: data.get('username'),
        email: data.get('email'),
        age: data.get('age') ? Number(data.get('age')) : null,
        phone: data.get('phone') || null,
        city: data.get('city') || null,
        bio: data.get('bio'),
        gender: data.get('gender'),
        skills: data.getAll('skills'),       // 多选：getAll 才是数组
        notify: data.get('notify') === 'on', // 未勾选的 checkbox 不会出现在 FormData 里
    };

    // 真实项目这里换成 fetch('/api/profile', { method: 'POST', ... })
    console.log('[3.3] 收集到的表单数据', payload);
    showResult('校验通过，数据已打印到控制台');
    form.reset();
    bioCounter.textContent = '0 / 120';
});

/* ---------- 7. 重置：把残留的错误状态一起清掉 ---------- */
form.addEventListener('reset', () => {
    Object.keys(rules).forEach((fieldId) => setError(fieldId, ''));
    result.classList.add('is-hidden');
});

/* ---------- 8. 结果提示 ---------- */
function showResult(message, isError = false) {
    result.textContent = message;
    result.classList.remove('is-hidden');
    // 成功用默认绿，失败换成浅红底
    result.style.background = isError ? '#fee2e2' : '';
    result.style.borderColor = isError ? '#fca5a5' : '';
    result.style.color = isError ? '#991b1b' : '';
}
