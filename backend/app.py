from flask import Flask, request, jsonify
from flask_cors import CORS
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

# In-memory storage for demo purposes
issues = []
meetings = []

@app.route('/api/qr/generate', methods=['POST'])
def generate_qr():
    data = request.json
    flat_details = data.get('flatDetails', '')
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(flat_details)
    qr.make(fit=True)
    
    # Create QR image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for sending to frontend
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'qr_code': img_str})

@app.route('/api/issues', methods=['GET', 'POST'])
def handle_issues():
    if request.method == 'POST':
        issue = request.json
        issue['id'] = len(issues) + 1
        issue['status'] = 'pending'
        issues.append(issue)
        return jsonify(issue), 201
    
    return jsonify(issues)

@app.route('/api/meetings', methods=['GET', 'POST'])
def handle_meetings():
    if request.method == 'POST':
        meeting = request.json
        meeting['id'] = len(meetings) + 1
        meetings.append(meeting)
        return jsonify(meeting), 201
    
    return jsonify(meetings)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 