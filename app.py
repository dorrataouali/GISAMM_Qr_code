from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pandas as pd
import gspread
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)

# Authenticate with Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# File ID of your Excel file on Google Drive
file_id = 'https://docs.google.com/spreadsheets/d/1ZflCUx-sR0p5zLLbUc-Fqw3cZS68SkdD/edit?usp=drive_link&ouid=103349363123575394209&rtpof=true&sd=true'

# Load participant data from Excel
file = drive.CreateFile({'id': file_id})
file.GetContentFile('participants.xlsx')

df = pd.read_excel('participants.xlsx', engine='openpyxl')

# Dummy database to simulate check-ins
check_ins = {}

@app.route('/')
def index():
    return render_template('index_with_counter.html', participants=df.to_dict(orient='records'))

@app.route('/check_in', methods=['POST'])
def check_in():
    try:
        qr_data = request.form['qr_data']

        # Decode QR code data to get participant information
        participant_info = decode_qr(qr_data)

        # Check if the participant is registered
        if participant_info['Email'] in df['Email'].values:
            # Simulate check-in by updating the check_ins database
            email = participant_info['Email']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if email not in check_ins:
                check_ins[email] = {'count': 1, 'timestamps': [timestamp]}
            else:
                check_ins[email]['count'] += 1
                check_ins[email]['timestamps'].append(timestamp)

            return jsonify({'status': 'success', 'message': 'Check-in successful', 'participant_info': participant_info, 'count': check_ins[email]['count'], 'timestamps': check_ins[email]['timestamps']})
        else:
            return jsonify({'status': 'error', 'message': 'Participant not registered'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def decode_qr(qr_data):
    # In a real-world scenario, you would need to implement a secure decoding mechanism
    # This is a dummy implementation assuming the QR code contains participant information
    lines = qr_data.split('\n')
    participant_info = {}
    for line in lines:
        key, value = line.split(': ')
        participant_info[key] = value
    return participant_info

if __name__ == '__main__':
    app.run(debug=True)
