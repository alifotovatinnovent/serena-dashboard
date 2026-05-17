#!/usr/bin/env python3
"""
Serena API Server
Connects dashboard to Serena agent
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
from serena_agent import SerenaAgent

app = Flask(__name__)
CORS(app)

serena = SerenaAgent()

@app.route('/')
def index():
    """Serve dashboard"""
    return send_file('serena-dashboard.html')

@app.route('/api/proposals', methods=['GET'])
def get_proposals():
    """Get all proposals"""
    return jsonify(serena.proposals)

@app.route('/api/proposals', methods=['POST'])
def add_proposal():
    """Add new proposal"""
    data = request.json
    
    proposal_id = serena.add_proposal({
        'name': data['name'],
        'company': data['company'],
        'contacts': data['contacts'],
        'amount': data.get('amount'),
        'value_props': data.get('valueProps', ''),
        'proposal_url': data.get('proposalUrl')
    })
    
    # Process immediately
    serena.process_campaigns()
    
    return jsonify({'success': True, 'proposal_id': proposal_id})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get status report"""
    return jsonify(serena.get_status_report())

@app.route('/api/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get specific campaign details"""
    campaign = serena.campaigns.get(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    return jsonify(campaign)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
