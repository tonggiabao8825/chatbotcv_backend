document.getElementById("send-button").addEventListener("click", sendmessage);
document.getElementById("user-input").addEventListener("keypress", function(event){
    if(event.key === "Enter") {
        sendmessage();
    }
});

// Function to add messages using DOM manipulation rather than innerHTML
function addMessage(type, content) {
    const chatbox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.className = type;
    
    const paragraph = document.createElement("p");
    paragraph.textContent = content;
    
    messageDiv.appendChild(paragraph);
    
    const typingIndicator = document.querySelector(".typing-indicator");
    chatbox.insertBefore(messageDiv, typingIndicator);
    
    chatbox.scrollTop = chatbox.scrollHeight;
    
    return { messageDiv, paragraph }; 
}

// Function to simulate streaming text effect
async function streamText(element, text, speed = 30) {
    element.textContent = '';
    
    for (let i = 0; i < text.length; i++) {
        element.textContent += text.charAt(i);
        await new Promise(resolve => setTimeout(resolve, speed));
        element.parentElement.parentElement.scrollTop = element.parentElement.parentElement.scrollHeight;
    }
}

async function sendmessage() {
    const chatbox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input").value.trim();
    const typingIndicator = document.querySelector(".typing-indicator");
    
    if(!userInput) {
        return;
    }
    else {
        addMessage("user-message", userInput);
        document.getElementById("user-input").value = "";
        
        typingIndicator.style.display = "block";
        chatbox.scrollTop = chatbox.scrollHeight;
        
        try {
            const response = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message: userInput})
            });
            
            const data = await response.json();
            typingIndicator.style.display = "none";
            const { messageDiv, paragraph } = addMessage("bot-message", "");
            await streamText(paragraph, data.answer);
        }
        catch(e) {
            typingIndicator.style.display = "none";
            const { messageDiv, paragraph } = addMessage("bot-message", "");
            await streamText(paragraph, `Unable to connect to server! ${e.message}`);
        }
    }
}