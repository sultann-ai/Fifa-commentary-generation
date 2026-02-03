// Client-side JavaScript for FIFA Commentator

const videoInput = document.getElementById('videoInput');
const videoPlayer = document.getElementById('videoPlayer');
const fileName = document.getElementById('fileName');
const commentary = document.getElementById('commentary');
const status = document.getElementById('status');

let ws = null;

// API endpoint
const API_URL = 'http://localhost:8000';

// Load voices when they become available
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        const voices = window.speechSynthesis.getVoices();
        console.log('Available voices:', voices.length);
    };
}

// Handle video file selection
videoInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    fileName.textContent = `Selected: ${file.name}`;
    
    // Display video locally
    const videoURL = URL.createObjectURL(file);
    videoPlayer.src = videoURL;
    
    // Clear previous commentary
    commentary.innerHTML = '<div class="commentary-title">Live Commentary</div><div id="commentaryText" class="commentary-text">Processing video...</div>';
    
    // Upload video to backend
    await uploadVideo(file);
});

async function uploadVideo(file) {
    try {
        showStatus('Uploading video...', 'success');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const result = await response.json();
        showStatus('Video uploaded successfully! Processing...', 'success');
        
        // Connect WebSocket with job_id
        connectWebSocket(result.job_id);
        
    } catch (error) {
        showStatus('Error uploading video: ' + error.message, 'error');
        console.error('Upload error:', error);
    }
}

function connectWebSocket(jobId) {
    console.log('Connecting WebSocket for job:', jobId);
    ws = new WebSocket('ws://localhost:8000/ws/commentary');
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        showStatus('Connected! Waiting for commentary...', 'success');
        
        // Wait a bit for connection to fully establish
        setTimeout(() => {
            // Send job_id to start receiving commentary
            const message = JSON.stringify({ job_id: jobId });
            console.log('Sending job_id:', message);
            ws.send(message);
        }, 100);
    };
    
    ws.onmessage = (event) => {
        console.log('Received message:', event.data);
        const data = JSON.parse(event.data);
        
        if (data.commentary) {
            console.log('Commentary received:', data.commentary);
            addCommentary(data.commentary, data.timestamp);
        } else if (data.status) {
            console.log('Status:', data.message);
        } else if (data.error) {
            console.error('Error:', data.error);
            showStatus('Error: ' + data.error, 'error');
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        showStatus('Connection error', 'error');
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        showStatus('Processing complete!', 'success');
    };
}

function addCommentary(text, timestamp) {
    const time = timestamp ? `[${formatTime(timestamp)}] ` : '';
    
    // Get or create commentary text container
    let commentaryText = document.getElementById('commentaryText');
    if (!commentaryText) {
        commentaryText = document.createElement('div');
        commentaryText.id = 'commentaryText';
        commentaryText.className = 'commentary-text';
        commentary.appendChild(commentaryText);
    }
    
    const newComment = document.createElement('p');
    newComment.textContent = `${time}${text}`;
    newComment.style.marginBottom = '10px';
    newComment.style.animation = 'fadeIn 0.3s';
    
    commentaryText.appendChild(newComment);
    commentary.scrollTop = commentary.scrollHeight;
    
    // Speak the commentary using Web Speech API
    speakCommentary(text);
}

function speakCommentary(text) {
    console.log('Attempting to speak:', text);
    
    // Check if speech synthesis is supported
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        // Small delay to ensure cancellation is complete
        setTimeout(() => {
            // Create a new speech utterance
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Configure voice settings
            utterance.rate = 1.1;  // Slightly faster for excitement
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Try to use a more natural voice if available
            const voices = window.speechSynthesis.getVoices();
            console.log('Available voices:', voices.length);
            
            const englishVoice = voices.find(voice => 
                voice.lang.startsWith('en') && 
                (voice.name.includes('Natural') || voice.name.includes('Google') || voice.name.includes('Microsoft'))
            );
            
            if (englishVoice) {
                utterance.voice = englishVoice;
                console.log('Using voice:', englishVoice.name);
            } else if (voices.length > 0) {
                // Use first available English voice
                const anyEnglishVoice = voices.find(v => v.lang.startsWith('en'));
                if (anyEnglishVoice) {
                    utterance.voice = anyEnglishVoice;
                    console.log('Using voice:', anyEnglishVoice.name);
                }
            }
            
            utterance.onstart = () => console.log('Speech started');
            utterance.onend = () => console.log('Speech ended');
            utterance.onerror = (e) => console.error('Speech error:', e);
            
            // Speak the text
            window.speechSynthesis.speak(utterance);
            console.log('Speech queued');
        }, 100);
        
    } else {
        console.error('Speech synthesis not supported in this browser');
        alert('Speech synthesis is not supported in your browser. Please try Chrome, Edge, or Firefox.');
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    
    if (type === 'success') {
        setTimeout(() => {
            status.className = 'status';
        }, 3000);
    }
}

// Add fade-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);
