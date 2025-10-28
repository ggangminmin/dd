/**
 * 챗봇 프론트엔드 로직
 */

let currentUser = null;
let selectedFiles = [];

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // Enter 키로 로그인
    const usernameInput = document.getElementById('username-input');
    if (usernameInput) {
        usernameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loginUser();
            }
        });
        usernameInput.focus();
    }
});

/**
 * 사용자 로그인
 */
async function loginUser() {
    const username = document.getElementById('username-input').value.trim();
    const errorDiv = document.getElementById('login-error');

    if (!username) {
        errorDiv.textContent = '이름을 입력해주세요.';
        return;
    }

    errorDiv.textContent = '';

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username })
        });

        if (!response.ok) {
            const error = await response.json();
            errorDiv.textContent = error.error || '로그인 중 오류가 발생했습니다.';
            return;
        }

        const data = await response.json();
        currentUser = data;

        // 채팅 화면으로 전환
        switchScreen('chat-screen');

        // 사용자 정보 표시
        document.getElementById('user-info').textContent = `${data.username}님 환영합니다`;

        // 메시지 영역 초기화
        const messagesDiv = document.getElementById('chat-messages');
        messagesDiv.innerHTML = '';

        // 환영 메시지 표시
        addBotMessage(data.welcome_message);

        // 이전 대화 이력 표시
        if (data.history && data.history.length > 0) {
            data.history.forEach(msg => {
                if (msg.is_user) {
                    addUserMessage(msg.message, false);
                } else {
                    addBotMessage(msg.message, false);
                }
            });
        }

        // 입력창에 포커스
        document.getElementById('message-input').focus();

    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = '서버 연결 중 오류가 발생했습니다.';
    }
}

/**
 * 로그아웃
 */
function logout() {
    if (confirm('로그아웃하시겠습니까?')) {
        currentUser = null;
        document.getElementById('username-input').value = '';
        switchScreen('login-screen');
    }
}

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
 * 파일 선택 처리
 */
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    selectedFiles = files;

    // 파일 미리보기 표시
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
 * 파일 제거
 */
function removeFile(index) {
    selectedFiles.splice(index, 1);

    // 파일 input 초기화
    const fileInput = document.getElementById('file-input');
    fileInput.value = '';

    // 미리보기 다시 렌더링
    const preview = document.getElementById('file-preview');
    preview.innerHTML = '';

    selectedFiles.forEach((file, idx) => {
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
                    <button class="file-remove image-remove" onclick="removeFile(${idx})" title="삭제">&times;</button>
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
                <button class="file-remove" onclick="removeFile(${idx})">&times;</button>
            `;
        }

        preview.appendChild(fileItem);
    });
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
            formData.append('files', file);
        });

        const response = await fetch('/api/chat', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('메시지 전송 실패');
        }

        const data = await response.json();

        // 타이핑 인디케이터 제거
        hideTypingIndicator();

        // 이미지 URL이 있으면 사용자 메시지에 추가
        if (data.image_urls && data.image_urls.length > 0) {
            updateUserMessageWithImages(tempMessageId, data.image_urls);
        }

        // 봇 응답 표시
        addBotMessage(data.response);

        // 감정 정보 표시
        if (data.sentiment_info) {
            showSentimentInfo(data.sentiment_info);
        }

        // 파일 미리보기 초기화
        selectedFiles = [];
        document.getElementById('file-preview').innerHTML = '';
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
 * 사용자 메시지에 이미지 추가 (업로드 후)
 */
function updateUserMessageWithImages(messageId, imageUrls) {
    const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageDiv) return;

    const messageContent = messageDiv.querySelector('.message-content');
    const messageTime = messageDiv.querySelector('.message-time');

    let imagesHtml = '<div class="message-images">';
    imageUrls.forEach(url => {
        imagesHtml += `<img src="${url}" alt="첨부 이미지" class="message-image">`;
    });
    imagesHtml += '</div>';

    // 이미지를 메시지 내용 앞에 삽입
    if (messageContent) {
        messageContent.insertAdjacentHTML('beforebegin', imagesHtml);
    } else {
        messageTime.insertAdjacentHTML('beforebegin', imagesHtml);
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

    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(message)}</div>
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
