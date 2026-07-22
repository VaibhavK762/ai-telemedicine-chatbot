// Telemedicine AI Assistant - Main Application Logic

document.addEventListener('DOMContentLoaded', () => {
  // DOM Element Selectors
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');
  const chatFeed = document.getElementById('chat-feed');
  const emergencyContainer = document.getElementById('emergency-container');
  const newChatBtn = document.getElementById('new-chat-btn');
  const clearHistoryBtn = document.getElementById('clear-history-btn');

  // Navigation Tabs
  const navChat = document.getElementById('nav-chat');
  const navReports = document.getElementById('nav-reports');
  const chatView = document.getElementById('chat-view');
  const reportView = document.getElementById('report-view');
  const headerTitle = document.getElementById('header-title');

  // Report Form Selectors
  const reportForm = document.getElementById('report-form');
  const dropzone = document.getElementById('dropzone');
  const reportFileInput = document.getElementById('report-file');
  const selectedFileName = document.getElementById('selected-file-name');
  const analyzeReportBtn = document.getElementById('analyze-report-btn');
  const reportResultsCard = document.getElementById('report-results-card');
  const ocrTextBox = document.getElementById('ocr-text-box');
  const clinicalSummaryBox = document.getElementById('clinical-summary-box');

  // State
  let sessionId = localStorage.getItem('telemedicine_session_id') || null;

  // Tab Navigation Switching
  navChat.addEventListener('click', () => {
    navChat.classList.add('active');
    navReports.classList.remove('active');
    chatView.classList.remove('hidden');
    reportView.classList.add('hidden');
    headerTitle.textContent = 'AI Telemedicine Chat Assistant';
  });

  navReports.addEventListener('click', () => {
    navReports.classList.add('active');
    navChat.classList.remove('active');
    reportView.classList.remove('hidden');
    chatView.classList.add('hidden');
    headerTitle.textContent = 'Lab Report OCR & Analysis';
  });

  // Auto-expanding Textarea
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  sendBtn.addEventListener('click', handleSendMessage);

  newChatBtn.addEventListener('click', () => {
    sessionId = null;
    localStorage.removeItem('telemedicine_session_id');
    emergencyContainer.innerHTML = '';
    chatFeed.innerHTML = `
      <div id="emergency-container"></div>
      <div class="message-row assistant-row">
        <div class="avatar assistant-avatar">🤖</div>
        <div class="message-bubble">
          Started a new conversation session. How can I assist you with your health today?
          <div class="disclaimer-tag">
            <i data-lucide="shield-alert" style="width: 14px; height: 14px;"></i>
            Educational medical guidance only. Consult a doctor for diagnosis.
          </div>
        </div>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
  });

  clearHistoryBtn.addEventListener('click', async () => {
    if (sessionId) {
      try {
        await fetch(`/api/chat/history/${sessionId}`, { method: 'DELETE' });
      } catch (err) {
        console.error('Error clearing history:', err);
      }
    }
    newChatBtn.click();
  });
  // Send Message Handler
  async function handleSendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Append User Message to UI
    appendUserMessage(message);
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Disable input while processing
    setChatLoading(true);

    // Append Typing Indicator
    const typingElem = createTypingIndicator();
    chatFeed.appendChild(typingElem);
    scrollToBottom();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });

      const data = await response.json();
      chatFeed.removeChild(typingElem);

      if (response.ok) {
        if (data.session_id) {
          sessionId = data.session_id;
          localStorage.setItem('telemedicine_session_id', sessionId);
        }

        // Check Emergency Status
        if (data.is_emergency) {
          renderEmergencyBanner(data.response);
        }

        appendAssistantMessage(data.response);
      } else {
        appendAssistantMessage(`Error: ${data.detail || 'Failed to reach AI Assistant backend.'}`);
      }
    } catch (error) {
      console.error('Chat API Error:', error);
      if (typingElem.parentNode) chatFeed.removeChild(typingElem);
      appendAssistantMessage('Sorry, a network connection error occurred. Please verify backend service availability.');
    } finally {
      setChatLoading(false);
      scrollToBottom();
    }
  }

  function appendUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'message-row user-row';
    row.innerHTML = `
      <div class="avatar user-avatar">👤</div>
      <div class="message-bubble">${escapeHtml(text)}</div>
    `;
    chatFeed.appendChild(row);
    scrollToBottom();
  }

  function appendAssistantMessage(text) {
    const row = document.createElement('div');
    row.className = 'message-row assistant-row';
    row.innerHTML = `
      <div class="avatar assistant-avatar">🤖</div>
      <div class="message-bubble">
        ${formatMarkdown(text)}
        <div class="disclaimer-tag">
          <i data-lucide="shield-alert" style="width: 14px; height: 14px;"></i>
          Educational medical guidance only. Consult a doctor for diagnosis.
        </div>
      </div>
    `;
    chatFeed.appendChild(row);
    if (window.lucide) window.lucide.createIcons();
    scrollToBottom();
  }

  function createTypingIndicator() {
    const elem = document.createElement('div');
    elem.className = 'message-row assistant-row';
    elem.innerHTML = `
      <div class="avatar assistant-avatar">🤖</div>
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    return elem;
  }

  function renderEmergencyBanner(message) {
    const container = document.getElementById('emergency-container');
    container.innerHTML = `
      <div class="emergency-banner">
        <div class="emergency-icon">🚨</div>
        <div class="emergency-content">
          <h4>EMERGENCY WARNING DETECTED</h4>
          <p>${escapeHtml(message)}</p>
        </div>
      </div>
    `;
  }

  function setChatLoading(isLoading) {
    sendBtn.disabled = isLoading;
    chatInput.disabled = isLoading;
  }

  function scrollToBottom() {
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatMarkdown(text) {
    let formatted = escapeHtml(text);
    // Replace newlines with <br>
    formatted = formatted.replace(/\n/g, '<br>');
    // Bold text **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return formatted;
  }

  // --- Lab Report Drag & Drop and Upload ---
  dropzone.addEventListener('click', () => reportFileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      reportFileInput.files = e.dataTransfer.files;
      updateSelectedFileName();
    }
  });

  reportFileInput.addEventListener('change', updateSelectedFileName);

  function updateSelectedFileName() {
    if (reportFileInput.files.length > 0) {
      selectedFileName.textContent = `Selected File: ${reportFileInput.files[0].name}`;
    }
  }

  reportForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!reportFileInput.files || reportFileInput.files.length === 0) {
      alert('Please select or drop a lab report file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', reportFileInput.files[0]);
    formData.append('test_type', document.getElementById('test-type').value);

    const age = document.getElementById('patient-age').value;
    if (age) formData.append('age', age);

    const sex = document.getElementById('patient-sex').value;
    if (sex) formData.append('sex', sex);

    analyzeReportBtn.disabled = true;
    analyzeReportBtn.textContent = 'Processing OCR & Analysis...';

    reportResultsCard.classList.remove('hidden');
    ocrTextBox.textContent = 'Running PaddleOCR text extraction...';
    clinicalSummaryBox.textContent = 'Analyzing parameters against reference ranges...';

    try {
      const response = await fetch('/api/reports/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        ocrTextBox.textContent = result.raw_ocr_text || result.extracted_text || 'Text extracted successfully.';
        clinicalSummaryBox.innerHTML = formatMarkdown(result.clinical_analysis || result.analysis || JSON.stringify(result, null, 2));
      } else {
        ocrTextBox.textContent = 'Error during report processing.';
        clinicalSummaryBox.textContent = result.detail || 'Failed to process report.';
      }
    } catch (err) {
      console.error('Report upload error:', err);
      ocrTextBox.textContent = 'Upload network error.';
      clinicalSummaryBox.textContent = 'Failed to upload report to backend server.';
    } finally {
      analyzeReportBtn.disabled = false;
      analyzeReportBtn.textContent = 'Extract & Analyze Lab Report';
    }
  });
});
