# ⚽ FIFA AI Commentator

An intelligent real-time football match commentary system powered by computer vision and advanced AI models. Upload any football match video and get natural, dynamic commentary generated automatically!

## 🎯 Description

This project combines cutting-edge computer vision and natural language processing to create an AI-powered sports commentator. Using YOLOv8 for object detection, ByteTrack for player tracking, GPT-4 Vision for event recognition, and GPT-3.5 for commentary generation, the system analyzes football match videos and produces real-time, context-aware commentary with text-to-speech output.

## ✨ Features

- 🎥 **Real-time Video Analysis**: Processes uploaded football match videos frame-by-frame
- 👥 **Player & Ball Detection**: Uses YOLOv8 for accurate object detection
- 📍 **Smart Object Tracking**: ByteTrack algorithm maintains player identities across frames
- 🧠 **AI Event Recognition**: GPT-4 Vision (VLM) identifies key events (goals, passes, shots, tackles)
- 📝 **Natural Commentary**: GPT-3.5-turbo generates engaging, short commentary phrases
- 🎤 **Text-to-Speech**: Browser-based speech synthesis for audio commentary
- ⚡ **WebSocket Streaming**: Real-time commentary delivery to frontend
- 🎨 **Modern Web UI**: Beautiful gradient interface with smooth animations
- 🛡️ **Event Filtering**: Smart aggregation prevents commentary spam (5-second cooldown)

## 🏗️ Architecture

The system consists of three microservices:

### API Service (FastAPI)
- Handles video uploads
- Manages WebSocket connections for real-time streaming
- Creates processing jobs and enqueues them to Redis

### Worker Service (Python)
- Processes videos through ML pipeline:
  1. **Detection**: YOLOv8 identifies players and ball
  2. **Tracking**: ByteTrack maintains object identities
  3. **Classification**: GPT-4 Vision analyzes frames for events
  4. **Aggregation**: Filters duplicate events with confidence thresholds
  5. **Commentary**: GPT-3.5 generates natural language
  6. **Publishing**: Sends commentary via Redis pub/sub

### Frontend Service (HTML/JS)
- Video upload interface
- WebSocket client for real-time commentary
- Browser-based speech synthesis
- Responsive, modern UI design

## 📋 Requirements

- **Python**: 3.10 or higher
- **Redis**: 5.0+ (message queue and pub/sub)
- **OpenAI API Key**: For GPT-4 Vision and GPT-3.5-turbo
- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: Optional but recommended (NVIDIA CUDA for faster processing)

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/fifa-ai-commentator.git
cd fifa-ai-commentator
```

### 2. Install Redis

**Windows:**
```powershell
# Download Redis from https://github.com/microsoftarchive/redis/releases
# Extract to C:\Program Files\Redis
# Add to PATH:
$env:Path += ";C:\Program Files\Redis"
```

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

### 3. Create Virtual Environment
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```powershell
# Install root dependencies
pip install -r requirements.txt

# Install API service dependencies
pip install -r services/api/requirements.txt

# Install worker service dependencies
pip install -r services/worker/requirements.txt
```

### 5. Configure Environment Variables
```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-your-key-here
```

**Required environment variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (get from https://platform.openai.com/api-keys)
- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379`)
- `YOLO_MODEL_PATH`: Path to YOLO model (default: `models/yolov8n.pt`)

### 6. Download YOLO Model
The YOLOv8 model will be downloaded automatically on first run, or manually:
```bash
mkdir models
# YOLOv8n will be downloaded automatically by ultralytics
```

## 🎮 Running the Project

You need **4 separate terminal windows** to run all services:

### Terminal 1: Start Redis
```powershell
redis-server
```
Wait for message: `Ready to accept connections`

### Terminal 2: Start API Service
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to API directory
cd services/api

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API will be available at: http://localhost:8000

### Terminal 3: Start Worker Service
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to worker directory
cd services/worker

# Start processing pipeline
python -m app.pipeline
```
Wait for message: `Worker started. Waiting for jobs...`

### Terminal 4: Start Frontend
```powershell
# Navigate to frontend directory
cd frontend/app

# Start simple HTTP server
python -m http.server 3000
```
Frontend will be available at: http://localhost:3000

## 📖 Usage

1. **Open your browser** and navigate to http://localhost:3000
2. **Upload a video**: Click "Choose File" or drag-and-drop a football match video (.mp4, .avi, .mov, .mkv)
3. **Click "Upload Video"** to start processing
4. **Watch the magic**: Real-time commentary appears in the commentary section
5. **Listen**: Browser will automatically speak the commentary aloud

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints
- `POST /upload`: Upload video for processing
- `GET /ws/commentary/{job_id}`: WebSocket endpoint for real-time commentary

## ⚙️ Configuration

Edit `configs/pipeline.yaml` to customize:

```yaml
detection:
  classes_to_detect: [person, sports ball]
  confidence_threshold: 0.5

tracking:
  match_threshold: 0.8
  max_frames_skip: 30

classification:
  model: "gpt-4o"  # GPT-4 Vision model
  event_types: [goal, shot, pass, tackle, corner, free_kick, offside, other]

aggregation:
  cooldown_period: 5.0  # Seconds between same events
  min_confidence: 0.75  # Minimum confidence threshold

commentary:
  model: "gpt-3.5-turbo"
  max_tokens: 30  # Keep commentary short
  temperature: 0.7
```

## 🛠️ Troubleshooting

### Redis Connection Error
```powershell
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start Redis server
redis-server
```

### OpenAI API Key Error
```powershell
# Verify API key is set in .env file
Get-Content .env | Select-String OPENAI_API_KEY

# Test API key
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### Worker Not Processing
- Check Redis is running and accessible
- Verify all dependencies are installed
- Check `uploads/` directory exists and is writable
- Review worker terminal for error messages

### No Speech Output
- Ensure browser supports Web Speech API (Chrome/Edge recommended)
- Check browser audio isn't muted
- Look for speech synthesis errors in browser console (F12)

## 📁 Project Structure

```
fifa-ai-commentator/
├── configs/
│   ├── models.yaml           # Model configurations
│   └── pipeline.yaml         # Pipeline settings
├── frontend/
│   └── app/
│       ├── index.html        # Web interface
│       └── client.js         # WebSocket client
├── services/
│   ├── api/
│   │   └── app/
│   │       ├── main.py       # FastAPI application
│   │       ├── routes.py     # Upload & WebSocket endpoints
│   │       └── schemas.py    # Pydantic models
│   └── worker/
│       └── app/
│           ├── pipeline.py           # Main processing pipeline
│           ├── detectors/
│           │   └── yolo_detector.py  # YOLOv8 detection
│           ├── trackers/
│           │   └── bytetrack_wrapper.py  # Object tracking
│           ├── classifiers/
│           │   └── video_classifier.py   # GPT-4 Vision events
│           ├── aggregator/
│           │   └── event_aggregator.py   # Event filtering
│           ├── nlp/
│           │   └── commentary_generator.py  # GPT-3.5 commentary
│           └── utils/
│               └── video_reader.py   # Video frame extraction
├── .env                      # Environment variables (not in git)
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎯 How It Works

1. **Video Upload**: User uploads football match video via web interface
2. **Job Creation**: API service creates unique job ID and enqueues to Redis
3. **Frame Processing**: Worker extracts frames and processes every 30th frame
4. **Detection**: YOLOv8 detects players (`person` class) and ball (`sports ball` class)
5. **Tracking**: ByteTrack assigns unique IDs to maintain object identities
6. **Event Analysis**: GPT-4 Vision analyzes frame with detections to identify events
7. **Filtering**: Event Aggregator filters duplicates using 5-second cooldown
8. **Commentary**: GPT-3.5 generates short, natural commentary (max 8 words)
9. **Delivery**: Commentary sent via Redis pub/sub to WebSocket clients
10. **Speech**: Browser speaks commentary using Web Speech API

## 🤖 AI Models Used

- **YOLOv8n**: Lightweight object detection (Ultralytics)
- **GPT-4o**: Vision-language model for event classification (OpenAI)
- **GPT-3.5-turbo**: Text generation for commentary (OpenAI)
- **Web Speech API**: Browser-native text-to-speech (free)

## 📝 License

MIT License - feel free to use this project for learning and development!

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- ByteTrack for object tracking
- OpenAI for GPT models
- FastAPI framework
- Redis for message queue

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for football fans and AI enthusiasts**
