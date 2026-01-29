# 🚦 Traffic Analytics System

A real-time traffic monitoring and analytics system powered by **YOLOv8** and **Flask**. The system uses computer vision to detect and track vehicles from video feeds, providing live analytics and visualization on an interactive web dashboard.

## ✨ Features

- **Real-time Vehicle Detection**: Uses YOLOv8 for accurate vehicle detection (cars, bikes, buses, trucks)
- **Vehicle Tracking**: Persistent object tracking across frames
- **Live Video Feed**: Streaming annotated video with bounding boxes
- **Interactive Dashboard**: Web-based interface for monitoring traffic data
- **Multi-Camera Support**: Configurable for multiple video sources
- **Heatmap Visualization**: Geographic traffic intensity mapping
- **Mock Mode**: Fallback simulation mode when AI libraries aren't available

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) NVIDIA GPU with CUDA support for accelerated inference

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/GIS-Project-jubin.git
cd GIS-Project-jubin
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

#### Option A: CPU-Only Installation (Default)

```bash
pip install -r requirements.txt
```

#### Option B: NVIDIA GPU Installation (Recommended for better performance)

For **CUDA 12.4+ / CUDA 13.x** (Latest):
```bash
pip install -r requirements-gpu-cu124.txt
```

For **CUDA 12.1**:
```bash
pip install -r requirements-gpu-cu121.txt
```

For **CUDA 11.8**:
```bash
pip install -r requirements-gpu-cu118.txt
```

> **Note**: Make sure you have the appropriate NVIDIA drivers and CUDA toolkit installed on your system. You can check your CUDA version with `nvcc --version` or `nvidia-smi`. CUDA 12.4 builds are forward-compatible with CUDA 13.x.

## 🏃 Running the Application

```bash
python main.py
```

The application will start on `http://localhost:5000`

## 📁 Project Structure

```
GIS-Project-jubin/
├── main.py                     # Flask application entry point
├── backend/
│   └── analytics.py            # Traffic analysis and YOLOv8 integration
├── templates/
│   └── index.html              # Web dashboard template
├── static/
│   ├── css/                    # Stylesheets
│   └── js/                     # JavaScript files
├── requirements.txt            # CPU-only dependencies
├── requirements-gpu-cu118.txt  # GPU dependencies (CUDA 11.8)
├── requirements-gpu-cu121.txt  # GPU dependencies (CUDA 12.1)
├── requirements-gpu-cu124.txt  # GPU dependencies (CUDA 12.4+ / 13.x)
├── yolov8n.pt                  # YOLOv8 nano model weights
└── traffic_cam*.mp4            # Sample video files
```

## 🔧 Configuration

### Camera Configuration

Edit `backend/analytics.py` to configure camera sources:

```python
self.camera_config = [
    {
        "id": "CAM_001",
        "lat": 10.025,
        "lng": 76.312,
        "name": "Location Name",
        "file": "video_file.mp4"
    }
]
```

### Detection Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frame_interval` | Process every Nth frame | 3 |
| Frame Size | Detection resolution | 640x360 |

## 🖥️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/data` | GET | Get latest traffic analytics data |
| `/video_feed/<camera_id>` | GET | Live video stream for a camera |

## 🎮 Modes

The system automatically selects the appropriate mode:

- **Real Mode**: When YOLOv8 and OpenCV are available, processes actual video feeds
- **Mock Mode**: When AI libraries are missing, generates simulated data for demo purposes

## 🔍 Troubleshooting

### GPU Not Detected

1. Verify NVIDIA drivers are installed: `nvidia-smi`
2. Check CUDA version: `nvcc --version`
3. Ensure PyTorch CUDA is working:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should print True
   print(torch.cuda.get_device_name(0))  # Should print your GPU name
   ```

### Video Feed Not Loading

1. Ensure video files exist in the project root
2. Check file permissions
3. Verify OpenCV can read the video format

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
