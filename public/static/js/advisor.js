/**
 * AI Financial Advisor Chat Controller
 * Manages conversational exchange, markdown formatting, and prompt suggestions.
 */

// Send prompt text from one of the quick suggestion pills
function sendPrompt(text) {
    const input = document.getElementById('chat-input');
    if (input) {
        input.value = text;
        const form = document.getElementById('chat-form');
        if (form) {
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
}

// Handle Form Submission
async function handleChatSubmit(event) {
    if (event) event.preventDefault();

    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const message = input.value.trim();

    if (!message) return;

    // 1. Append User Message
    appendMessage(message, 'user');
    input.value = '';
    input.disabled = true;
    sendBtn.disabled = true;

    // 2. Append Typing Indicator
    const typingId = appendTypingIndicator();

    try {
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        removeTypingIndicator(typingId);

        if (data.success && data.reply) {
            appendMessage(data.reply, 'bot');
        } else {
            appendMessage("I encountered an issue processing that question. Please try asking again.", 'bot');
        }
    } catch (err) {
        removeTypingIndicator(typingId);
        appendMessage("Unable to reach the advisor service right now. Please check your network connection.", 'bot');
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// Generate Full Monthly Advisory Report
async function generateComprehensiveReport() {
    const stream = document.getElementById('chat-stream');
    appendMessage("Generating your comprehensive monthly financial analysis report...", 'user');
    const typingId = appendTypingIndicator();

    try {
        const response = await fetch('/api/ai/advice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        const data = await response.json();
        removeTypingIndicator(typingId);

        if (data.success && data.advice) {
            appendMessage(data.advice, 'bot');
        } else {
            appendMessage("Could not compile report at this moment.", 'bot');
        }
    } catch (err) {
        removeTypingIndicator(typingId);
        appendMessage("Error communicating with AI report generator.", 'bot');
    }
}

// Append Chat Bubble to DOM
function appendMessage(text, sender) {
    const stream = document.getElementById('chat-stream');
    if (!stream) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg chat-msg-${sender}`;

    const avatar = document.createElement('div');
    avatar.className = `msg-avatar avatar-${sender}`;
    avatar.textContent = sender === 'user' ? '👤' : '✨';

    const bubble = document.createElement('div');
    bubble.className = `msg-bubble bubble-${sender}`;

    if (sender === 'bot') {
        bubble.innerHTML = formatMarkdown(text);
    } else {
        bubble.textContent = text;
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    stream.appendChild(msgDiv);

    // Scroll to latest message
    stream.scrollTop = stream.scrollHeight;
}

// Typing Indicator Handlers
function appendTypingIndicator() {
    const stream = document.getElementById('chat-stream');
    const typingId = 'typing-' + Date.now();

    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-msg chat-msg-bot';
    msgDiv.id = typingId;

    msgDiv.innerHTML = `
        <div class="msg-avatar avatar-bot">✨</div>
        <div class="msg-bubble bubble-bot">
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span style="font-size: 0.78rem; color: #94a3b8; margin-left: 6px;">Advisor is analyzing...</span>
            </div>
        </div>
    `;

    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
    return typingId;
}

function removeTypingIndicator(typingId) {
    const el = document.getElementById(typingId);
    if (el) el.remove();
}

// Clean Markdown Formatter
function formatMarkdown(text) {
    if (!text) return '';

    let formatted = text
        // Headers
        .replace(/^### (.*$)/gim, '<h4 style="color:#ffffff; margin: 12px 0 6px 0; font-size: 1.05rem;">$1</h4>')
        .replace(/^## (.*$)/gim, '<h3 style="color:#ffffff; margin: 14px 0 8px 0; font-size: 1.15rem;">$1</h3>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#ffffff;">$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Unordered bullet points
        .replace(/^\s*[-•]\s+(.*$)/gim, '<li style="margin-left: 18px; margin-bottom: 4px;">$1</li>')
        // Blockquotes
        .replace(/^\> (.*$)/gim, '<blockquote style="border-left: 3px solid #6366f1; padding-left: 10px; margin: 10px 0; color: #94a3b8; font-size: 0.85rem;">$1</blockquote>')
        // Linebreaks
        .replace(/\n\n/g, '<p style="margin-bottom: 10px;"></p>')
        .replace(/\n/g, '<br>');

    return formatted;
}
