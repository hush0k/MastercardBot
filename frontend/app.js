const mockResponse = {
    question: "Top 5 merchants",
    sql: "SELECT merchant_name, SUM(amount) as revenue FROM transactions GROUP BY merchant_name ORDER BY revenue DESC LIMIT 5",
    results: [
      { merchant_name: "Yandex", revenue: 1500000 },
      { merchant_name: "Silk Pay", revenue: 1200000 },
      { merchant_name: "Kaspi", revenue: 950000 },
      { merchant_name: "Halyk", revenue: 720000 },
      { merchant_name: "Beeline", revenue: 680000 }
    ],
    columns: ["merchant_name", "revenue"]
  };
  
  const chat = document.getElementById("chat-container");
  const input = document.getElementById("user-input");
  
  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("msg", sender);
    msg.innerHTML = text;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
  }
  
  function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
  
    addMessage(text, "user");
    input.value = "";
  
    addMessage("Thinking...", "bot");
  
    setTimeout(() => {
      chat.removeChild(chat.lastChild);
      addMessage("Here are the top merchants:", "bot");
      showResultsInChat(mockResponse);
    }, 800);
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
  