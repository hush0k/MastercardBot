const API_URL = "http://localhost:8088";

  const chat = document.getElementById("chat-container");
  const input = document.getElementById("user-input");

  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("msg", sender);
    msg.innerHTML = text;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    const thinkingMsg = addMessage("Thinking...", "bot");

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Remove "Thinking..." message
      chat.removeChild(chat.lastChild);

      if (data.error) {
        addMessage(`Error: ${data.error}`, "bot");
      } else if (data.results && data.results.length > 0) {
        showResultsInChat(data);
      } else {
        addMessage("No results found for your query.", "bot");
      }
    } catch (error) {
      console.error('Error:', error);
      chat.removeChild(chat.lastChild);
      addMessage(`Error connecting to server: ${error.message}`, "bot");
    }
  }
  
  function showResultsInChat(data) {
    const botMsg = document.createElement("div");
    botMsg.classList.add("msg", "bot");
  
    let html = `<p><b>SQL:</b> ${data.sql}</p>`;
    html += `<table style="width:100%; border-collapse: collapse; margin-top: 6px;">`;
    html += `<tr>${data.columns.map(col => `<th style="border:1px solid #ccc; padding:6px; text-align:left;">${col}</th>`).join("")}</tr>`;
    data.results.forEach(row => {
      html += `<tr>${data.columns.map(col => `<td style="border:1px solid #ccc; padding:6px;">${row[col]}</td>`).join("")}</tr>`;
    });
    html += `</table>`;
  
    botMsg.innerHTML = html;
    chat.appendChild(botMsg);
    chat.scrollTop = chat.scrollHeight;
  }
  
  document.getElementById("send-btn").addEventListener("click", sendMessage);
  input.addEventListener("keypress", e => { if(e.key === "Enter") sendMessage(); });
  