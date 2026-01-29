import time
import random
import threading
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrafficAI")

# Try importing real AI libraries
try:
    from ultralytics import YOLO
    import cv2
    import numpy as np
    AI_AVAILABLE = True
    logger.info("YOLOv8 and OpenCV detected. Real-time AI mode available.")
except ImportError:
    AI_AVAILABLE = False
    logger.warning("YOLOv8/OpenCV not found. Running in MOCK/SIMULATION mode.")

class TrafficAnalyzer:
    def __init__(self, mode="auto"):
        self.lock = threading.Lock()
        self.data = []
        self.camera_config = [
            {"id": "CAM_002", "lat": 10.025, "lng": 76.312, "name": "Seaport-Airport Rd", "file": "traffic_cam2.mp4"}
        ]
        self.unique_ids = set() # Store unique vehicle track IDs
        self.vehicle_types = ["car", "bike", "bus", "truck"]
        self.running = True
        self.current_frames = {} # Store latest JPG bytes for each camera
        
        # Decide mode
        if mode == "real" and not AI_AVAILABLE:
            logger.error("Real mode requested but libraries missing. Fallback to mock.")
            self.mode = "mock"
        elif mode == "auto":
            self.mode = "real" if AI_AVAILABLE else "mock"
        else:
            self.mode = mode
            
        logger.info(f"Traffic Analyzer starting in {self.mode.upper()} mode.")

        # Initialize Dummy Nodes (Static Locations)
        self.dummy_nodes = []
        base_lat, base_lng = 10.025, 76.312
        for i in range(20):
            self.dummy_nodes.append({
                "lat": base_lat + random.uniform(-0.005, 0.005),
                "lng": base_lng + random.uniform(-0.005, 0.005),
                "id": f"DUMMY_{i}",
                "name": f"Sensor Node #{i+1}"
            })

        # Initialize AI
        self.model = None
        if self.mode == "real":
            try:
                self.model = YOLO('yolov8n.pt') 
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                self.mode = "mock"

        self.thread = threading.Thread(target=self._run_pipeline)
        self.thread.daemon = True
        self.thread.start()

    def _run_pipeline(self):
        if self.mode == "real":
            self._process_cameras()
        else:
            self._generate_mock_stream()

    def _process_cameras(self):
        """
        Multi-Camera Real AI Pipeline.
        Round-robin processing of all configured video files.
        """
        import os
        import cv2 # Ensure cv2 is available in this scope

        caps = {}
        for cam in self.camera_config:
            # Check file existence
            src = cam["file"] if os.path.exists(cam["file"]) else 0 # 0 as fallback, or maybe skip?
            if src == 0 and not os.path.exists("traffic.mov"): # Only fallback to webcam if NO file
                 pass 
            
            # If specified file missing, try to use main traffic.mov
            if isinstance(src, str) and not os.path.exists(src):
                if os.path.exists("traffic.mov"): src = "traffic.mov"
            
            cap = cv2.VideoCapture(src)
            if cap.isOpened():
                caps[cam["id"]] = cap
                logger.info(f"Initialized {cam['id']} with source {src}")
            else:
                logger.warning(f"Failed to open source for {cam['id']}")

        frame_interval = 3 # Process every Nth frame to save CPU
        frame_count = 0
        cached_annotated_frames = {}  # Store last annotated frame per camera

        while self.running:
            keys = list(caps.keys())
            for cam_id in keys:
                cap = caps[cam_id]
                ret, frame = cap.read()
                
                if not ret:
                    # Loop video
                    logger.debug(f"Looping {cam_id}")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Resize for speed (optional, but good for CPU)
                frame = cv2.resize(frame, (640, 360))

                # Frame Skipping Logic
                frame_count += 1
                should_run_ai = (frame_count % frame_interval == 0)

                # Use cached annotated frame by default (keeps boxes visible)
                annotated_frame = cached_annotated_frames.get(cam_id, frame)

                if should_run_ai:
                    # Run Tracking
                    results = self.model.track(frame, persist=True, verbose=False)
                    annotated_frame = results[0].plot()
                    # Cache this annotated frame
                    cached_annotated_frames[cam_id] = annotated_frame

                    # Count Logic
                    current_counts = {v: 0 for v in self.vehicle_types}
                    
                    if results[0].boxes.id is not None:
                        boxes = results[0].boxes
                        track_ids = boxes.id.int().cpu().tolist()
                        clss = boxes.cls.int().cpu().tolist()

                        for track_id, cls_id in zip(track_ids, clss):
                            # Add to unique set
                            self.unique_ids.add(track_id)
                            
                            label = self.model.names[cls_id].lower()
                            if label in ['car', 'motorcycle', 'bus', 'truck']:
                                type_key = label if label != 'motorcycle' else 'bike'
                                current_counts[type_key] += 1
                    
                    # Update Data Store
                    with self.lock:
                        timestamp = datetime.datetime.now().isoformat()
                        if sum(current_counts.values()) > 0:
                            for v_type, count in current_counts.items():
                                if count > 0:
                                    self.data.append({
                                        "camera_id": cam_id,
                                        "camera_name": next(c['name'] for c in self.camera_config if c['id'] == cam_id),
                                        "lat": next(c['lat'] for c in self.camera_config if c['id'] == cam_id),
                                        "lng": next(c['lng'] for c in self.camera_config if c['id'] == cam_id),
                                        "vehicle_type": v_type,
                                        "count": count,
                                        "timestamp": timestamp
                                    })
                        # Prune Data
                        if len(self.data) > 2000: self.data.pop(0)

                # Overlay Timestamp
                cv2.putText(annotated_frame, datetime.datetime.now().strftime("%H:%M:%S"), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                # Store Frame for Streaming (Always update this to keep feed smooth)
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                with self.lock:
                    self.current_frames[cam_id] = buffer.tobytes()
                    
                    # Prune Data
                    if len(self.data) > 2000: self.data.pop(0)

            time.sleep(0.016) # Yield CPU and limit to ~60 FPS

    def generate_frames(self, camera_id):
        """Yields latest frame for specific camera."""
        while True:
            with self.lock:
                frame = self.current_frames.get(camera_id)
            
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # If no frame yet, yield empty or waiting logic
                pass
                
            time.sleep(0.05)
    
    # ... mock stream methods below can remain or be ignored if we always run real ...
    def _generate_mock_stream(self):
        """Generates continuous traffic data for demo purposes."""
        while self.running:
            with self.lock:
                self._generate_mock_data_for_other_cams([c["id"] for c in self.camera_config])
                # Prune
                if len(self.data) > 1000: self.data.pop(0)
            
            time.sleep(2) # Update every 2 seconds

    def _generate_mock_data_for_other_cams(self, cam_ids):
        timestamp = datetime.datetime.now().isoformat()
        # Use camera_config instead of camera_locations
        for cam in self.camera_config:
            if cam["id"] not in cam_ids: continue
            
            # Randomly detect vehicles
            if random.random() > 0.3: # 70% chance of detection per tick
                v_type = random.choice(self.vehicle_types)
                count = random.randint(1, 3)
                
                entry = {
                    "camera_id": cam["id"],
                    "camera_name": cam["name"],
                    "lat": cam["lat"],
                    "lng": cam["lng"],
                    "vehicle_type": v_type,
                    "count": count,
                    "timestamp": timestamp
                }
                self.data.append(entry)

    def get_latest_data(self):
        with self.lock:
            # Return a summary for the dashboard
            total_vehicles = len(self.unique_ids)
            
            # Aggregation by vehicle type
            by_type = {v: 0 for v in self.vehicle_types}
            for d in self.data:
                by_type[d['vehicle_type']] += d['count']
                
            # Aggregation by camera (for map)
            by_camera = {}
            for cam in self.camera_config:
                cam_data = [d for d in self.data if d['camera_id'] == cam['id']]
                
                # If no data yet (e.g. startup), return 0s but correct name
                total_cam = sum(d['count'] for d in cam_data)
                
                # Simple intensity calculation
                intensity = "low"
                if total_cam > 15: intensity = "moderate" # Lower threshold since we clean data often
                if total_cam > 40: intensity = "high"
                
                by_camera[cam['id']] = {
                    "lat": cam['lat'],
                    "lng": cam['lng'],
                    "name": cam['name'],
                    "total": total_cam,
                    "intensity": intensity,
                    "breakdown": {v: sum(d['count'] for d in cam_data if d['vehicle_type'] == v) for v in self.vehicle_types}
                }

            # Generate Dummy Heatmap Data (Using Persistent Locations)
            current_dummy_data = []
            for node in self.dummy_nodes:
                # Random traffic intensity for this update
                count = random.randint(10, 60)
                intensity = "low"
                if count > 20: intensity = "moderate"
                if count > 45: intensity = "high"
                
                heading = node.copy()
                heading.update({
                    "total": count,
                    "intensity": intensity,
                    "breakdown": {"car": count, "bike": 0, "bus": 0, "truck": 0}
                })
                current_dummy_data.append(heading)

            return {
                "total_vehicles": total_vehicles,
                "distribution": by_type,
                "locations": list(by_camera.values()) + current_dummy_data
            }

traffic_system = TrafficAnalyzer(mode="auto")
