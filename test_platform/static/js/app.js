/* =============================================
   test_platform - 自动化测试平台 前端逻辑
   ============================================= */

(function() {
    'use strict';

    // ===== 状态管理 =====
    const STATE = {
        testTree: [],
        isRunning: false,
        selectedKeys: new Set(),
        expandedModules: new Set(),
        expandedClasses: new Set(),
        currentRunId: null,
        eventSource: null,
    };

    // ===== DOM 引用 =====
    const $ = (id) => document.getElementById(id);
    const dom = {
        moduleList: $('moduleList'),
        moduleListMobile: $('moduleListMobile'),
        logOutput: $('logOutput'),
        historyList: $('historyList'),
        statusBadge: $('statusBadge'),
        statusText: $('statusText'),
        statTotal: $('statTotal'),
        statPassed: $('statPassed'),
        statFailed: $('statFailed'),
        statSkipped: $('statSkipped'),
        testCount: $('testCount'),
        progressBar: $('progressBar'),
        progressFill: $('progressFill'),
        btnRun: $('btnRun'),
        btnStop: $('btnStop'),
        btnRefresh: $('btnRefresh'),
        btnClearLog: $('btnClearLog'),
        btnCopyLog: $('btnCopyLog'),
        btnRefreshHistory: $('btnRefreshHistory'),
        btnExpandAll: $('btnExpandAll'),
        btnCollapseAll: $('btnCollapseAll'),
        optParallel: $('optParallel'),
        optRetry: $('optRetry'),
        optVerbose: $('optVerbose'),
    };

    // ===== 工具函数 =====
    function formatTime(ts) {
        const d = new Date(ts * 1000);
        return d.toLocaleTimeString('zh-CN', { hour12: false });
    }

    function formatTimestamp(ts) {
        const d = new Date(ts * 1000);
        return d.toLocaleString('zh-CN', { hour12: false });
    }

    function now() {
        return formatTime(Date.now() / 1000);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ===== 获取选中的测试键 =====
    function collectSelectedKeys() {
        return Array.from(STATE.selectedKeys);
    }

    // ===== 构建额外参数 =====
    function getExtraArgs() {
        const args = [];
        if (dom.optParallel.checked) args.push('-n', 'auto');
        if (dom.optRetry.checked) args.push('--reruns', '1');
        if (!dom.optVerbose.checked) args.push('-q');
        return args;
    }

    // ===== 渲染测试树 =====
    function renderTestTree(tree) {
        const container = dom.moduleList;
        const containerMobile = dom.moduleListMobile;
        container.innerHTML = '';
        containerMobile.innerHTML = '';

        if (!tree || tree.length === 0) {
            container.innerHTML = '<div class="text-center py-4 text-muted">暂无测试用例</div>';
            containerMobile.innerHTML = container.innerHTML;
            return;
        }

        // 统计总数
        let total = 0;
        tree.forEach(m => { total += m.total || 0; });
        dom.testCount.textContent = `共 ${total} 项`;

        // 渲染桌面版
        tree.forEach(mod => renderModule(container, mod, false));

        // 渲染移动版
        tree.forEach(mod => renderModule(containerMobile, mod, true));
    }

    function renderModule(container, mod, isMobile) {
        const div = document.createElement('div');
        div.className = 'module-node';
        div.dataset.key = mod.key;

        // 模块头
        const header = document.createElement('div');
        header.className = 'module-header';
        header.innerHTML = `
            <span class="toggle-icon ${STATE.expandedModules.has(mod.key) ? 'expanded' : ''}">
                <i class="fas fa-chevron-right"></i>
            </span>
            <input type="checkbox" ${isModuleAllSelected(mod) ? 'checked' : ''}>
            <span class="module-icon">${mod.icon || '📦'}</span>
            <span class="module-name">${escapeHtml(mod.label || mod.module_name)}</span>
            <span class="badge bg-secondary module-badge">${mod.total || 0}</span>
        `;

        // 展开/折叠
        header.querySelector('.toggle-icon').addEventListener('click', (e) => {
            e.stopPropagation();
            toggleModule(mod.key, container);
        });

        // 全选/取消
        const cb = header.querySelector('input[type="checkbox"]');
        cb.addEventListener('change', () => {
            toggleModuleSelection(mod, cb.checked, container);
        });

        div.appendChild(header);

        // 子节点容器
        const children = document.createElement('div');
        children.className = 'module-children';
        children.style.display = STATE.expandedModules.has(mod.key) ? 'block' : 'none';

        (mod.children || []).forEach(cls => {
            const clsDiv = document.createElement('div');
            clsDiv.className = 'class-node';
            clsDiv.dataset.key = cls.key;

            const clsHeader = document.createElement('div');
            clsHeader.className = 'class-header';
            clsHeader.innerHTML = `
                <span class="toggle-icon ${STATE.expandedClasses.has(cls.key) ? 'expanded' : ''}">
                    <i class="fas fa-chevron-right"></i>
                </span>
                <input type="checkbox" ${isClassAllSelected(cls) ? 'checked' : ''}>
                <span class="class-name">${escapeHtml(cls.label)}</span>
                <span class="class-count">${cls.children ? cls.children.length : 0}</span>
            `;

            const cbCls = clsHeader.querySelector('input[type="checkbox"]');
            cbCls.addEventListener('change', () => {
                toggleClassSelection(cls, cbCls.checked, container);
            });

            clsHeader.querySelector('.toggle-icon').addEventListener('click', (e) => {
                e.stopPropagation();
                toggleClass(cls.key, container);
            });

            clsDiv.appendChild(clsHeader);

            // 方法列表
            const methodContainer = document.createElement('div');
            methodContainer.className = 'method-children';
            methodContainer.style.display = STATE.expandedClasses.has(cls.key) ? 'block' : 'none';

            (cls.children || []).forEach(m => {
                const mDiv = document.createElement('div');
                mDiv.className = 'method-node';
                mDiv.innerHTML = `
                    <input type="checkbox" ${STATE.selectedKeys.has(m.key) ? 'checked' : ''}>
                    <span class="method-name" title="${escapeHtml(m.doc || m.label)}">
                        ${escapeHtml(m.label)}
                    </span>
                    <span class="method-status status-pending"></span>
                `;

                const cbM = mDiv.querySelector('input[type="checkbox"]');
                cbM.addEventListener('change', () => {
                    if (cbM.checked) {
                        STATE.selectedKeys.add(m.key);
                    } else {
                        STATE.selectedKeys.delete(m.key);
                    }
                    updateCheckboxStates(container);
                });

                // 点击方法名查看详细信息
                mDiv.querySelector('.method-name').addEventListener('click', () => {
                    if (m.doc) {
                        addLog('info', `📋 ${m.label}: ${m.doc}`);
                    }
                });

                methodContainer.appendChild(mDiv);
            });

            clsDiv.appendChild(methodContainer);
            children.appendChild(clsDiv);
        });

        div.appendChild(children);
        container.appendChild(div);
    }

    function isModuleAllSelected(mod) {
        if (!mod.children) return true;
        for (const cls of mod.children) {
            if (!isClassAllSelected(cls)) return false;
        }
        return true;
    }

    function isClassAllSelected(cls) {
        if (!cls.children) return true;
        for (const m of cls.children) {
            if (!STATE.selectedKeys.has(m.key)) return false;
        }
        return true;
    }

    function toggleModule(modKey, container) {
        const expanded = STATE.expandedModules.has(modKey);
        if (expanded) {
            STATE.expandedModules.delete(modKey);
        } else {
            STATE.expandedModules.add(modKey);
        }
        // 重新渲染整个树
        refreshTree();
    }

    function toggleClass(clsKey, container) {
        const expanded = STATE.expandedClasses.has(clsKey);
        if (expanded) {
            STATE.expandedClasses.delete(clsKey);
        } else {
            STATE.expandedClasses.add(clsKey);
        }
        refreshTree();
    }

    function toggleModuleSelection(mod, selected, container) {
        (mod.children || []).forEach(cls => {
            (cls.children || []).forEach(m => {
                if (selected) {
                    STATE.selectedKeys.add(m.key);
                } else {
                    STATE.selectedKeys.delete(m.key);
                }
            });
        });
        refreshTree();
    }

    function toggleClassSelection(cls, selected, container) {
        (cls.children || []).forEach(m => {
            if (selected) {
                STATE.selectedKeys.add(m.key);
            } else {
                STATE.selectedKeys.delete(m.key);
            }
        });
        refreshTree();
    }

    function updateCheckboxStates(container) {
        // 更新所有复选框状态
        const cbs = container.querySelectorAll('.module-header input[type="checkbox"]');
        const modules = STATE.testTree;
        cbs.forEach((cb, i) => {
            if (i < modules.length) {
                cb.checked = isModuleAllSelected(modules[i]);
            }
        });

        container.querySelectorAll('.class-header input[type="checkbox"]').forEach(cb => {
            const clsKey = cb.closest('.class-node')?.dataset?.key;
            if (clsKey) {
                for (const mod of modules) {
                    for (const cls of (mod.children || [])) {
                        if (cls.key === clsKey) {
                            cb.checked = isClassAllSelected(cls);
                            break;
                        }
                    }
                }
            }
        });
    }

    function refreshTree() {
        renderTestTree(STATE.testTree);
    }

    // ===== 加载测试用例 =====
    function loadTests() {
        dom.moduleList.innerHTML = '<div class="text-center py-4"><div class="spinner-border spinner-border-sm text-primary" role="status"></div><span class="ms-2">加载测试用例...</span></div>';
        dom.testCount.textContent = '加载中...';

        fetch('/api/tests')
            .then(r => r.json())
            .then(res => {
                if (res.code === 200 && res.data) {
                    STATE.testTree = res.data;
                    // 默认全选
                    STATE.selectedKeys.clear();
                    res.data.forEach(mod => {
                        (mod.children || []).forEach(cls => {
                            (cls.children || []).forEach(m => {
                                STATE.selectedKeys.add(m.key);
                            });
                        });
                    });
                    renderTestTree(res.data);
                    updateStats({ total: STATE.selectedKeys.size });
                }
            })
            .catch(err => {
                dom.moduleList.innerHTML = `<div class="text-center py-4 text-danger">
                    <i class="fas fa-exclamation-triangle"></i> 加载失败: ${err.message}
                </div>`;
                dom.testCount.textContent = '加载失败';
            });
    }

    // ===== 更新统计 =====
    function updateStats(summary) {
        if (!summary) return;
        dom.statTotal.textContent = summary.total ?? '-';
        dom.statPassed.textContent = summary.passed ?? '-';
        dom.statFailed.textContent = summary.failed ?? '-';
        dom.statSkipped.textContent = summary.skipped ?? '-';
    }

    // ===== 日志系统 =====
    function addLog(level, message) {
        const log = dom.logOutput;
        const isAtBottom = log.scrollHeight - log.scrollTop - log.clientHeight < 30;

        // 清除占位
        const placeholder = log.querySelector('.text-muted');
        if (placeholder && log.children.length === 1) {
            log.innerHTML = '';
        }

        const line = document.createElement('div');
        line.className = 'log-line';

        const time = document.createElement('span');
        time.className = 'log-time';
        time.textContent = now();

        const msg = document.createElement('span');
        msg.className = `log-${level}`;
        msg.textContent = message;

        line.appendChild(time);
        line.appendChild(msg);
        log.appendChild(line);

        if (isAtBottom) {
            log.scrollTop = log.scrollHeight;
        }
    }

    function clearLog() {
        dom.logOutput.innerHTML = '<div class="log-line text-muted"><span class="log-time">--:--:--</span><span>等待操作...</span></div>';
    }

    function copyLog() {
        const text = Array.from(dom.logOutput.querySelectorAll('.log-line'))
            .map(line => line.textContent)
            .join('\n');
        navigator.clipboard.writeText(text).then(() => {
            addLog('success', '📋 日志已复制到剪贴板');
        }).catch(() => {
            addLog('error', '❌ 复制失败');
        });
    }

    // ===== SSE 实时流 =====
    function connectSSE() {
        if (STATE.eventSource) {
            STATE.eventSource.close();
        }

        STATE.eventSource = new EventSource('/stream');

        STATE.eventSource.onopen = () => {
            addLog('info', '🔗 已连接实时事件流');
        };

        STATE.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'connected') {
                    addLog('info', `🟢 ${data.message}`);
                } else if (data.type === 'log') {
                    addLog(data.level, data.message);
                } else if (data.type === 'result') {
                    handleResult(data);
                } else if (data.type === 'done') {
                    addLog('info', '🏁 事件流结束');
                    setRunningState(false);
                    STATE.eventSource.close();
                    STATE.eventSource = null;
                }
            } catch (e) {
                // ignore parse errors
            }
        };

        STATE.eventSource.onerror = () => {
            // 连接错误可能是流结束，忽略
        };
    }

    // ===== 处理测试结果 =====
    function handleResult(data) {
        const summary = data.summary || {};
        updateStats(summary);

        if (data.exit_code === 0) {
            dom.statusBadge.textContent = '全部通过';
            dom.statusBadge.className = 'badge bg-success ms-2';
        } else if (data.exit_code === 1) {
            dom.statusBadge.textContent = '有失败';
            dom.statusBadge.className = 'badge bg-danger ms-2';
        } else {
            dom.statusBadge.textContent = `错误 (${data.exit_code})`;
            dom.statusBadge.className = 'badge bg-warning ms-2';
        }

        // 高亮测试用例状态（如果有 node_id 信息）
        if (summary.failures && summary.failures.length > 0) {
            const failedNodes = new Set(summary.failures.map(f => f.node_id));
            addLog('error', `❌ ${summary.failures.length} 个测试失败:`);
            summary.failures.forEach(f => {
                addLog('error', `   - ${f.node_id}`);
            });
        }

        const duration = data.duration ? (data.duration).toFixed(1) : '?';
        addLog('info', `⏱️ 总耗时: ${duration}秒`);
    }

    // ===== 设置运行状态 =====
    function setRunningState(running) {
        STATE.isRunning = running;
        dom.btnRun.disabled = running;
        dom.btnStop.disabled = !running;
        dom.statusText.textContent = running ? '运行中...' : '就绪';
        dom.statusBadge.textContent = running ? '运行中' : '就绪';
        dom.statusBadge.className = running
            ? 'badge bg-warning ms-2 running-pulse'
            : 'badge bg-light text-primary ms-2';

        dom.progressBar.style.display = running ? 'block' : 'none';
        if (running) {
            dom.progressFill.style.width = '60%';
        } else {
            dom.progressFill.style.width = '100%';
            setTimeout(() => {
                dom.progressBar.style.display = 'none';
                dom.progressFill.style.width = '0%';
            }, 1000);
        }
    }

    // ===== 运行测试 =====
    function runTests() {
        if (STATE.isRunning) return;

        const selected = collectSelectedKeys();
        if (selected.length === 0) {
            addLog('warning', '⚠️ 请至少选择一个测试用例');
            return;
        }

        setRunningState(true);
        clearLog();
        addLog('info', `🚀 开始运行 ${selected.length} 个测试用例...`);
        updateStats({ total: selected.length, passed: 0, failed: 0, skipped: 0 });

        // 先连接到 SSE
        connectSSE();

        fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                selected: selected,
                extra_args: getExtraArgs(),
            }),
        })
        .then(r => r.json())
        .then(res => {
            if (res.code === 200) {
                addLog('success', `✅ ${res.message}`);
            } else {
                addLog('error', `❌ ${res.message}`);
                setRunningState(false);
            }
        })
        .catch(err => {
            addLog('error', `❌ 启动失败: ${err.message}`);
            setRunningState(false);
        });
    }

    // ===== 停止测试 =====
    function stopTests() {
        if (!STATE.isRunning) return;

        fetch('/api/stop', { method: 'POST' })
            .then(r => r.json())
            .then(res => {
                addLog('warning', `⏹️ ${res.message}`);
                setRunningState(false);
            })
            .catch(err => {
                addLog('error', `❌ 停止失败: ${err.message}`);
            });
    }

    // ===== 加载历史记录 =====
    function loadHistory() {
        dom.historyList.innerHTML = '<div class="text-center py-4"><div class="spinner-border spinner-border-sm text-primary" role="status"></div><span class="ms-2">加载历史...</span></div>';

        fetch('/api/history')
            .then(r => r.json())
            .then(res => {
                if (res.code === 200 && res.data && res.data.length > 0) {
                    renderHistory(res.data);
                } else {
                    dom.historyList.innerHTML = `<div class="text-center py-4 text-muted">
                        <i class="fas fa-inbox fa-2x mb-2 d-block"></i>
                        暂无历史记录
                    </div>`;
                }
            })
            .catch(err => {
                dom.historyList.innerHTML = `<div class="text-center py-4 text-danger">
                    <i class="fas fa-exclamation-triangle"></i> 加载失败
                </div>`;
            });
    }

    function renderHistory(records) {
        dom.historyList.innerHTML = '';
        records.forEach(r => {
            const div = document.createElement('div');
            div.className = 'history-item fade-in';
            const statusClass = r.failed > 0 ? 'text-danger' : 'text-success';
            div.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span class="h-result ${statusClass}">
                        ${r.failed > 0 ? '❌' : '✅'} 共 ${r.total} 项
                    </span>
                    <span class="h-time">${formatTimestamp(r.time)}</span>
                </div>
                <div class="h-detail mt-1">
                    通过: ${r.passed} | 失败: ${r.failed} | 跳过: ${r.skipped} | 耗时: ${r.duration.toFixed(1)}s
                </div>
            `;

            div.addEventListener('click', () => {
                // 点击查看详情
                fetch(`/api/report/${r.file}`)
                    .then(r => r.json())
                    .then(res => {
                        if (res.code === 200) {
                            showReportDetail(res.data);
                        }
                    })
                    .catch(() => {});
            });

            dom.historyList.appendChild(div);
        });
    }

    function showReportDetail(report) {
        clearLog();
        addLog('info', `📊 报告详情 - ${report.metadata?.created_at || ''}`);

        const summary = report.summary || {};
        addLog('info', `总计: ${summary.total} | 通过: ${summary.passed} | 失败: ${summary.failed} | 跳过: ${summary.skipped}`);

        const tests = report.tests || [];
        tests.forEach(t => {
            const outcome = t.outcome || 'unknown';
            const icon = outcome === 'passed' ? '✅' : outcome === 'failed' ? '❌' : '⏭️';
            const duration = t.duration ? `(${t.duration.toFixed(2)}s)` : '';
            addLog(outcome === 'passed' ? 'success' : outcome === 'failed' ? 'error' : 'info',
                `${icon} ${t.node_id} ${duration}`);
        });
    }

    // ===== 展开/折叠全部 =====
    function expandAll() {
        STATE.testTree.forEach(mod => {
            STATE.expandedModules.add(mod.key);
            (mod.children || []).forEach(cls => {
                STATE.expandedClasses.add(cls.key);
            });
        });
        refreshTree();
    }

    function collapseAll() {
        STATE.expandedModules.clear();
        STATE.expandedClasses.clear();
        refreshTree();
    }

    // ===== 标签页切换 =====
    function setupTabs() {
        document.querySelectorAll('[data-tab]').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                document.querySelectorAll('[data-tab]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active', 'show'));
                const pane = document.getElementById(`tab${tab.charAt(0).toUpperCase() + tab.slice(1)}`);
                if (pane) {
                    pane.classList.add('active', 'show');
                }

                if (tab === 'history') {
                    loadHistory();
                }
            });
        });
    }

    // ===== 初始化 =====
    function init() {
        loadTests();
        loadHistory();
        setupTabs();

        // 事件绑定
        dom.btnRun.addEventListener('click', runTests);
        dom.btnStop.addEventListener('click', stopTests);
        dom.btnRefresh.addEventListener('click', loadTests);
        dom.btnClearLog.addEventListener('click', clearLog);
        dom.btnCopyLog.addEventListener('click', copyLog);
        dom.btnRefreshHistory.addEventListener('click', loadHistory);
        dom.btnExpandAll.addEventListener('click', expandAll);
        dom.btnCollapseAll.addEventListener('click', collapseAll);

        // 回车快捷键
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                runTests();
            }
        });

        addLog('info', '🟢 测试平台已就绪 - 选择测试用例后点击"运行"');
        addLog('info', '⌨️ 快捷键: Ctrl+Enter 运行测试');
    }

    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();