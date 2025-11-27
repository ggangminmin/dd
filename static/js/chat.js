/**
 * 챗봇 프론트엔드 로직
 */

let currentUser = null;
let selectedFiles = [];

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 로그인 상태 확인
    checkAuthStatus();

    // 드래그 앤 드롭 설정
    setupDragAndDrop();
});

/**
 * 로그인 상태 확인
 */
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/check-auth');
        const data = await response.json();

        if (data.authenticated) {
            // 이미 로그인된 경우
            currentUser = data.user;
            showChatScreen(data.user.username);
            loadChatHistory();
        } else {
            // 로그인 안 된 경우
            showLoginScreen();
        }
    } catch (error) {
        console.error('인증 확인 오류:', error);
        showLoginScreen();
    }
}

/**
 * 로그인 화면 표시
 */
function showLoginScreen() {
    document.getElementById('login-screen').classList.add('active');
    document.getElementById('chat-screen').classList.remove('active');

    // 로그인 탭에 포커스
    const loginUsernameInput = document.getElementById('login-username');
    if (loginUsernameInput) {
        setTimeout(() => loginUsernameInput.focus(), 100);
    }
}

/**
 * 인증 탭 전환
 */
function switchAuthTab(tab) {
    const loginTab = document.querySelector('.auth-tab:first-child');
    const signupTab = document.querySelector('.auth-tab:last-child');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    const errorMsg = document.getElementById('auth-error');
    const successMsg = document.getElementById('auth-success');

    // 에러/성공 메시지 초기화
    errorMsg.textContent = '';
    successMsg.textContent = '';

    if (tab === 'login') {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.classList.add('active');
        signupForm.classList.remove('active');
        forgotPasswordForm.classList.remove('active');
        setTimeout(() => document.getElementById('login-username').focus(), 100);
    } else {
        loginTab.classList.remove('active');
        signupTab.classList.add('active');
        loginForm.classList.remove('active');
        signupForm.classList.add('active');
        forgotPasswordForm.classList.remove('active');
        setTimeout(() => document.getElementById('signup-username').focus(), 100);
    }
}

/**
 * 비밀번호 찾기 화면 표시
 */
function showForgotPassword(event) {
    event.preventDefault();

    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    const loginTab = document.querySelector('.auth-tab:first-child');
    const signupTab = document.querySelector('.auth-tab:last-child');
    const errorMsg = document.getElementById('auth-error');
    const successMsg = document.getElementById('auth-success');

    // 에러/성공 메시지 초기화
    errorMsg.textContent = '';
    successMsg.textContent = '';

    // 탭 비활성화
    loginTab.classList.remove('active');
    signupTab.classList.remove('active');

    // 폼 전환
    loginForm.classList.remove('active');
    signupForm.classList.remove('active');
    forgotPasswordForm.classList.add('active');

    setTimeout(() => document.getElementById('forgot-email').focus(), 100);
}

/**
 * 로그인 화면으로 돌아가기
 */
function backToLogin() {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    const loginTab = document.querySelector('.auth-tab:first-child');
    const errorMsg = document.getElementById('auth-error');
    const successMsg = document.getElementById('auth-success');

    // 에러/성공 메시지 초기화
    errorMsg.textContent = '';
    successMsg.textContent = '';

    // 로그인 탭 활성화
    loginTab.classList.add('active');

    // 폼 전환
    forgotPasswordForm.classList.remove('active');
    loginForm.classList.add('active');
    signupForm.classList.remove('active');

    setTimeout(() => document.getElementById('login-username').focus(), 100);
}

/**
 * 비밀번호 찾기 처리
 */
async function handleForgotPassword() {
    const email = document.getElementById('forgot-email').value.trim();
    const errorMsg = document.getElementById('auth-error');
    const successMsg = document.getElementById('auth-success');

    errorMsg.textContent = '';
    successMsg.textContent = '';

    if (!email) {
        errorMsg.textContent = '이메일을 입력해주세요.';
        return;
    }

    try {
        const response = await fetch('/api/request-password-reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.success) {
            successMsg.textContent = data.message;
            document.getElementById('forgot-email').value = '';
        } else {
            errorMsg.textContent = data.error || '오류가 발생했습니다.';
        }
    } catch (error) {
        console.error('비밀번호 찾기 오류:', error);
        errorMsg.textContent = '서버와의 통신에 실패했습니다.';
    }
}

/**
 * 비밀번호 찾기 엔터키 처리
 */
function handleForgotPasswordKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        handleForgotPassword();
    }
}

/**
 * 로그인 처리
 */
async function handleLogin() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const errorMsg = document.getElementById('auth-error');
    const successMsg = document.getElementById('auth-success');

    errorMsg.textContent = '';
    successMsg.textContent = '';

    if (!username || !password) {
        errorMsg.textContent = '아이디와 비밀번호를 입력해주세요.';
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            currentUser = data.user;
            successMsg.textContent = data.message;
            setTimeout(() => {
                showChatScreen(data.user.username);
                loadHistoryFromLoginResponse(data.history);
            }, 500);
        } else {
            errorMsg.textContent = data.error;
        }
    } catch (error) {
        console.error('로그인 오류:', error);
        errorMsg.textContent = '로그인 중 오류가 발생했습니다.';
    }
}

/**
 * 회원가입 처리
 */
async function handleSignup() {
    const username = document.getElementById('signup-username').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;
    const passwordConfirm = document.getElementById('signup-password-confirm').value;
    const errorMsg = document.getElementById('auth-error');
    const successMsg = document.getElementById('auth-success');

    errorMsg.textContent = '';
    successMsg.textContent = '';

    if (!username || !email || !password || !passwordConfirm) {
        errorMsg.textContent = '모든 필드를 입력해주세요.';
        return;
    }

    if (password !== passwordConfirm) {
        errorMsg.textContent = '비밀번호가 일치하지 않습니다.';
        return;
    }

    if (password.length < 6) {
        errorMsg.textContent = '비밀번호는 최소 6자 이상이어야 합니다.';
        return;
    }

    try {
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (data.success) {
            currentUser = data.user;
            successMsg.textContent = data.message;
            setTimeout(() => {
                showChatScreen(data.user.username);
            }, 500);
        } else {
            errorMsg.textContent = data.error;
        }
    } catch (error) {
        console.error('회원가입 오류:', error);
        errorMsg.textContent = '회원가입 중 오류가 발생했습니다.';
    }
}

/**
 * 게스트 로그인
 */
async function guestLogin() {
    const guestUsername = 'Guest_' + Math.random().toString(36).substring(2, 8);

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: guestUsername })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '게스트 로그인 실패');
        }

        currentUser = { username: data.username };
        showChatScreen(data.username);
        loadHistoryFromLoginResponse(data.history);
    } catch (error) {
        console.error('게스트 로그인 오류:', error);
        document.getElementById('auth-error').textContent = '게스트 로그인 중 오류가 발생했습니다.';
    }
}

/**
 * Enter 키 처리 (로그인)
 */
function handleLoginKeyPress(event) {
    if (event.key === 'Enter') {
        handleLogin();
    }
}

/**
 * Enter 키 처리 (회원가입)
 */
function handleSignupKeyPress(event) {
    if (event.key === 'Enter') {
        handleSignup();
    }
}

/**
 * 채팅 화면 표시
 */
function showChatScreen(username) {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('chat-screen').classList.add('active');
    document.getElementById('user-info').textContent = `👤 ${username}`;

    // 메시지 입력창에 포커스
    setTimeout(() => {
        const messageInput = document.getElementById('message-input');
        if (messageInput) messageInput.focus();
    }, 100);
}

/**
 * 로그인 응답에서 히스토리 로드
 */
function loadHistoryFromLoginResponse(history) {
    if (!history || history.length === 0) return;

    const messagesDiv = document.getElementById('chat-messages');
    messagesDiv.innerHTML = ''; // 기존 메시지 제거

    // 역순으로 메시지 표시 (오래된 것부터)
    history.reverse().forEach(msg => {
        if (msg.is_user) {
            // 사용자 메시지: 첨부 파일도 함께 표시
            addUserMessage(msg.message || "", msg.attached_files || [], null, false);
        } else {
            addBotMessage(msg.message, false);
        }
    });

    scrollToBottom();
}

/**
 * 로그아웃
 */
async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        currentUser = null;
        localStorage.removeItem('chatbot_username');

        // 채팅 화면 초기화
        document.getElementById('chat-messages').innerHTML = '<div class="welcome-message"><p>안녕하세요! 무엇을 도와드릴까요?</p></div>';

        // 로그인 화면으로 전환
        showLoginScreen();

        // 폼 초기화
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
        document.getElementById('signup-username').value = '';
        document.getElementById('signup-email').value = '';
        document.getElementById('signup-password').value = '';
        document.getElementById('signup-password-confirm').value = '';

        // 로그인 탭으로 전환
        switchAuthTab('login');
    } catch (error) {
        console.error('로그아웃 오류:', error);
    }
}

/**
 * 드래그 앤 드롭 기능 설정
 */
function setupDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');

    if (!dropZone) return;

    // 드래그 이벤트 방지 (기본 동작 차단)
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // 드래그 진입 시 시각적 피드백
    dropZone.addEventListener('dragenter', function(e) {
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragover', function(e) {
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', function(e) {
        // input-wrapper 영역을 벗어날 때만 클래스 제거
        if (e.target === dropZone) {
            dropZone.classList.remove('drag-over');
        }
    });

    // 파일 드롭
    dropZone.addEventListener('drop', function(e) {
        dropZone.classList.remove('drag-over');

        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            handleDroppedFiles(files);
        }
    });
}

/**
 * 파일 미리보기 표시
 */
function displayFilePreview(files) {
    const preview = document.getElementById('file-preview');
    preview.innerHTML = '';

    files.forEach((file, index) => {
        const fileItem = document.createElement('div');

        // 이미지 파일 확인
        const isImage = file.type.startsWith('image/');

        if (isImage) {
            // 이미지 미리보기
            fileItem.className = 'file-item image-preview';

            const reader = new FileReader();
            reader.onload = function(e) {
                const fileSize = formatFileSize(file.size);
                fileItem.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}" class="preview-image">
                    <div class="image-overlay">
                        <span class="image-name">${file.name}</span>
                        <span class="image-size">${fileSize}</span>
                    </div>
                    <button class="file-remove image-remove" onclick="removeFile(${index})" title="삭제">&times;</button>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            // 일반 파일
            fileItem.className = 'file-item';
            const fileIcon = getFileIcon(file.name);
            const fileSize = formatFileSize(file.size);

            fileItem.innerHTML = `
                <span class="file-icon">${fileIcon}</span>
                <span class="file-name">${file.name}</span>
                <span class="file-size">${fileSize}</span>
                <button class="file-remove" onclick="removeFile(${index})">&times;</button>
            `;
        }

        preview.appendChild(fileItem);
    });
}

/**
 * 드롭된 파일 처리
 */
function handleDroppedFiles(files) {
    const fileInput = document.getElementById('file-input');
    const dataTransfer = new DataTransfer();

    // 기존 선택된 파일 유지
    selectedFiles.forEach(file => {
        dataTransfer.items.add(file);
    });

    // 새로 드롭된 파일 추가
    Array.from(files).forEach(file => {
        dataTransfer.items.add(file);
    });

    fileInput.files = dataTransfer.files;

    // 파일 선택 이벤트 트리거
    const event = new Event('change', { bubbles: true });
    fileInput.dispatchEvent(event);
}

// 기존 로그인 관련 함수들은 새로운 인증 시스템으로 대체되었습니다.

/**
 * 히스토리 로드 (호환성 유지)
 */
async function loadChatHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) return;

        const data = await response.json();
        if (data.history && data.history.length > 0) {
            loadHistoryFromLoginResponse(data.history);
        }
    } catch (error) {
        console.error('히스토리 로드 오류:', error);
    }
}

// 기존 logout, loginUser, autoLogin 함수들은 삭제되고 새 버전으로 대체되었습니다.

/**
 * 화면 전환
 */
function switchScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

/**
 * 파일 선택 처리 (📎 버튼 클릭 시)
 */
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    selectedFiles = files;

    // 파일 미리보기 표시
    displayFilePreview(files);
}

/**
 * 파일 제거
 */
function removeFile(index) {
    selectedFiles.splice(index, 1);

    // 파일이 모두 제거되면 미리보기 영역 비우기
    if (selectedFiles.length === 0) {
        const preview = document.getElementById('file-preview');
        preview.innerHTML = '';
    } else {
        // 미리보기 다시 렌더링
        displayFilePreview(selectedFiles);
    }
}

/**
 * 메시지 전송
 */
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message && selectedFiles.length === 0) return;

    // 입력창 비우기
    input.value = '';
    input.style.height = 'auto';

    // 사용자 메시지 표시 (이미지 URL은 나중에 추가)
    const displayMessage = message || ''; // 메시지 없으면 빈 문자열
    const tempMessageId = Date.now(); // 임시 ID
    addUserMessage(displayMessage, [], tempMessageId);

    // 전송 버튼 비활성화
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;

    // 타이핑 인디케이터 표시
    showTypingIndicator();

    try {
        // FormData로 파일과 메시지 전송
        const formData = new FormData();
        formData.append('message', message);

        selectedFiles.forEach(file => {
            console.log('첨부 파일:', file.name, file.size, 'bytes');
            formData.append('files', file);
        });

        console.log('메시지 전송 시작...');
        const response = await fetch('/api/chat', {
            method: 'POST',
            body: formData
        });

        console.log('응답 상태:', response.status, response.statusText);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('서버 오류 응답:', errorText);
            throw new Error(`메시지 전송 실패: ${response.status}`);
        }

        const data = await response.json();
        console.log('응답 데이터:', data);

        // 타이핑 인디케이터 제거
        hideTypingIndicator();

        // 첨부 파일이 있으면 사용자 메시지에 추가
        if (data.attached_files && data.attached_files.length > 0) {
            updateUserMessageWithFiles(tempMessageId, data.attached_files);
        }

        // 봇 응답 표시
        addBotMessage(data.response);

        // 감정 정보 표시
        if (data.sentiment_info) {
            showSentimentInfo(data.sentiment_info);
        }

        // 파일 미리보기 초기화
        selectedFiles = [];
        const preview = document.getElementById('file-preview');
        preview.innerHTML = '';
        document.getElementById('file-input').value = '';

    } catch (error) {
        console.error('Send message error:', error);
        hideTypingIndicator();
        addBotMessage('죄송합니다. 메시지 전송 중 오류가 발생했습니다.');
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

/**
 * 사용자 메시지 추가
 */
function addUserMessage(message, imageUrls = [], messageId = null, scroll = true) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';

    if (messageId) {
        messageDiv.setAttribute('data-message-id', messageId);
    }

    let imagesHtml = '';
    if (imageUrls && imageUrls.length > 0) {
        imagesHtml = '<div class="message-images">';
        imageUrls.forEach(url => {
            imagesHtml += `<img src="${url}" alt="첨부 이미지" class="message-image">`;
        });
        imagesHtml += '</div>';
    }

    messageDiv.innerHTML = `
        ${imagesHtml}
        ${message ? `<div class="message-content">${escapeHtml(message)}</div>` : ''}
        <div class="message-time">${getCurrentTime()}</div>
    `;

    messagesDiv.appendChild(messageDiv);

    if (scroll) {
        scrollToBottom();
    }
}

/**
 * 사용자 메시지 추가 (이전 대화 이력용 - 첨부 파일 포함)
 */
function addUserMessageWithHistory(message, attachedFiles, messageId, scroll = true) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';

    if (messageId) {
        messageDiv.setAttribute('data-message-id', messageId);
    }

    let contentHtml = '';

    // 이미지 파일
    const images = attachedFiles.filter(f => f.is_image);
    if (images.length > 0) {
        contentHtml += '<div class="message-images">';
        images.forEach(file => {
            contentHtml += `<img src="${file.url}" alt="${file.filename}" class="message-image">`;
        });
        contentHtml += '</div>';
    }

    // 일반 파일
    const otherFiles = attachedFiles.filter(f => !f.is_image);
    if (otherFiles.length > 0) {
        contentHtml += '<div class="message-files">';
        otherFiles.forEach(file => {
            // Excel/CSV 표 미리보기
            if (file.table_data) {
                contentHtml += renderTablePreview(file);
            }
            // Word/Text 파일 미리보기
            else if (file.text_preview) {
                contentHtml += renderTextPreview(file);
            }
            else {
                // 파일 카드 (다운로드용)
                const fileIcon = getFileIcon(file.filename);
                const fileSize = formatFileSize(file.size);
                contentHtml += `
                    <a href="${file.url}" download="${file.filename}" class="file-card">
                        <span class="file-card-icon">${fileIcon}</span>
                        <div class="file-card-info">
                            <div class="file-card-name">${escapeHtml(file.filename)}</div>
                            <div class="file-card-size">${fileSize}</div>
                        </div>
                    </a>
                `;
            }
        });
        contentHtml += '</div>';
    }

    // 메시지 텍스트 (있으면 표시)
    if (message && message.trim()) {
        contentHtml += `<div class="message-content">${escapeHtml(message)}</div>`;
    }

    contentHtml += `<div class="message-time">${getCurrentTime()}</div>`;

    messageDiv.innerHTML = contentHtml;
    messagesDiv.appendChild(messageDiv);

    if (scroll) {
        scrollToBottom();
    }
}

/**
 * 사용자 메시지에 첨부 파일 추가 (업로드 후)
 */
function updateUserMessageWithFiles(messageId, attachedFiles) {
    const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageDiv) return;

    const messageContent = messageDiv.querySelector('.message-content');
    const messageTime = messageDiv.querySelector('.message-time');

    let filesHtml = '';

    // 이미지 파일
    const images = attachedFiles.filter(f => f.is_image);
    if (images.length > 0) {
        filesHtml += '<div class="message-images">';
        images.forEach(file => {
            filesHtml += `<img src="${file.url}" alt="${file.filename}" class="message-image">`;
        });
        filesHtml += '</div>';
    }

    // 일반 파일
    const otherFiles = attachedFiles.filter(f => !f.is_image);
    if (otherFiles.length > 0) {
        filesHtml += '<div class="message-files">';
        otherFiles.forEach(file => {
            // Excel/CSV 표 미리보기
            if (file.table_data) {
                filesHtml += renderTablePreview(file);
            }
            // Word/Text 파일 미리보기
            else if (file.text_preview) {
                filesHtml += renderTextPreview(file);
            }
            else {
                // 파일 카드 (다운로드용) - 미리보기가 없을 때만 표시
                const fileIcon = getFileIcon(file.filename);
                const fileSize = formatFileSize(file.size);
                filesHtml += `
                    <a href="${file.url}" download="${file.filename}" class="file-card">
                        <span class="file-card-icon">${fileIcon}</span>
                        <div class="file-card-info">
                            <div class="file-card-name">${escapeHtml(file.filename)}</div>
                            <div class="file-card-size">${fileSize}</div>
                        </div>
                    </a>
                `;
            }
        });
        filesHtml += '</div>';
    }

    // 파일을 메시지 내용 앞에 삽입
    if (messageContent) {
        messageContent.insertAdjacentHTML('beforebegin', filesHtml);
    } else {
        messageTime.insertAdjacentHTML('beforebegin', filesHtml);
    }

    scrollToBottom();
}

/**
 * 봇 메시지 추가
 */
function addBotMessage(message, scroll = true) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';

    // HTML 포함 여부 확인 (뉴스, 표 등)
    const containsHtml = message.includes('<') && message.includes('>');

    messageDiv.innerHTML = `
        <div class="message-content">${containsHtml ? message : escapeHtml(message)}</div>
        <div class="message-time">${getCurrentTime()}</div>
    `;

    messagesDiv.appendChild(messageDiv);

    if (scroll) {
        scrollToBottom();
    }
}

/**
 * 타이핑 인디케이터 표시
 */
function showTypingIndicator() {
    const messagesDiv = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing';
    typingDiv.id = 'typing-indicator';

    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    messagesDiv.appendChild(typingDiv);
    scrollToBottom();
}

/**
 * 타이핑 인디케이터 숨기기
 */
function hideTypingIndicator() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

/**
 * 감정 정보 표시
 */
function showSentimentInfo(sentimentInfo) {
    const indicator = document.getElementById('sentiment-indicator');
    const sentimentMap = {
        'angry': { emoji: '😠', text: '화남', color: '#e74c3c' },
        'sad': { emoji: '😢', text: '슬픔', color: '#3498db' },
        'happy': { emoji: '😊', text: '기쁨', color: '#2ecc71' },
        'polite': { emoji: '🙏', text: '공손', color: '#9b59b6' },
        'neutral': { emoji: '😐', text: '중립', color: '#95a5a6' }
    };

    const sentiment = sentimentMap[sentimentInfo.sentiment] || sentimentMap['neutral'];

    indicator.innerHTML = `
        ${sentiment.emoji} 감지된 감정: <span style="color: ${sentiment.color}; font-weight: bold;">${sentiment.text}</span>
    `;

    // 3초 후 숨기기
    setTimeout(() => {
        indicator.innerHTML = '';
    }, 3000);
}

/**
 * 대화 이력 모달 표시
 */
async function showHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) throw new Error('이력 조회 실패');

        const data = await response.json();
        const modal = document.getElementById('history-modal');
        const content = document.getElementById('history-content');

        let html = '<h4>통계 정보</h4>';

        if (data.stats) {
            html += `
                <div class="stats-item">
                    <label>총 메시지 수</label>
                    <div>${data.stats.total_messages}개</div>
                </div>
                <div class="stats-item">
                    <label>첫 대화</label>
                    <div>${formatDate(data.stats.first_interaction)}</div>
                </div>
                <div class="stats-item">
                    <label>최근 대화</label>
                    <div>${formatDate(data.stats.last_interaction)}</div>
                </div>
            `;
        }

        content.innerHTML = html;
        modal.classList.add('active');

    } catch (error) {
        console.error('History error:', error);
        alert('이력을 불러오는 중 오류가 발생했습니다.');
    }
}

/**
 * 대화 이력 모달 닫기
 */
function closeHistory() {
    document.getElementById('history-modal').classList.remove('active');
}

/**
 * 전문가 시스템 상태 표시
 */
async function showExpertStatus() {
    try {
        const response = await fetch('/api/expert-status');
        if (!response.ok) throw new Error('전문가 상태 조회 실패');

        const data = await response.json();
        const modal = document.getElementById('expert-modal');
        const content = document.getElementById('expert-content');

        const progress = (data.conversation_count / data.auto_summarize_interval) * 100;

        let html = `
            <div class="expert-section">
                <h4>💬 메세징 전문가</h4>
                <p>고객 질문에 감정 기반으로 자연스럽게 응답합니다.</p>
                <div class="expert-status">
                    <span class="status-badge active">활성</span>
                    <span>GPT ${data.gpt_enabled ? '사용 중' : '미사용'}</span>
                </div>
            </div>

            <div class="expert-section">
                <h4>📢 마케팅 전문가</h4>
                <p>긍정적 반응 감지 시 자연스러운 CTA를 제안합니다.</p>
                <div class="expert-status">
                    <span class="status-badge active">활성</span>
                    <span>긍정 신호 모니터링 중</span>
                </div>
            </div>

            <div class="expert-section">
                <h4>📝 문서작성 전문가</h4>
                <p>대화 내용을 자동으로 분석하고 FAQ를 생성합니다.</p>
                <div class="expert-status">
                    <span class="status-badge active">활성</span>
                    <span>대화 버퍼: ${data.conversation_count}/${data.auto_summarize_interval}개</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
                <p class="progress-text">${data.auto_summarize_interval - data.conversation_count}개 대화 후 자동 요약</p>
            </div>

            <div class="expert-section">
                <h4>🔄 협업 워크플로우</h4>
                <ol class="workflow-list">
                    <li>고객 질문 → <strong>메세징 전문가</strong>가 감정 분석 후 1차 응답</li>
                    <li>긍정 신호 감지 → <strong>마케팅 전문가</strong>가 CTA 추가</li>
                    <li>대화 진행 → <strong>문서작성 전문가</strong>가 자동 기록</li>
                    <li>${data.auto_summarize_interval}개 대화 완료 → 자동으로 FAQ 생성 및 저장</li>
                </ol>
            </div>

            <div class="expert-actions">
                <button onclick="manualSummarize()" class="summarize-btn">📄 지금 요약하기</button>
            </div>
        `;

        content.innerHTML = html;
        modal.classList.add('active');

    } catch (error) {
        console.error('Expert status error:', error);
        alert('전문가 상태를 불러오는 중 오류가 발생했습니다.');
    }
}

/**
 * 전문가 시스템 모달 닫기
 */
function closeExpertStatus() {
    document.getElementById('expert-modal').classList.remove('active');
}

/**
 * 수동 요약 트리거
 */
async function manualSummarize() {
    if (!confirm('현재까지의 대화 내용을 요약하시겠습니까?')) {
        return;
    }

    try {
        const response = await fetch('/api/summarize', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ ' + data.message + '\n\n주제: ' + data.summary.main_topic);
            closeExpertStatus();
            // 상태 새로고침
            setTimeout(() => showExpertStatus(), 500);
        } else {
            alert('⚠️ ' + data.message);
        }
    } catch (error) {
        console.error('Summarize error:', error);
        alert('요약 중 오류가 발생했습니다.');
    }
}

/**
 * 키 입력 처리
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * 스크롤을 최하단으로
 */
function scrollToBottom() {
    const messagesDiv = document.getElementById('chat-messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * 현재 시간 포맷
 */
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
}

/**
 * 날짜 포맷
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR');
}

/**
 * HTML 이스케이프
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 파일 아이콘 가져오기
 */
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'webp': '🖼️',
        'pdf': '📄', 'docx': '📝', 'txt': '📃',
        'xlsx': '📊', 'csv': '📈',
        'json': '📋', 'xml': '📋',
        'zip': '📦'
    };
    return iconMap[ext] || '📎';
}

/**
 * 파일 크기 포맷
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Word/Text 파일 미리보기 렌더링
 */
function renderTextPreview(file) {
    const textContent = file.text_preview || '';
    const maxLength = 500; // 최대 표시 길이
    const truncated = textContent.length > maxLength;
    const displayText = truncated ? textContent.substring(0, maxLength) + '...' : textContent;

    const fileIcon = getFileIcon(file.filename);
    const fileSize = formatFileSize(file.size);

    let html = '<div class="text-preview-container">';

    // 헤더
    html += '<div class="text-preview-header">';
    html += `<span class="text-preview-icon">${fileIcon}</span>`;
    html += `<div class="text-preview-title">`;
    html += `<div class="text-preview-filename">${escapeHtml(file.filename)}</div>`;
    html += `<div class="text-preview-size">${fileSize}</div>`;
    html += `</div>`;
    html += `<a href="${file.url}" download="${file.filename}" class="text-preview-download" title="다운로드">⬇</a>`;
    html += '</div>';

    // 내용
    html += '<div class="text-preview-content">';
    html += escapeHtml(displayText).replace(/\n/g, '<br>');
    html += '</div>';

    if (truncated) {
        html += '<div class="text-preview-more">더 보려면 파일을 다운로드하세요</div>';
    }

    html += '</div>';

    return html;
}

/**
 * Excel/CSV 표 미리보기 렌더링
 */
function renderTablePreview(file) {
    const tableData = file.table_data;
    if (!tableData || !tableData.headers || !tableData.rows) {
        return '';
    }

    let html = '<div class="excel-preview-container">';
    html += `<div class="excel-filename">${escapeHtml(file.filename)}</div>`;

    // 전체 행 수 표시
    if (tableData.total_rows > tableData.rows.length) {
        html += `<div class="excel-info">처음 ${tableData.rows.length}행 표시 (전체 ${tableData.total_rows}행)</div>`;
    }

    html += '<div class="excel-table-wrapper">';
    html += '<table class="excel-table">';

    // 헤더
    html += '<thead><tr>';
    tableData.headers.forEach(header => {
        html += `<th>${escapeHtml(String(header))}</th>`;
    });
    html += '</tr></thead>';

    // 데이터 행
    html += '<tbody>';
    tableData.rows.forEach(row => {
        html += '<tr>';
        row.forEach(cell => {
            const cellValue = cell === null || cell === undefined ? '' : String(cell);
            html += `<td>${escapeHtml(cellValue)}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';

    html += '</table>';
    html += '</div>'; // excel-table-wrapper
    html += '</div>'; // excel-preview-container

    return html;
}

// 텍스트 영역 자동 크기 조절
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('message-input');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
    }
});

/**
 * 대화 기록 삭제
 */
async function deleteHistory() {
    if (!confirm('정말로 모든 대화 기록을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')) {
        return;
    }

    try {
        const response = await fetch('/api/delete-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            // 화면의 메시지 제거
            document.getElementById('chat-messages').innerHTML = '<div class="welcome-message">대화 기록이 삭제되었습니다.</div>';
        } else {
            alert(data.error || '대화 삭제 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('대화 삭제 오류:', error);
        alert('서버와의 통신에 실패했습니다.');
    }
}

/**
 * 대화 기록 내보내기
 */
async function exportHistory(format = 'json') {
    try {
        // JSON 또는 TXT 다운로드
        window.location.href = `/api/export-history?format=${format}`;
    } catch (error) {
        console.error('대화 내보내기 오류:', error);
        alert('대화 내보내기 중 오류가 발생했습니다.');
    }
}
