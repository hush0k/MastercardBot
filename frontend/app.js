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
  const resultsDiv = document.getElementById("results");
  const tableEl = document.getElementById("table");
  const sqlEl = document.getElementById("sql");
  
  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.textContent = text;
    msg.classList.add("msg", sender);
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
      showResults(mockResponse);
    }, 800);
  }
  
  function showResults(data) {
    resultsDiv.style.display = "block";
    sqlEl.innerHTML = `<b>SQL:</b> ${data.sql}`;
  
    let html = `<tr>${data.columns.map(col => `<th>${col}</th>`).join("")}</tr>`;
    data.results.forEach(row => {
      html += `<tr>${data.columns.map(col => `<td>${row[col]}</td>`).join("")}</tr>`;
    });
  
    tableEl.innerHTML = html;
  }
  
  document.getElementById("send-btn").addEventListener("click", sendMessage);
  input.addEventListener("keypress", e => { if(e.key === "Enter") sendMessage(); });
  