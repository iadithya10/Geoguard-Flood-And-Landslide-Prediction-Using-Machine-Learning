// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const languageSelector = document.getElementById('language-selector');
const typingIndicator = document.getElementById('typing-indicator');

// Event Listeners
chatForm.addEventListener('submit', handleSubmit);
languageSelector.addEventListener('change', handleLanguageChange);

// Show typing indicator
function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

// Add a message to the chat
function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Convert URLs to clickable links and preserve line breaks
    const formattedMessage = message
        .replace(/\n/g, '<br>')
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');

    contentDiv.innerHTML = formattedMessage;
    messageDiv.appendChild(contentDiv);

    // Remove typing indicator if present
    hideTypingIndicator();

    // Add the message
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, true);

    // Clear input
    userInput.value = '';

    // Show typing indicator
    showTypingIndicator();

    try {
        // Send message to server
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                language: languageSelector.value
            })
        });

        const data = await response.json();

        // Add bot response to chat
        addMessage(data.response);

        // Update emergency helplines if provided
        if (data.emergency_helplines) {
            updateEmergencyHelplines(data.emergency_helplines);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your request. Please try again.');
    }
}

// Handle language change
async function handleLanguageChange() {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: "Language selection changed",
                language: languageSelector.value
            })
        });

        const data = await response.json();
        addMessage(data.response);
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error changing the language. Please try again.');
    }
}

// Update emergency helplines section
function updateEmergencyHelplines(helplines) {
    const helplineContainer = document.getElementById('emergency-helplines');
    if (!helplineContainer) return;

    let html = '<div class="accordion" id="helplineAccordion">';
    
    // Add National helplines first
    if (helplines.National) {
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#national-helplines">
                        National Emergency Numbers
                    </button>
                </h2>
                <div id="national-helplines" class="accordion-collapse collapse show">
                    <div class="accordion-body">
                        <ul class="list-unstyled">`;
        
        for (const [service, number] of Object.entries(helplines.National)) {
            html += `<li><strong>${service}:</strong> <a href="tel:${number}">${number}</a></li>`;
        }
        
        html += `</ul></div></div></div>`;
    }
    
    // Add state helplines
    for (const [state, numbers] of Object.entries(helplines)) {
        if (state !== 'National') {
            const stateId = state.toLowerCase().replace(/\s+/g, '-');
            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${stateId}">
                            ${state}
                        </button>
                    </h2>
                    <div id="${stateId}" class="accordion-collapse collapse">
                        <div class="accordion-body">
                            <ul class="list-unstyled">`;
            
            for (const [service, number] of Object.entries(numbers)) {
                html += `<li><strong>${service}:</strong> <a href="tel:${number}">${number}</a></li>`;
            }
            
            html += `</ul></div></div></div>`;
        }
    }
    
    html += '</div>';
    helplineContainer.innerHTML = html;
}



// Initialize emergency helplines
fetch('/get_helplines')
    .then(response => response.json())
    .then(data => {
        updateEmergencyHelplines(data);
    })
    .catch(error => {
        console.error('Error fetching helplines:', error);
    });