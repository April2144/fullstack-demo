// ===== 对应笔记 2.3 JavaScript 核心语法 =====
// 打开浏览器开发者工具 → Console，能看到每一段打印结果。
// 这一段不操作页面，只演示语言本身。

/* ---------- 1. 变量：优先 const，需要重新赋值才用 let ---------- */
const courseName = '全栈开发：从 0 到上线';
let readCount = 3;
readCount = readCount + 1; // let 才能重新赋值
console.log('[1] 变量', { courseName, readCount });

/* ---------- 2. 基本类型 ---------- */
const sample = {
    string: '文本',
    number: 42,
    boolean: true,
    nullValue: null,
    undefinedValue: undefined,
    array: [1, 2, 3],
    object: { level: 'basic' },
};
console.log('[2] 类型', sample);

/* 判断类型：typeof 对 null 会返回 'object'，这是历史遗留问题 */
console.log('[2] typeof null =', typeof null); // 'object'
console.log('[2] Array.isArray([]) =', Array.isArray([])); // true

/* ---------- 3. 模板字符串 ---------- */
const note = { id: '2.3', title: 'JavaScript 核心语法', minutes: 18 };
console.log('[3] 模板字符串', `笔记 ${note.id}：${note.title}（约 ${note.minutes} 分钟）`);

/* ---------- 4. 函数：声明式 与 箭头函数 ---------- */
function formatMinutes(min) {
    return `${min} 分钟`;
}

const formatMinutesArrow = (min) => `${min} 分钟`;

console.log('[4] 函数', formatMinutes(18), formatMinutesArrow(18));

/* 默认参数：调用时不传就用默认值 */
const greet = (name = '同学') => `你好，${name}`;
console.log('[4] 默认参数', greet(), greet('禾安'));

/* ---------- 5. 数组方法：map / filter / reduce 是最常用的三个 ---------- */
const notes = [
    { id: '2.1', title: 'HTML 结构', done: true },
    { id: '2.2', title: 'CSS 基础', done: true },
    { id: '2.3', title: 'JS 语法', done: false },
];

const titles = notes.map((n) => n.title);              // 取字段
const finished = notes.filter((n) => n.done);          // 筛选
const doneCount = notes.reduce((sum, n) => sum + (n.done ? 1 : 0), 0); // 汇总

console.log('[5] map', titles);
console.log('[5] filter', finished.map((n) => n.id));
console.log('[5] reduce', `${doneCount}/${notes.length} 已完成`);

/* ---------- 6. 对象与解构 ---------- */
const { title, minutes = 0 } = note;   // 解构 + 默认值
console.log('[6] 解构', title, minutes);

const merged = { ...note, minutes: 20 }; // 展开运算符做浅拷贝
console.log('[6] 展开', merged);

/* ---------- 7. 条件与可选链 ---------- */
const user = { profile: { nickname: 'April' } };
// 可选链：中间某一层是 null/undefined 时不会报错，只返回 undefined
console.log('[7] 可选链', user?.profile?.nickname, user?.account?.email);

/* ---------- 8. 异步：Promise 与 async/await ---------- */
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function loadDemo() {
    console.log('[8] 开始等待');
    await wait(300);
    console.log('[8] 300ms 后继续执行');
}

loadDemo();

// 提示：真正的网络请求在 05-fetch.js 里演示

/* ---------- 9. 运算符 ---------- */
const a = 7;
const b = 2;
console.log('[9] 算术', a + b, a - b, a * b, a / b, a % b); // 除法不会自动取整

// === 比 == 严格：前者比类型，后者会偷偷转换
console.log('[9] === 与 ==', 1 === '1', 1 == '1');

console.log('[9] 逻辑', true && false, true || false, !true);

// ?? 只在左边是 null / undefined 时才用右边
console.log('[9] 空值合并 ??', 0 ?? '默认值', null ?? '默认值');

// || 把 0、''、false 也当成「没有值」，这是最常见的误用
console.log('[9] || 的区别', 0 || '默认值', 0 ?? '默认值');

/* ---------- 10. 流程控制 ---------- */
const score = 82;
if (score >= 90) {
    console.log('[10] if', '优秀');
} else if (score >= 60) {
    console.log('[10] if', '及格');
} else {
    console.log('[10] if', '不及格');
}

// 三元运算符适合「二选一赋值」，嵌套超过两层就该改回 if
const level = score >= 90 ? 'A' : (score >= 60 ? 'B' : 'C');
console.log('[10] 三元', level);

const status = 'done';
switch (status) {
    case 'todo':
        console.log('[10] switch', '待办');
        break;                            // 漏写 break 会继续往下执行
    case 'done':
        console.log('[10] switch', '已完成');
        break;
    default:
        console.log('[10] switch', '未知状态');
}

for (let i = 1; i <= 3; i += 1) {
    console.log('[10] for', i);
}

// for...of 直接拿值，比 for 循环少写一个下标
for (const name of ['HTML', 'CSS', 'JS']) {
    console.log('[10] for...of', name);
}

/* ---------- 11. 字符串常用方法 ---------- */
const raw = '  Hello World  ';
console.log('[11] trim', `"${raw.trim()}"`);                 // 去首尾空白
console.log('[11] toLowerCase', raw.trim().toLowerCase());   // 转小写（搜索时常用）
console.log('[11] includes', raw.includes('World'));         // 是否包含，返回布尔值
console.log('[11] slice', raw.trim().slice(0, 5));           // 截取 [0, 5)
console.log('[11] split', 'a,b,c'.split(','));               // 切成数组
console.log('[11] replace', 'hello world'.replace('world', 'JS')); // 只替换第一处

/* ---------- 12. 错误处理 ---------- */
// 主动抛错比返回 null 更清楚：调用方必须处理，不会悄悄拿到一个错值
function parseAge(input) {
    const age = Number(input);
    if (Number.isNaN(age)) {
        throw new Error(`不是合法数字：${input}`);
    }
    return age;
}

try {
    console.log('[12] try', parseAge('18'));
    console.log('[12] try', parseAge('abc'));   // 这一行抛错，try 里后面的代码不再执行
} catch (error) {
    console.warn('[12] catch', error.message);  // 接住错误，避免整页脚本中断
} finally {
    console.log('[12] finally', '无论成功失败都会执行');
}
