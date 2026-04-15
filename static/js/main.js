// MÜZEREHBERI - Ana JavaScript Dosyası

function searchArtwork() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value;
    
    if (query.trim() === '') {
        alert('Lütfen bir eser adı girin');
        return;
    }
    
    console.log('Aranan eser:', query);
    // API çağrısı burada yapılacak
}

// Enter tuşuna basıldığında arama yap
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchArtwork();
        }
    });
});

// ──────────────────── EXHIBIT PAGE FUNCTIONS ────────────────────

let currentLanguage = 'tr';

function onLanguageChange() {
    const langSelect = document.getElementById('exhibitLang');
    currentLanguage = langSelect.value;
    console.log('Dil değişti:', currentLanguage);
}

function speakDescription() {
    const btn = document.getElementById('btnSpeak');
    btn.disabled = true;
    btn.innerHTML = '⏳ Hazırlanıyor...';

    fetch('/api/describe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            exhibit_id: EXHIBIT_ID,
            language: currentLanguage
        })
    })
    .then(response => response.json())
    .then(data => {
        btn.disabled = false;
        btn.innerHTML = '🔊 Sesli Rehberlik';

        if (data.error) {
            console.error('Sesli rehberlik hatası:', data.error);
            return;
        }

        if (data.audio_url) {
            playAudio(data.audio_url);
        }
    })
    .catch(err => {
        btn.disabled = false;
        btn.innerHTML = '🔊 Sesli Rehberlik';
        console.error('Sesli rehberlik bağlantı hatası:', err);
    });
}

let recognition = null;
let isListening = false;

function toggleVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Tarayıcınız ses girişini desteklemiyor. Chrome, Edge veya Safari kullanın.');
        return;
    }

    if (isListening) {
        stopVoiceInput();
        return;
    }

    startVoiceInput();
}

function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.lang = currentLanguage === 'tr' ? 'tr-TR' : 
                      currentLanguage === 'en' ? 'en-US' : 
                      currentLanguage === 'de' ? 'de-DE' : 
                      currentLanguage === 'fr' ? 'fr-FR' : 
                      currentLanguage === 'ar' ? 'ar-SA' : 
                      currentLanguage === 'ja' ? 'ja-JP' : 
                      currentLanguage === 'zh' ? 'zh-CN' : 'tr-TR';
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        isListening = true;
        document.getElementById('btnMic').innerHTML = '🎤 Dinleniyor...';
        document.getElementById('btnMic').classList.add('listening');
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('chatInput').value = transcript;
        sendQuestion(); // Otomatik gönder
    };

    recognition.onerror = function(event) {
        console.error('Ses tanıma hatası:', event.error);
        alert('Ses tanıma hatası: ' + event.error);
        stopVoiceInput();
    };

    recognition.onend = function() {
        stopVoiceInput();
    };

    recognition.start();
}

function stopVoiceInput() {
    if (recognition) {
        recognition.stop();
    }
    isListening = false;
    document.getElementById('btnMic').innerHTML = '🎤 Sesle Soru Sor';
    document.getElementById('btnMic').classList.remove('listening');
}

function sendQuestion() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    
    if (!question) {
        alert('Lütfen bir soru girin.');
        return;
    }

    // Kullanıcı mesajını ekle
    addMessage('user', question);
    input.value = '';

    // API'ye gönder
    fetch('/api/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            exhibit_id: EXHIBIT_ID,
            language: currentLanguage
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage('assistant', 'Üzgünüm, bir hata oluştu: ' + data.error);
        } else {
            addMessage('assistant', data.answer);
            // Sesli oynat
            if (data.audio_url) {
                playAudio(data.audio_url);
            }
        }
    })
    .catch(error => {
        addMessage('assistant', 'Bağlantı hatası: ' + error.message);
    });
}

function addMessage(sender, text) {
    const messages = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender} fade-in`;
    bubble.innerHTML = `
        <div class="bubble-speaker">${sender === 'user' ? '👤 Siz' : '🏛️ Rehber'}</div>
        ${text}
    `;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
}

function playAudio(url) {
    const audio = document.getElementById('audioElement');
    const player = document.getElementById('audioPlayer');
    audio.src = url;
    audio.play();
    if (player) {
        player.classList.add('visible');
    }
}
