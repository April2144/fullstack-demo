/**
 * 极简构建脚本 —— 对应笔记 4.4 构建与压缩。
 *
 * 它只做三件事，却正好是构建工具的核心：
 *   1. 合并（多个文件 → 一个）
 *   2. 去注释
 *   3. 压空白
 *
 * 为什么不用 Vite / Webpack？
 *   本专题的原则是「零构建依赖」，这里想让你看清构建到底做了什么，
 *   而不是被一堆插件配置挡住。真实项目该用 Vite，它会多做模块解析、
 *   Tree Shaking、内容哈希、sourcemap 等一堆事。
 *
 * 运行：node build.mjs
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const SRC = join(ROOT, 'src');
const DIST = join(ROOT, 'dist');

/* ---------- 1. 压缩工具函数 ---------- */

/** 去掉块注释与整行双斜杠注释 */
function stripComments(code) {
    return code
        .replace(/\/\*[\s\S]*?\*\//g, '')          // 块注释
        .split('\n')
        .filter((line) => !line.trim().startsWith('//'))  // 整行注释
        .join('\n');
}

/**
 * 压空白：去行首尾空白、合并连续空格、删空行。
 * 注意保留换行 —— 直接删掉换行会触发 JS 的自动分号插入（ASI）问题。
 */
function collapseWhitespace(code) {
    return code
        .split('\n')
        .map((line) => line.trim().replace(/[ \t]+/g, ' '))
        .filter((line) => line.length > 0)
        .join('\n');
}

/** 读文件 → 压缩，返回字符串 */
function minify(filePath) {
    const raw = readFileSync(filePath, 'utf-8');
    return { raw, min: collapseWhitespace(stripComments(raw)) };
}

function sizeOf(text) {
    return Buffer.byteLength(text, 'utf-8');
}

function kb(bytes) {
    return `${(bytes / 1024).toFixed(2)} KB`;
}

/* ---------- 2. 执行构建 ---------- */
mkdirSync(DIST, { recursive: true });

// JS：顺序很重要 —— utils.js 提供 formatSize，必须排在 app.js 前
const jsFiles = ['utils.js', 'app.js'];
let rawJsTotal = 0;
const jsParts = jsFiles.map((name) => {
    const { raw, min } = minify(join(SRC, name));
    rawJsTotal += sizeOf(raw);
    console.log(`  合并 ${name.padEnd(12)} ${kb(sizeOf(raw)).padStart(9)} → ${kb(sizeOf(min))}`);
    return min;
});

// 合并后加一行来源标记，方便线上排查「这是哪个版本」
const banner = `/* built ${new Date().toISOString().slice(0, 19)} */\n`;
const bundleJs = banner + jsParts.join('\n');
writeFileSync(join(DIST, 'bundle.min.js'), bundleJs, 'utf-8');

// CSS：只有一份，同样去注释压空白
const css = minify(join(SRC, 'style.css'));
const bundleCss = css.min;
writeFileSync(join(DIST, 'bundle.min.css'), bundleCss, 'utf-8');

/* ---------- 3. 体积对比 ---------- */
const rawTotal = rawJsTotal + sizeOf(css.raw);
const minTotal = sizeOf(bundleJs) + sizeOf(bundleCss);
const saved = (100 - (minTotal / rawTotal) * 100).toFixed(1);

console.log('');
console.log('构建完成');
console.log(`  源文件合计   ${kb(rawTotal)}`);
console.log(`  产物合计     ${kb(minTotal)}`);
console.log(`  减少         ${saved}%`);
console.log('');
console.log(`产物已写入  ${DIST}/bundle.min.js`);
console.log(`            ${DIST}/bundle.min.css`);
console.log('（体积用字节数统计，UTF-8 中文注释占 3 字节，所以压缩收益比纯英文更明显）');
