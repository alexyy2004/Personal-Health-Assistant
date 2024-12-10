
const form = document.getElementById('chatForm');
const loading = document.getElementById('loading');
const chatContainer = document.getElementById('chat');
const userInput = document.getElementById('userInput');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    addMessageToChat('You', message);
    userInput.value = '';
    loading.style.display = 'block';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        loading.style.display = 'none';

        if (response.ok) {
            addMessageToChat('AI', data.response)
        } else {
            addMessageToChat('Error', data.error || 'An error occurred.');
        }
    } catch (error) {
        loading.style.display = 'none';
        addMessageToChat('Error', 'An error occurred. Please try again later.');
        console.error('Error:', error);
    }
});
function addMessageToChat(sender, message) {
    const messageItem = document.createElement('div');
    messageItem.className = sender === 'You' ? 'user-message' : 'ai-message';
    if (sender === 'AI') {
        // 使用 Marked.js 解析 Markdown
        const rawHtml = marked.parse(message);
        // 使用 DOMPurify 净化 HTML
        const cleanHtml = DOMPurify.sanitize(rawHtml);
        message = cleanHtml;
    } else {
        // 对于用户消息，保持原样并处理换行
        message = message.replace(/\n/g, '<br>');
    }
    messageItem.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatContainer.appendChild(messageItem);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
