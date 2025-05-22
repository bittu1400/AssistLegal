let userAuth = undefined

document.addEventListener('DOMContentLoaded', async function () {
    const chatBody = document.querySelector('.chat-body');
    const chatInputField = document.querySelector('.chat-input-field');
    const chatSendBtn = document.querySelector('.chat-send-btn');

    // Initialize chat history from localStorage
    loadChatHistory();

    // Scroll to bottom of chat
    scrollToBottom();

    const response = await fetch("http://127.0.0.1:8000/firebase-config");
    const firebaseConfig = await response.json();

    if (!firebase?.apps?.length) {
        firebase.initializeApp(firebaseConfig);
    }

    firebase.auth().onAuthStateChanged(async (user) => {
        userAuth = user
    })

    // Send message when clicking the send button
    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', sendMessage);
    }

    // Send message when pressing Enter
    if (chatInputField) {
        chatInputField.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Select domain from sidebar
    const domainItems = document.querySelectorAll('.domain-item');
    domainItems.forEach(function (item) {
        item.addEventListener('click', function () {
            if (this.classList.contains('disabled')) {
                showToast('This domain is coming soon!');
                return;
            }

            // Remove active class from all items
            domainItems.forEach(function (domain) {
                domain.classList.remove('active');
            });

            // Add active class to clicked item
            this.classList.add('active');

            // Update domain title in chat header
            const domainTitle = this.querySelector('.domain-item-title').textContent;
            document.querySelector('.current-domain').textContent = domainTitle;

            // Clear chat history when changing domains
            if (confirm('Changing domain will clear current chat history. Continue?')) {
                clearChat();
                saveChatHistory();
            } else {
                // If user cancels, revert to previous active domain
                this.classList.remove('active');
                const prevActive = document.querySelector('.domain-item.active');
                if (prevActive) {
                    prevActive.classList.add('active');
                }
            }
        });
    });

    // Toggle sidebar on mobile
    const toggleSidebarBtn = document.querySelector('.toggle-sidebar-btn');
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', function () {
            const sidebar = document.querySelector('.chat-sidebar');
            sidebar.classList.toggle('active');
        });
    }

    function sendMessage() {
        const message = chatInputField.value.trim();

        if (message === '') return;

        // Add user message to chat
        addUserMessage(message);

        // Clear input field
        chatInputField.value = '';

        // Show typing indicator
        showTypingIndicator();

        // Save to chat history
        saveChatHistory();

        // Send to server and get response
        sendToServer(message);
    }

    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-user';

        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageElement.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${timeString}</div>
        `;

        chatBody.appendChild(messageElement);
        scrollToBottom();
    }

    function addBotMessage(message) {
        // Remove typing indicator if exists
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }

        const messageElement = document.createElement('div');
        messageElement.className = 'message message-bot';

        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageElement.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${timeString}</div>
        `;

        chatBody.appendChild(messageElement);
        chatInputField.disabled = false;
        chatInputField.focus();

        scrollToBottom();
    }

    function showTypingIndicator() {
        const indicatorElement = document.createElement('div');
        indicatorElement.className = 'message message-bot typing-indicator';

        indicatorElement.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;

        chatBody.appendChild(indicatorElement);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    async function sendToServer(message) {
        fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // 'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ user_message: message })
        })
            .then(async response => {
                console.log("Raw response status:", response.status);
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || 'Unknown error');
                }
                addBotMessage(data.response);
                saveChatHistory();
            })
            .catch(error => {
                console.error('Error:', error);
                addBotMessage('Sorry, I encountered an error. Please try again later.');
                saveChatHistory();
            });
    }

    function saveChatHistory() {
        const domain = document.querySelector('.current-domain')?.textContent || 'default';
        const messages = chatBody.querySelectorAll('.message');
        const history = [];

        messages.forEach(message => {
            const content = message.querySelector('.message-content')?.textContent || '';
            const time = message.querySelector('.message-time')?.textContent || '';
            const isUser = message.classList.contains('message-user');

            history.push({ content, time, isUser });
        });

        localStorage.setItem(`chatHistory_${domain}`, JSON.stringify(history));
    }


    function loadChatHistory() {
        const domain = document.querySelector('.current-domain')?.textContent || 'default';
        const history = JSON.parse(localStorage.getItem(`chatHistory_${domain}`) || '[]');

        history.forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.className = message.isUser ? 'message message-user' : 'message message-bot';
            messageElement.innerHTML = `
            <div class="message-content">${message.content}</div>
            <div class="message-time">${message.time}</div>
        `;
            chatBody.appendChild(messageElement);
        });
    }


    function clearChat() {
        while (chatBody.firstChild) {
            chatBody.removeChild(chatBody.firstChild);
        }
        localStorage.removeItem('chatHistory');
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;

        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        toast.style.color = 'white';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '4px';
        toast.style.zIndex = '9999';
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';

        document.body.appendChild(toast);

        // Show toast
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 10);

        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
});