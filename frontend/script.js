// Variables pointing to specific elements in the HTML
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');

// No Conversation Yet
let currentConversationId = null; // Variable to store the current conversation ID

// Function to send a message
async function sendMessage() {
    const text = chatInput.value; // Get the text from the input field

    if (text.trim() === '') return; // Do not send empty messages

    // Creates a 'p' element to log the message in chat log
    const messageE1 = document.createElement("p");
    messageE1.className = "user-message"; // Assign a class for styling
    messageE1.textContent = "You: " + text; // Prefix the message with "You: "
    chatLog.appendChild(messageE1); // Append the message to the chat log

    chatInput.value = ''; // Clear the input field after sending

    // Sending message to backend and waiting for response
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
             message: text,
             conversation_id: currentConversationId // Send the current conversation ID to the backend
            })
    });

    const data = await response.json(); // Parse the JSON FastAPI sent back

    // Remember the conversation ID for future messages
    currentConversationId = data.conversation_id;

    // Show Reply
    const rhyMsgE1 = document.createElement("p");
    rhyMsgE1.className = "rhy-message"; // Assign a class for styling 
    rhyMsgE1.textContent = "Rhy: " + data.reply; // Prefix the reply with "Rhy: "
    chatLog.appendChild(rhyMsgE1); // Append the reply to the chat log
}

sendBtn.addEventListener('click', sendMessage); // Add event listener to the send button

// Allows sending messages by pressing the Enter key
chatInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") { // Check if the pressed key is Enter
        sendMessage(); // Call the sendMessage function
    }

});

sidebarToggle.addEventListener('click', function() {
    sidebar.classList.toggle('collapsed'); // Toggle the 'collapsed' class on the sidebar
});

if (sidebar.classList.contains('collapsed')) {
    sidebar.classList.remove('collapsed'); // Ensure the sidebar is not collapsed on page load
} else {
    sidebar.classList.add('collapsed'); // Collapse the sidebar on page load
}