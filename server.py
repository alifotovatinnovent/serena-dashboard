import os
#!/usr/bin/env python3
"""
Serena API Server - Connected to Autonomous Service
Serves real-time data from running automation
"""

from flask import Flask, jsonify, send_file
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Path to autonomous service data
DATA_PATH = Path.home() / ".openclaw" / "workspace" / "serena-data"

@app.route('/')
def index():
    """Serve dashboard"""
    return send_file('serena-dashboard.html')

@app.route('/api/status')
def get_status():
    """Get autonomous service status"""
    state_file = DATA_PATH / "serena_state.json"
    
    if not state_file.exists():
        return jsonify({
            'status': 'not_initialized',
            'message': 'Autonomous service not started yet'
        })
    
    with open(state_file) as f:
        state = json.load(f)
    
    # Calculate stats
    total_campaigns = len(state.get('campaigns', {}))
    total_activities = state.get('total_activities', 0)
    last_sync = state.get('last_sync', None)
    
    # Count stakeholders and actions
    total_stakeholders = 0
    total_emails = 0
    total_linkedin = 0
    
    for campaign in state.get('campaigns', {}).values():
        total_stakeholders += len(campaign.get('stakeholders', []))
        total_emails += campaign.get('emails_sent', 0)
        total_linkedin += campaign.get('linkedin_sent', 0)
    
    return jsonify({
        'status': 'running',
        'last_sync': last_sync,
        'campaigns': {
            'total': total_campaigns,
            'active': total_campaigns
        },
        'stakeholders': {
            'total': total_stakeholders
        },
        'actions': {
            'emails_sent': total_emails,
            'linkedin_sent': total_linkedin,
            'total_activities': total_activities
        },
        'daily_stats': state.get('daily_stats', {})
    })

@app.route('/api/campaigns')
def get_campaigns():
    """Get all campaigns"""
    state_file = DATA_PATH / "serena_state.json"
    
    if not state_file.exists():
        return jsonify([])
    
    with open(state_file) as f:
        state = json.load(f)
    
    campaigns = []
    for campaign_id, campaign in state.get('campaigns', {}).items():
        campaigns.append({
            'id': campaign_id,
            'name': campaign.get('name'),
            'company': campaign.get('company'),
            'started': campaign.get('started'),
            'status': campaign.get('status'),
            'week': campaign.get('week'),
            'stakeholders': campaign.get('stakeholders', []),
            'emails_sent': campaign.get('emails_sent', 0),
            'linkedin_sent': campaign.get('linkedin_sent', 0)
        })
    
    return jsonify(campaigns)

@app.route('/api/activities')
def get_activities():
    """Get recent activities"""
    log_file = DATA_PATH / "activity_log.jsonl"
    
    if not log_file.exists():
        return jsonify([])
    
    activities = []
    with open(log_file) as f:
        for line in f:
            activities.append(json.loads(line))
    
    # Return last 50 activities, newest first
    return jsonify(activities[-50:][::-1])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
