#!/usr/bin/env python3
"""
Serena - AI Sales Acceleration Agent
Autonomous proposal follow-up with multi-channel outreach
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class SerenaAgent:
    """
    Serena autonomously manages proposal follow-up campaigns with:
    - Stakeholder research and mapping
    - Multi-channel outreach (email + LinkedIn)
    - Adaptive sequencing based on engagement
    - Buying signal detection
    - Real-time reporting
    """
    
    def __init__(self, data_dir="serena_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.proposals_file = self.data_dir / "proposals.json"
        self.campaigns_file = self.data_dir / "campaigns.json"
        self.activity_log = self.data_dir / "activity.log"
        
        self.proposals = self._load_json(self.proposals_file, [])
        self.campaigns = self._load_json(self.campaigns_file, {})
        
    def _load_json(self, filepath, default):
        """Load JSON file or return default if not exists"""
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath, data):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _log(self, message):
        """Log activity"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.activity_log, 'a') as f:
            f.write(log_entry)
        print(log_entry.strip())
    
    def add_proposal(self, proposal_data):
        """
        Add a new proposal and start campaign
        
        proposal_data = {
            'name': str,
            'company': str,
            'contacts': [emails],
            'amount': float,
            'value_props': str,
            'proposal_url': str (optional)
        }
        """
        proposal_id = f"prop_{len(self.proposals) + 1}_{int(datetime.now().timestamp())}"
        
        proposal = {
            'id': proposal_id,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'engagement_score': 0,
            **proposal_data
        }
        
        self.proposals.append(proposal)
        self._save_json(self.proposals_file, self.proposals)
        
        # Initialize campaign
        self._init_campaign(proposal)
        
        self._log(f"✅ New proposal added: {proposal['name']} ({proposal['company']})")
        
        return proposal_id
    
    def _init_campaign(self, proposal):
        """Initialize multi-touch campaign for a proposal"""
        campaign_id = proposal['id']
        
        campaign = {
            'proposal_id': campaign_id,
            'status': 'research',
            'stage': 'stakeholder_mapping',
            'stakeholders': [],
            'touches': [],
            'next_action': {
                'action': 'research_stakeholders',
                'scheduled_at': datetime.now().isoformat(),
                'description': 'Researching stakeholders and building org map'
            }
        }
        
        self.campaigns[campaign_id] = campaign
        self._save_json(self.campaigns_file, self.campaigns)
        
        self._log(f"🎯 Campaign initialized for: {proposal['name']}")
    
    def process_campaigns(self):
        """
        Main loop: process all active campaigns
        This would be called periodically (cron or continuous)
        """
        self._log("🔄 Processing active campaigns...")
        
        for proposal in self.proposals:
            if proposal['status'] != 'active':
                continue
            
            campaign = self.campaigns.get(proposal['id'])
            if not campaign:
                continue
            
            # Execute next action based on campaign stage
            self._execute_campaign_action(proposal, campaign)
        
        self._log("✅ Campaign processing complete")
    
    def _execute_campaign_action(self, proposal, campaign):
        """Execute the next action for a campaign"""
        stage = campaign['stage']
        
        if stage == 'stakeholder_mapping':
            self._research_stakeholders(proposal, campaign)
        
        elif stage == 'outreach_planning':
            self._plan_outreach_sequence(proposal, campaign)
        
        elif stage == 'active_outreach':
            self._execute_outreach(proposal, campaign)
        
        elif stage == 'monitoring':
            self._monitor_engagement(proposal, campaign)
    
    def _research_stakeholders(self, proposal, campaign):
        """
        Research and map stakeholders at target company
        
        In production:
        - Use Apollo.io API for contact enrichment
        - Use LinkedIn API for org chart
        - Use web search for company structure
        
        For MVP: placeholder logic
        """
        self._log(f"🔍 Researching stakeholders for: {proposal['company']}")
        
        # Parse primary contacts
        contacts = [c.strip() for c in proposal['contacts'].split(',')]
        
        # In production, enrich these contacts with:
        # - Full name, title, role
        # - LinkedIn profile
        # - Decision-making authority
        # - Reporting structure
        
        stakeholders = []
        for email in contacts:
            name = email.split('@')[0].replace('.', ' ').title()
            stakeholders.append({
                'email': email,
                'name': name,
                'role': 'Unknown',  # Would be enriched via Apollo/LinkedIn
                'linkedin': None,
                'engagement': 0
            })
        
        campaign['stakeholders'] = stakeholders
        campaign['stage'] = 'outreach_planning'
        campaign['next_action'] = {
            'action': 'plan_outreach',
            'scheduled_at': datetime.now().isoformat(),
            'description': f'Planning multi-touch sequence for {len(stakeholders)} stakeholders'
        }
        
        self._save_json(self.campaigns_file, self.campaigns)
        self._log(f"✅ Found {len(stakeholders)} stakeholders")
    
    def _plan_outreach_sequence(self, proposal, campaign):
        """
        Plan adaptive outreach sequence
        
        Multi-touch strategy:
        - Day 1: Initial value email to all stakeholders
        - Day 3: ROI-focused follow-up
        - Day 7: Case study / social proof
        - Day 14: Direct ask / demo offer
        - LinkedIn: Connection requests + message sequence
        
        Adaptive: adjust timing based on engagement
        """
        self._log(f"📋 Planning outreach for: {proposal['name']}")
        
        sequence = [
            {
                'day': 1,
                'type': 'email',
                'template': 'initial_value',
                'subject': f"Transforming Operations at {proposal['company']}",
                'focus': proposal['value_props'].split('\n')[0] if proposal['value_props'] else 'Key benefits'
            },
            {
                'day': 3,
                'type': 'email',
                'template': 'roi_focus',
                'subject': f"ROI Analysis: {proposal['name']}",
                'focus': 'Financial impact and payback period'
            },
            {
                'day': 1,
                'type': 'linkedin',
                'action': 'connect',
                'message': f"Interested in discussing how we can help {proposal['company']} achieve similar results"
            },
            {
                'day': 7,
                'type': 'email',
                'template': 'social_proof',
                'subject': 'Success Stories Similar to Your Needs',
                'focus': 'Case studies from similar organizations'
            },
            {
                'day': 14,
                'type': 'email',
                'template': 'direct_ask',
                'subject': 'Next Steps - Demo or Technical Discussion?',
                'focus': 'Call to action: schedule meeting'
            }
        ]
        
        campaign['sequence'] = sequence
        campaign['stage'] = 'active_outreach'
        campaign['sequence_start'] = datetime.now().isoformat()
        campaign['next_action'] = {
            'action': 'send_initial_emails',
            'scheduled_at': datetime.now().isoformat(),
            'description': 'Sending Day 1 emails to all stakeholders'
        }
        
        self._save_json(self.campaigns_file, self.campaigns)
        self._log(f"✅ Outreach sequence planned ({len(sequence)} touches)")
    
    def _execute_outreach(self, proposal, campaign):
        """
        Execute scheduled outreach touches
        
        In production:
        - Send emails via Outlook API
        - Execute LinkedIn actions via MeetAlfred API
        - Track delivery and opens
        """
        self._log(f"📤 Executing outreach for: {proposal['name']}")
        
        # Check which touches are due
        start_date = datetime.fromisoformat(campaign['sequence_start'])
        now = datetime.now()
        days_elapsed = (now - start_date).days
        
        for touch in campaign['sequence']:
            if touch['day'] <= days_elapsed:
                touch_id = f"{touch['day']}_{touch['type']}"
                
                # Check if already executed
                if touch_id in [t['id'] for t in campaign.get('touches', [])]:
                    continue
                
                # Execute touch
                result = self._send_touch(proposal, campaign, touch)
                
                # Log touch
                campaign.setdefault('touches', []).append({
                    'id': touch_id,
                    'executed_at': now.isoformat(),
                    'type': touch['type'],
                    'result': result
                })
        
        # Move to monitoring stage
        campaign['stage'] = 'monitoring'
        campaign['next_action'] = {
            'action': 'monitor_engagement',
            'scheduled_at': (now + timedelta(days=1)).isoformat(),
            'description': 'Monitoring responses and engagement'
        }
        
        self._save_json(self.campaigns_file, self.campaigns)
    
    def _send_touch(self, proposal, campaign, touch):
        """
        Send individual touch (email or LinkedIn)
        
        In production: actual API calls
        For MVP: simulate
        """
        if touch['type'] == 'email':
            self._log(f"  📧 Email: {touch['subject']}")
            # Would call Outlook API here
            return {'status': 'sent', 'recipients': len(campaign['stakeholders'])}
        
        elif touch['type'] == 'linkedin':
            self._log(f"  💼 LinkedIn: {touch['action']}")
            # Would call MeetAlfred API here
            return {'status': 'queued', 'recipients': len(campaign['stakeholders'])}
    
    def _monitor_engagement(self, proposal, campaign):
        """
        Monitor engagement and adapt strategy
        
        Track:
        - Email opens/clicks
        - LinkedIn connection accepts/replies
        - Website visits (if proposal URL tracked)
        - Buying signals in responses
        """
        self._log(f"👁️  Monitoring engagement for: {proposal['name']}")
        
        # In production: fetch real engagement data
        # For MVP: simulate
        engagement_score = 35  # Would be calculated from real data
        
        proposal['engagement_score'] = engagement_score
        
        # Detect buying signals
        if engagement_score > 60:
            self._alert_hot_lead(proposal, campaign)
        
        campaign['next_action'] = {
            'action': 'monitor_engagement',
            'scheduled_at': (datetime.now() + timedelta(days=1)).isoformat(),
            'description': f'Engagement: {engagement_score}% - Continue monitoring'
        }
        
        self._save_json(self.proposals_file, self.proposals)
        self._save_json(self.campaigns_file, self.campaigns)
    
    def _alert_hot_lead(self, proposal, campaign):
        """Alert Ali when a hot lead is detected"""
        self._log(f"🔥 HOT LEAD DETECTED: {proposal['name']}")
        # In production: send Telegram alert
    
    def get_status_report(self):
        """Generate status report for dashboard"""
        active = [p for p in self.proposals if p['status'] == 'active']
        won = [p for p in self.proposals if p['status'] == 'won']
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_proposals': len(self.proposals),
            'active_campaigns': len(active),
            'won': len(won),
            'win_rate': round(len(won) / len(self.proposals) * 100) if self.proposals else 0,
            'campaigns': []
        }
        
        for proposal in self.proposals:
            campaign = self.campaigns.get(proposal['id'], {})
            report['campaigns'].append({
                'id': proposal['id'],
                'name': proposal['name'],
                'company': proposal['company'],
                'status': proposal['status'],
                'engagement': proposal.get('engagement_score', 0),
                'next_action': campaign.get('next_action', {}).get('description', 'Initializing...')
            })
        
        return report


def main():
    """Main entry point for Serena agent"""
    serena = SerenaAgent()
    
    print("🎯 Serena Agent - AI Sales Acceleration")
    print("=" * 50)
    
    # Process all active campaigns
    serena.process_campaigns()
    
    # Generate status report
    report = serena.get_status_report()
    print(f"\n📊 Status Report:")
    print(f"   Active Campaigns: {report['active_campaigns']}")
    print(f"   Total Proposals: {report['total_proposals']}")
    print(f"   Win Rate: {report['win_rate']}%")


if __name__ == "__main__":
    main()
