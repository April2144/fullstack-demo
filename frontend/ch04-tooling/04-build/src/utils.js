/**
 * 字节数转人类可读的大小。
 *
 * 开发阶段代码写清楚比写短重要：这些注释、缩进、换行，
 * 构建时会全部去掉，不影响运行时。
 *
 * @param {number} bytes 字节数
 * @returns {string} 例如 "12.3 KB"
 */
function formatSize(bytes) {
    if (bytes < 1024) {
        return bytes + ' B';
    }

    const kb = bytes / 1024;
    if (kb < 1024) {
        return kb.toFixed(1) + ' KB';
    }

    const mb = kb / 1024;
    return mb.toFixed(2) + ' MB';
}

/**
 * 把毫秒数转成 "1.2s" 这样的展示形式。
 * @param {number} ms
 */
function formatDuration(ms) {
    if (ms < 1000) {
        return ms + ' ms';
    }
    return (ms / 1000).toFixed(1) + ' s';
}
