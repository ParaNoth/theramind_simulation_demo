// 全局变量
let isInitialized = false;
let currentDebugInfo = null;
let allDialogs = [];
let currentTherapy = null;
let viewingSessionIndex = null; // 当前查看的会话索引，null 表示查看当前会话
let currentLang = localStorage.getItem('ui_language') || 'zh'; // 当前界面语言
let currentConfigPath = null; // 当前配置文件路径

// DOM 元素
const initBtn = document.getElementById('initBtn');
const loadBtn = document.getElementById('loadBtn');
const debugToggle = document.getElementById('debugToggle');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const currentSessionContent = document.getElementById('currentSessionContent');
const sessionsContent = document.getElementById('sessionsContent');
const debugPanel = document.getElementById('debugPanel');
const debugContent = document.getElementById('debugContent');
const loadModal = document.getElementById('loadModal');
const fileList = document.getElementById('fileList');
const initModal = document.getElementById('initModal');
const initConfigSelect = document.getElementById('initConfigSelect');
const loadConfigSelect = document.getElementById('loadConfigSelect');
const confirmInitBtn = document.getElementById('confirmInitBtn');
const sessionTitle = document.getElementById('sessionTitle');
const backToCurrentBtn = document.getElementById('backToCurrentBtn');
const langToggle = document.getElementById('langToggle');
const configInfo = document.getElementById('configInfo');
const configFileName = document.getElementById('configFileName');

// API 基础 URL
const API_BASE = '';

// 国际化文本
const i18n = {
    zh: {
        newSession: '新建会话',
        loadArchive: '加载存档',
        debugMode: 'Debug 模式',
        currentSession: '当前会话',
        backToCurrent: '回到当前会话',
        pleaseInit: '请先初始化或加载一个会话',
        inputPlaceholder: '请输入您的问题或感受...',
        send: '发送',
        pastSessions: '历史会话',
        noPastSessions: '暂无历史会话',
        debugInfo: 'Debug 信息',
        waitingForDialog: '等待对话开始...',
        selectConfig: '选择配置文件：',
        useDefaultConfig: '使用默认配置',
        confirm: '确认',
        cancel: '取消',
        selectArchiveFile: '选择存档文件',
        loading: '加载中...',
        noFiles: '暂无存档文件',
        loadingFiles: '加载文件列表失败',
        session: '会话',
        unknownTherapy: '未知疗法',
        emptySession: '空会话',
        visitor: '来访者',
        counselor: '咨询师',
        noDialog: '暂无对话记录',
        currentSessionEmpty: '当前会话暂无对话',
        sessionEmpty: '该会话暂无对话',
        sessionNotExist: '会话不存在',
        configFile: '配置文件：'
    },
    en: {
        newSession: 'New Session',
        loadArchive: 'Load Archive',
        debugMode: 'Debug Mode',
        currentSession: 'Current Session',
        backToCurrent: 'Back to Current',
        pleaseInit: 'Please initialize or load a session first',
        inputPlaceholder: 'Please enter your question or feeling...',
        send: 'Send',
        pastSessions: 'Past Sessions',
        noPastSessions: 'No past sessions',
        debugInfo: 'Debug Information',
        waitingForDialog: 'Waiting for dialog to start...',
        selectConfig: 'Select Config File:',
        useDefaultConfig: 'Use Default Config',
        confirm: 'Confirm',
        cancel: 'Cancel',
        selectArchiveFile: 'Select Archive File',
        loading: 'Loading...',
        noFiles: 'No archive files',
        loadingFiles: 'Failed to load file list',
        session: 'Session',
        unknownTherapy: 'Unknown Therapy',
        emptySession: 'Empty Session',
        visitor: 'Visitor',
        counselor: 'Counselor',
        noDialog: 'No dialog records',
        currentSessionEmpty: 'Current session has no dialog',
        sessionEmpty: 'This session has no dialog',
        sessionNotExist: 'Session does not exist',
        configFile: 'Config File:'
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 检查当前状态
    checkStatus();
    
    // 绑定事件
    initBtn.addEventListener('click', initNewSession);
    loadBtn.addEventListener('click', showLoadModal);
    sendBtn.addEventListener('click', sendMessage);
    debugToggle.addEventListener('change', toggleDebug);
    backToCurrentBtn.addEventListener('click', backToCurrentSession);
    langToggle.addEventListener('click', toggleLanguage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 初始化语言
    updateLanguage();
    
    // 模态框关闭
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modalId = e.target.getAttribute('data-modal');
            if (modalId) {
                document.getElementById(modalId).style.display = 'none';
            }
        });
    });
    
    // 取消按钮
    document.querySelectorAll('[data-modal]').forEach(btn => {
        if (btn.classList.contains('btn')) {
            btn.addEventListener('click', (e) => {
                const modalId = e.target.getAttribute('data-modal');
                if (modalId) {
                    document.getElementById(modalId).style.display = 'none';
                }
            });
        }
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === loadModal) {
            loadModal.style.display = 'none';
        }
        if (e.target === initModal) {
            initModal.style.display = 'none';
        }
    });
    
    // 确认新建会话
    confirmInitBtn.addEventListener('click', confirmInitSession);
    
    // 加载配置文件列表
    loadConfigList();
    
    // 初始化语言
    updateLanguage();
});

// 切换语言
function toggleLanguage() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    localStorage.setItem('ui_language', currentLang);
    updateLanguage();
    // 更新 UI 以刷新动态内容
    if (isInitialized) {
        updateUI();
    }
}

// 更新界面语言
function updateLanguage() {
    const texts = i18n[currentLang];
    
    // 更新所有带有 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (texts[key]) {
            el.textContent = texts[key];
        }
    });
    
    // 更新 placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (texts[key]) {
            el.placeholder = texts[key];
        }
    });
    
    // 更新选项文本
    document.querySelectorAll('option[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (texts[key]) {
            el.textContent = texts[key];
        }
    });
    
    // 更新语言切换按钮文本
    if (langToggle) {
        langToggle.textContent = currentLang === 'zh' ? 'EN' : '中';
    }
    
    // 更新动态内容
    updateDynamicTexts();
}

// 更新动态生成的文本
function updateDynamicTexts() {
    const texts = i18n[currentLang];
    
    // 更新会话标题（如果不在查看历史会话）
    if (viewingSessionIndex === null && sessionTitle) {
        sessionTitle.textContent = texts.currentSession;
    }
    
    // 更新config文件标签
    if (configInfo) {
        const configLabel = configInfo.querySelector('.config-label');
        if (configLabel) {
            configLabel.textContent = texts.configFile;
        }
    }
    
    // 更新空消息
    document.querySelectorAll('.empty-message').forEach(el => {
        if (el.textContent.includes('请先初始化') || el.textContent.includes('Please initialize')) {
            el.textContent = texts.pleaseInit;
        } else if (el.textContent.includes('暂无历史会话') || el.textContent.includes('No past sessions')) {
            el.textContent = texts.noPastSessions;
        } else if (el.textContent.includes('等待对话') || el.textContent.includes('Waiting for dialog')) {
            el.textContent = texts.waitingForDialog;
        } else if (el.textContent.includes('暂无对话记录') || el.textContent.includes('No dialog records')) {
            el.textContent = texts.noDialog;
        } else if (el.textContent.includes('当前会话暂无对话') || el.textContent.includes('Current session has no dialog')) {
            el.textContent = texts.currentSessionEmpty;
        } else if (el.textContent.includes('该会话暂无对话') || el.textContent.includes('This session has no dialog')) {
            el.textContent = texts.sessionEmpty;
        } else if (el.textContent.includes('会话不存在') || el.textContent.includes('Session does not exist')) {
            el.textContent = texts.sessionNotExist;
        }
    });
}

// 更新config文件名称显示
function updateConfigFileName(configPath) {
    if (!configPath) {
        if (configInfo) {
            configInfo.style.display = 'none';
        }
        currentConfigPath = null;
        return;
    }
    
    currentConfigPath = configPath;
    
    // 从路径中提取文件名
    const fileName = configPath.split(/[/\\]/).pop() || configPath;
    
    if (configFileName) {
        configFileName.textContent = fileName;
    }
    
    if (configInfo) {
        configInfo.style.display = 'flex';
    }
}

// 检查状态
async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.success && data.initialized) {
            isInitialized = true;
            allDialogs = data.all_dialogs || [];
            currentTherapy = data.current_therapy || null;
            // 更新config文件名称显示
            if (data.config_path) {
                updateConfigFileName(data.config_path);
            }
            // 页面加载时，自动显示最后一个会话（当前会话）
            if (allDialogs && allDialogs.length > 0) {
                viewingSessionIndex = allDialogs.length - 1; // 显示最后一个会话
            } else {
                viewingSessionIndex = null;
            }
            // 更新 debug 信息以显示当前疗法
            if (currentTherapy) {
                currentDebugInfo = { current_therapy: currentTherapy };
                if (debugToggle.checked) {
                    updateDebugPanel(currentDebugInfo);
                }
            }
            // 确保渲染当前会话的聊天记录
            updateUI();
            sendBtn.disabled = false;
        }
    } catch (error) {
        console.error('检查状态失败:', error);
    }
}

// 显示新建会话模态框
function showInitModal() {
    initModal.style.display = 'block';
}

// 确认新建会话
async function confirmInitSession() {
    const configPath = initConfigSelect.value || null;
    
    try {
        const response = await fetch(`${API_BASE}/api/init`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                config_path: configPath
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            isInitialized = true;
            allDialogs = data.all_dialogs || [];
            currentTherapy = data.current_therapy || null;
            // 更新config文件名称显示
            if (data.config_path) {
                updateConfigFileName(data.config_path);
            }
            // 新建会话后，自动显示最后一个会话（当前会话）
            if (allDialogs && allDialogs.length > 0) {
                viewingSessionIndex = allDialogs.length - 1; // 显示最后一个会话
            } else {
                viewingSessionIndex = null;
            }
            // 更新 debug 信息以显示当前疗法
            if (currentTherapy) {
                currentDebugInfo = { current_therapy: currentTherapy };
                if (debugToggle.checked) {
                    updateDebugPanel(currentDebugInfo);
                }
            }
            updateUI();
            sendBtn.disabled = false;
            initModal.style.display = 'none';
            const texts = i18n[currentLang];
            alert(currentLang === 'zh' ? '新会话已创建！' : 'New session created!');
        } else {
            const texts = i18n[currentLang];
            alert((currentLang === 'zh' ? '初始化失败: ' : 'Initialization failed: ') + data.message);
        }
    } catch (error) {
        console.error('初始化失败:', error);
        const texts = i18n[currentLang];
        alert((currentLang === 'zh' ? '初始化失败: ' : 'Initialization failed: ') + error.message);
    }
}

// 初始化新会话（旧函数，现在显示模态框）
async function initNewSession() {
    showInitModal();
}

// 显示加载模态框
async function showLoadModal() {
    loadModal.style.display = 'block';
    const texts = i18n[currentLang];
    fileList.innerHTML = `<p>${texts.loading}</p>`;
    
    try {
        const response = await fetch(`${API_BASE}/api/list_files`);
        const data = await response.json();
        
        if (data.success) {
            displayFileList(data.files);
        } else {
            const texts = i18n[currentLang];
            fileList.innerHTML = `<p>${texts.loadingFiles}: ${data.message}</p>`;
        }
    } catch (error) {
        const texts = i18n[currentLang];
        fileList.innerHTML = `<p>${texts.loadingFiles}: ${error.message}</p>`;
    }
}

// 加载配置文件列表
async function loadConfigList() {
    try {
        const response = await fetch(`${API_BASE}/api/list_configs`);
        const data = await response.json();
        
        if (data.success) {
            const configs = data.configs || [];
            
            // 更新两个选择框
            [initConfigSelect, loadConfigSelect].forEach(select => {
                // 保留默认选项
                const defaultOption = select.querySelector('option[value=""]');
                select.innerHTML = '';
                if (defaultOption) {
                    select.appendChild(defaultOption);
                }
                
                // 添加配置文件选项
                configs.forEach(config => {
                    const option = document.createElement('option');
                    option.value = config.file_path;
                    option.textContent = config.filename;
                    select.appendChild(option);
                });
            });
        }
    } catch (error) {
        console.error('加载配置文件列表失败:', error);
    }
}

// 显示文件列表
function displayFileList(files) {
    const texts = i18n[currentLang];
    if (files.length === 0) {
        fileList.innerHTML = `<p>${texts.noFiles}</p>`;
        return;
    }
    
    fileList.innerHTML = '';
    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = file.filename;
        
        const fileTime = document.createElement('div');
        fileTime.className = 'file-time';
        const texts = i18n[currentLang];
        const locale = currentLang === 'zh' ? 'zh-CN' : 'en-US';
        fileTime.textContent = (currentLang === 'zh' ? '修改时间: ' : 'Modified: ') + new Date(file.modified_time * 1000).toLocaleString(locale);
        
        fileItem.appendChild(fileName);
        fileItem.appendChild(fileTime);
        
        fileItem.addEventListener('click', () => {
            loadFile(file.file_path);
        });
        
        fileList.appendChild(fileItem);
    });
}

// 加载文件
async function loadFile(filePath) {
    const configPath = loadConfigSelect.value || null;
    
    try {
        const response = await fetch(`${API_BASE}/api/load`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_path: filePath,
                config_path: configPath
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            isInitialized = true;
            allDialogs = data.all_dialogs || [];
            currentTherapy = data.current_therapy || null;
            // 更新config文件名称显示
            if (data.config_path) {
                updateConfigFileName(data.config_path);
            }
            // 加载会话后，自动显示最后一个会话（当前会话）
            if (allDialogs && allDialogs.length > 0) {
                viewingSessionIndex = allDialogs.length - 1; // 显示最后一个会话
            } else {
                viewingSessionIndex = null;
            }
            
            // 更新 debug 信息以显示当前疗法
            if (currentTherapy) {
                currentDebugInfo = { current_therapy: currentTherapy };
                if (debugToggle.checked) {
                    updateDebugPanel(currentDebugInfo);
                }
            }
            // 更新 UI（包括渲染历史会话列表）
            updateUI();
            sendBtn.disabled = false;
            loadModal.style.display = 'none';
            alert(currentLang === 'zh' ? '存档文件加载成功！' : 'Archive file loaded successfully!');
        } else {
            alert((currentLang === 'zh' ? '加载失败: ' : 'Load failed: ') + data.message);
        }
    } catch (error) {
        console.error('加载失败:', error);
        alert((currentLang === 'zh' ? '加载失败: ' : 'Load failed: ') + error.message);
    }
}

// 发送消息
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    if (!isInitialized) {
        const texts = i18n[currentLang];
        alert(texts.pleaseInit);
        return;
    }
    
    // 禁用输入和按钮
    sendBtn.disabled = true;
    userInput.disabled = true;
    
    // 显示用户消息
    addMessageToCurrentSession('user', message);
    userInput.value = '';
    
    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                patient_input: message
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 更新对话记录
            allDialogs = data.all_dialogs || [];
            
            // 如果正在查看历史会话，自动回到最后一个会话（当前会话）
            if (allDialogs && allDialogs.length > 0) {
                viewingSessionIndex = allDialogs.length - 1;
            } else {
                viewingSessionIndex = null;
            }
            
            // 显示咨询师回复
            const counselorResponse = data.result.counselor_response || '';
            addMessageToCurrentSession('assistant', counselorResponse);
            
            // 更新当前疗法
            if (data.current_therapy) {
                currentTherapy = data.current_therapy;
            }
            
            // 更新 Debug 信息（包含当前疗法信息）
            currentDebugInfo = {
                ...data.result,
                current_therapy: data.current_therapy || currentTherapy || 'N/A'
            };
            if (debugToggle.checked) {
                updateDebugPanel(currentDebugInfo);
            }
            
            // 更新 UI
            updateUI();
        } else {
            alert((currentLang === 'zh' ? '发送失败: ' : 'Send failed: ') + data.message);
        }
    } catch (error) {
        console.error('发送失败:', error);
        alert((currentLang === 'zh' ? '发送失败: ' : 'Send failed: ') + error.message);
    } finally {
        // 恢复输入和按钮
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

// 添加消息到当前会话
function addMessageToCurrentSession(role, content) {
    if (currentSessionContent.querySelector('.empty-message')) {
        currentSessionContent.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const label = document.createElement('div');
    label.className = 'message-label';
    const texts = i18n[currentLang];
    label.textContent = role === 'user' ? texts.visitor : texts.counselor;
    
    const contentDiv = document.createElement('div');
    contentDiv.textContent = content;
    
    messageDiv.appendChild(label);
    messageDiv.appendChild(contentDiv);
    currentSessionContent.appendChild(messageDiv);
    
    // 滚动到底部
    currentSessionContent.scrollTop = currentSessionContent.scrollHeight;
}

// 更新 UI
function updateUI() {
    // 更新当前会话显示
    updateCurrentSession();
    
    // 更新历史会话显示
    updatePastSessions();
}

// 更新当前会话显示
function updateCurrentSession() {
    // 如果allDialogs为空，显示空消息
    if (!allDialogs || allDialogs.length === 0) {
        const texts = i18n[currentLang];
        currentSessionContent.innerHTML = `<p class="empty-message">${texts.noDialog}</p>`;
        sessionTitle.textContent = texts.currentSession;
        backToCurrentBtn.style.display = 'none';
        viewingSessionIndex = null;
        return;
    }
    
    // 如果viewingSessionIndex为null或无效，自动设置为最后一个会话
    if (viewingSessionIndex === null || viewingSessionIndex >= allDialogs.length) {
        viewingSessionIndex = allDialogs.length - 1;
    }
    
    // 显示指定的会话
    displaySession(viewingSessionIndex);
}

// 显示指定索引的会话
function displaySession(sessionIndex) {
    const texts = i18n[currentLang];
    if (!allDialogs || sessionIndex < 0 || sessionIndex >= allDialogs.length) {
        currentSessionContent.innerHTML = `<p class="empty-message">${texts.sessionNotExist}</p>`;
        return;
    }
    
    const session = allDialogs[sessionIndex];
    const dialogue = session.dialogue || [];
    const therapy = session.therapy || texts.unknownTherapy;
    const isEnded = session.is_ended || false;
    const lastIndex = allDialogs.length - 1;
    
    // 显示会话标题，标记为[进行中]或[已结束]
    const statusText = isEnded ? (currentLang === 'zh' ? ' [已结束]' : ' [Ended]') : (currentLang === 'zh' ? ' [进行中]' : ' [In Progress]');
    sessionTitle.textContent = `${texts.session} ${sessionIndex + 1} - ${therapy}${statusText}`;
    
    // 如果当前查看的不是最后一个会话，显示"回到当前会话"按钮
    if (sessionIndex !== lastIndex) {
        backToCurrentBtn.style.display = 'inline-block';
    } else {
        backToCurrentBtn.style.display = 'none';
    }
    
    if (dialogue.length === 0) {
        currentSessionContent.innerHTML = `<p class="empty-message">${texts.sessionEmpty}</p>`;
        return;
    }
    
    renderDialogue(dialogue);
}

// 渲染对话内容
function renderDialogue(dialogue) {
    currentSessionContent.innerHTML = '';
    dialogue.forEach(msg => {
        const role = msg.role === 'user' ? 'user' : 'assistant';
        const content = msg.content || '';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const label = document.createElement('div');
        label.className = 'message-label';
        const texts = i18n[currentLang];
        label.textContent = role === 'user' ? texts.visitor : texts.counselor;
        
        const contentDiv = document.createElement('div');
        contentDiv.textContent = content;
        
        messageDiv.appendChild(label);
        messageDiv.appendChild(contentDiv);
        currentSessionContent.appendChild(messageDiv);
    });
    
    // 滚动到底部
    currentSessionContent.scrollTop = currentSessionContent.scrollHeight;
}

// 回到当前会话（跳转到最后一个会话，即标记为[进行中]的会话）
function backToCurrentSession() {
    if (!allDialogs || allDialogs.length === 0) {
        viewingSessionIndex = null;
    } else {
        // 跳转到最后一个会话
        viewingSessionIndex = allDialogs.length - 1;
    }
    // 更新显示
    updateCurrentSession();
}

// 查看历史会话
function viewHistorySession(sessionIndex) {
    viewingSessionIndex = sessionIndex;
    displaySession(sessionIndex);
}

// 更新历史会话显示
function updatePastSessions() {
    const texts = i18n[currentLang];
    if (!allDialogs || allDialogs.length === 0) {
        sessionsContent.innerHTML = `<p class="empty-message">${texts.noPastSessions}</p>`;
        return;
    }
    
    sessionsContent.innerHTML = '';
    
    // 显示所有会话，包括最后一个（当前会话）
    // 同时显示已结束的会话（is_ended = true）和未结束的会话（is_ended = false）
    for (let i = 0; i < allDialogs.length; i++) {
        const session = allDialogs[i];
        const isEnded = session.is_ended || false;
        const sessionItem = document.createElement('div');
        sessionItem.className = 'session-item';
        
        // 如果当前正在查看这个会话，添加高亮样式
        if (viewingSessionIndex === i) {
            sessionItem.classList.add('session-item-active');
        }
        
        // 如果会话已结束，添加标识
        const header = document.createElement('div');
        header.className = 'session-header';
        const texts = i18n[currentLang];
        const statusText = isEnded ? (currentLang === 'zh' ? ' [已结束]' : ' [Ended]') : (currentLang === 'zh' ? ' [进行中]' : ' [In Progress]');
        header.textContent = `${texts.session} ${i + 1} - ${session.therapy || texts.unknownTherapy}${statusText}`;
        
        const preview = document.createElement('div');
        preview.className = 'session-preview';
        const dialogue = session.dialogue || [];
        if (dialogue.length > 0) {
            const firstMsg = dialogue[0].content || '';
            preview.textContent = firstMsg.substring(0, 100) + (firstMsg.length > 100 ? '...' : '');
        } else {
            preview.textContent = texts.emptySession;
        }
        
        sessionItem.appendChild(header);
        sessionItem.appendChild(preview);
        
        // 添加点击事件
        sessionItem.addEventListener('click', () => {
            viewHistorySession(i);
        });
        
        sessionsContent.appendChild(sessionItem);
    }
}

// 切换 Debug 模式
function toggleDebug() {
    if (debugToggle.checked) {
        debugPanel.style.display = 'flex';
        if (currentDebugInfo) {
            updateDebugPanel(currentDebugInfo);
        }
    } else {
        debugPanel.style.display = 'none';
    }
}

// 更新 Debug 面板
function updateDebugPanel(result) {
    if (!result) {
        debugContent.innerHTML = '<p class="empty-message">等待对话开始...</p>';
        return;
    }
    
    debugContent.innerHTML = '';
    
    // 当前疗法信息（显示在最前面）
    if (result.current_therapy) {
        addDebugSection('当前疗法', {
            '治疗方案': result.current_therapy || 'N/A'
        });
    }
    
    // 情感分类
    if (result.reaction_classification) {
        addDebugSection('情感分类', {
            '主要情感': result.reaction_classification.primary_emotion || 'N/A',
            '情感强度': result.reaction_classification.emotional_intensity || 'N/A'
        });
    }
    
    // 抵抗检测
    if (result.resistance !== undefined) {
        addDebugSection('抵抗检测', {
            '是否抵抗': result.resistance ? '是' : '否'
        });
    }
    
    // 策略选择
    if (result.strategy_selection) {
        addDebugSection('策略选择', {
            '策略': result.strategy_selection.strategy || 'N/A',
            '策略文本': result.strategy_selection.strategy_text || 'N/A'
        });
    }
    
    // 阶段分析
    if (result.phase_analysis) {
        addDebugSection('阶段分析', {
            '当前阶段': result.phase_analysis || 'N/A'
        });
    }
    
    // 记忆检索
    if (result.memory_result) {
        addDebugSection('记忆检索', {
            '检索结果': result.memory_result || 'N/A'
        });
    }
    
    // 会话结束
    if (result.end_session !== undefined) {
        addDebugSection('会话状态', {
            '是否结束会话': result.end_session ? '是' : '否'
        });
    }
    
    // 跨会话信息
    if (result.cross_session) {
        addDebugSection('跨会话评估', result.cross_session);
    }
    
    // 新会话开始
    if (result.new_session_started !== undefined) {
        addDebugSection('会话管理', {
            '新会话已开始': result.new_session_started ? '是' : '否'
        });
    }
    
    // 完整结果（JSON 格式）
    addDebugSection('完整结果 (JSON)', JSON.stringify(result, null, 2));
}

// 添加 Debug 部分
function addDebugSection(title, content) {
    const section = document.createElement('div');
    section.className = 'debug-section';
    
    const titleDiv = document.createElement('div');
    titleDiv.className = 'debug-section-title';
    titleDiv.textContent = title;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'debug-section-content';
    
    if (typeof content === 'object') {
        contentDiv.textContent = JSON.stringify(content, null, 2);
    } else {
        contentDiv.textContent = content;
    }
    
    section.appendChild(titleDiv);
    section.appendChild(contentDiv);
    debugContent.appendChild(section);
}

