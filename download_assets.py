import requests
import os

# New Highway/Road Videos
files = {
    "traffic_cam2.mp4": "https://github.com/wdzhong/traffic-video-process/raw/master/Freewa.mp4",
    "traffic_cam3.mp4": "https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4" # Reverting to car-detection as fallback for cam3, Freewa is definitely highway
}

def cleanup_corrupt_files():
    # Force delete potential corrupt model causing blank feed
    if os.path.exists("yolov8n.pt"):
        print("Removing existing yolov8n.pt to force fresh download...")
        try:
            os.remove("yolov8n.pt")
        except Exception as e:
            print(f"Error removing model: {e}")

    # Remove old videos to replace them
    for fname in files.keys():
        if os.path.exists(fname):
            try:
                os.remove(fname)
                print(f"Removed old {fname}")
            except Exception as e:
                print(f"Error removing {fname}: {e}")

def download_file(url, filename):
    print(f"Downloading {filename}...")
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    cleanup_corrupt_files()
    for fname, url in files.items():
        download_file(url, fname)
