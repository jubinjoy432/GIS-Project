from flask import Flask, render_template, jsonify
from backend.analytics import traffic_system

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify(traffic_system.get_latest_data())

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    from flask import Response
    return Response(traffic_system.generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/api/history')
def get_history():
    from flask import request
    slot = request.args.get('slot', 'morning')
    return jsonify(traffic_system.get_historical_data(slot))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
