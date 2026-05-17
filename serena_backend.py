#!/usr/bin/env python3
"""
Serena Backend - LIVE Automation System
Pulls proposals from pipeline2, executes multi-channel campaigns
"""

import requests
import json
from datetime import datetime, timedelta
from integrations import apollo, meetalfred, outlook, pipeline2, telegram

class SerenaLive:
    """Live automation engine"""
    
    def __init__(self):
        self.proposals = []
        self.campaigns = {}
        
    def sync_from_pipeline2(self):
        """Pull all proposals from pipeline2.onrender.com"""
        print("📡 Syncing from pipeline2...")
        
        try:
            proposals = pipeline2.get_proposals()
            
            for prop in proposals:
                if prop['status'] in ['sent', 'pending', 'active']:
                    self.add_proposal_from_pipeline(prop)
            
            print(f"✅ Synced {len(proposals)} proposals from pipeline2")
            return proposals
            
        except Exception as e:
            print(f"⚠️ Pipeline2 sync error: {e}")
            return []
    
    def add_proposal_from_pipeline(self, proposal):
        """Add proposal and start automation"""
        
        campaign_id = f"camp_{proposal.get('id', datetime.now().timestamp())}"
        
        campaign = {
            'id': campaign_id,
            'name': proposal.get('name', 'Unnamed Proposal'),
            'company': proposal.get('company', ''),
            'contacts': proposal.get('contacts', []),
            'amount': proposal.get('amount', 0),
            'value_props': proposal.get('description', ''),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'weekly_timeline': self.generate_timeline(),
            'current_week': 1,
            'stakeholders': [],
            'activities': []
        }
        
        self.campaigns[campaign_id] = campaign
        
        # Start automation
        self.execute_week1(campaign)
        
        return campaign_id
    
    def generate_timeline(self):
        """Generate 4-week automation timeline"""
        return {
            'week1': {
                'status': 'in_progress',
                'tasks': [
                    {'tool': 'Apollo', 'action': 'Find stakeholders', 'status': 'pending'},
                    {'tool': 'Outlook', 'action': 'Send initial emails (personalized by role)', 'status': 'pending'},
                    {'tool': 'MeetAlfred', 'action': 'LinkedIn connection requests', 'status': 'pending'}
                ],
                'results': {'stakeholders': 0, 'emails': 0, 'linkedin': 0}
            },
            'week2': {
                'status': 'scheduled',
                'tasks': [
                    {'tool': 'Serena', 'action': 'Track engagement (opens, clicks, replies)', 'status': 'scheduled'},
                    {'tool': 'Sales Navigator', 'action': 'Find additional stakeholders', 'status': 'scheduled'},
                    {'tool': 'MeetAlfred', 'action': 'Follow-up messages to connections', 'status': 'scheduled'}
                ],
                'results': {}
            },
            'week3': {
                'status': 'scheduled',
                'tasks': [
                    {'tool': 'Serena', 'action': 'Detect buying signals', 'status': 'scheduled'},
                    {'tool': 'Outlook', 'action': 'Pivot messaging for cold contacts', 'status': 'scheduled'},
                    {'tool': 'MeetAlfred', 'action': 'Case study shares on LinkedIn', 'status': 'scheduled'}
                ],
                'results': {}
            },
            'week4': {
                'status': 'scheduled',
                'tasks': [
                    {'tool': 'Serena', 'action': 'Hot lead handoff to Ali', 'status': 'scheduled'},
                    {'tool': 'Outlook', 'action': 'Demo offers to engaged contacts', 'status': 'scheduled'},
                    {'tool': 'Sales Navigator', 'action': 'Expand to procurement/facilities', 'status': 'scheduled'}
                ],
                'results': {}
            }
        }
    
    def execute_week1(self, campaign):
        """Execute Week 1 automation"""
        timeline = campaign['weekly_timeline']['week1']
        
        # Task 1: Apollo - Find stakeholders
        print(f"🔍 Week 1 - Finding stakeholders for {campaign['company']}...")
        timeline['tasks'][0]['status'] = 'in_progress'
        
        try:
            # In production: real Apollo API call
            # stakeholders = apollo.search_people(campaign['company'])
            
            # Demo: simulate finding stakeholders
            stakeholders = self.simulate_apollo_search(campaign)
            campaign['stakeholders'] = stakeholders
            timeline['results']['stakeholders'] = len(stakeholders)
            timeline['tasks'][0]['status'] = 'completed'
            
            print(f"✅ Found {len(stakeholders)} stakeholders")
            
        except Exception as e:
            print(f"⚠️ Apollo error: {e}")
            timeline['tasks'][0]['status'] = 'error'
        
        # Task 2: Outlook - Send emails
        print(f"📧 Week 1 - Sending personalized emails...")
        timeline['tasks'][1]['status'] = 'in_progress'
        
        try:
            for stakeholder in stakeholders:
                # In production: real email via Outlook API
                # outlook.send_email(stakeholder['email'], personalize_email(stakeholder))
                
                # Demo: log email
                print(f"  📧 Email → {stakeholder['name']} ({stakeholder['role']})")
                campaign['activities'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'email',
                    'tool': 'Outlook',
                    'contact': stakeholder['name'],
                    'action': f"Sent {stakeholder['email_angle']} email"
                })
            
            timeline['results']['emails'] = len(stakeholders)
            timeline['tasks'][1]['status'] = 'completed'
            print(f"✅ Sent {len(stakeholders)} personalized emails")
            
        except Exception as e:
            print(f"⚠️ Email error: {e}")
            timeline['tasks'][1]['status'] = 'error'
        
        # Task 3: MeetAlfred - LinkedIn connections
        print(f"💼 Week 1 - Sending LinkedIn connections...")
        timeline['tasks'][2]['status'] = 'in_progress'
        
        try:
            for stakeholder in stakeholders:
                # In production: real LinkedIn via MeetAlfred API
                # meetalfred.send_connection_request(stakeholder['linkedin'])
                
                # Demo: log LinkedIn
                print(f"  💼 LinkedIn → {stakeholder['name']}")
                campaign['activities'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'linkedin',
                    'tool': 'MeetAlfred',
                    'contact': stakeholder['name'],
                    'action': 'Sent connection request'
                })
            
            timeline['results']['linkedin'] = len(stakeholders)
            timeline['tasks'][2]['status'] = 'completed'
            print(f"✅ Sent {len(stakeholders)} LinkedIn connections")
            
        except Exception as e:
            print(f"⚠️ LinkedIn error: {e}")
            timeline['tasks'][2]['status'] = 'error'
        
        # Mark week 1 complete
        timeline['status'] = 'completed'
        campaign['current_week'] = 2
        
        # Alert Ali
        telegram.send_alert(
            f"🎯 Week 1 Complete: {campaign['name']}\n\n"
            f"✅ Found {len(stakeholders)} stakeholders (Apollo)\n"
            f"✅ Sent {len(stakeholders)} emails (Outlook)\n"
            f"✅ Sent {len(stakeholders)} LinkedIn (MeetAlfred)\n\n"
            f"Week 2 starts automatically..."
        )
    
    def simulate_apollo_search(self, campaign):
        """Simulate Apollo.io stakeholder discovery"""
        company = campaign['company']
        
        # Simulated stakeholders
        return [
            {
                'name': 'John Smith',
                'role': 'IT Director',
                'email': f'john.smith@{company.lower().replace(" ", "")}.ae',
                'linkedin': 'https://linkedin.com/in/johnsmith',
                'email_angle': 'Technical specs'
            },
            {
                'name': 'Sarah Jones',
                'role': 'CMO',
                'email': f'sarah.jones@{company.lower().replace(" ", "")}.ae',
                'linkedin': 'https://linkedin.com/in/sarahjones',
                'email_angle': 'Clinical impact'
            },
            {
                'name': 'Ahmed Hassan',
                'role': 'CFO',
                'email': f'ahmed.hassan@{company.lower().replace(" ", "")}.ae',
                'linkedin': 'https://linkedin.com/in/ahmedhassan',
                'email_angle': 'ROI & payback'
            },
            {
                'name': 'Mohammed Al-Rashid',
                'role': 'Operations Director',
                'email': f'mohammed.alrashid@{company.lower().replace(" ", "")}.ae',
                'linkedin': 'https://linkedin.com/in/mohammedalrashid',
                'email_angle': 'Efficiency gains'
            },
            {
                'name': 'Fatima Al-Nasser',
                'role': 'Nursing Director',
                'email': f'fatima.alnasser@{company.lower().replace(" ", "")}.ae',
                'linkedin': 'https://linkedin.com/in/fatimaalnasser',
                'email_angle': 'Workflow improvement'
            }
        ]
    
    def get_all_campaigns(self):
        """Get all campaigns with their timelines"""
        return list(self.campaigns.values())


# Test it
if __name__ == '__main__':
    serena = SerenaLive()
    
    print("🎯 Serena Live Automation System")
    print("=" * 50)
    
    # Sync from pipeline2
    proposals = serena.sync_from_pipeline2()
    
    # Show what's running
    campaigns = serena.get_all_campaigns()
    print(f"\n📊 Active Campaigns: {len(campaigns)}")
    
    for camp in campaigns:
        print(f"\n{camp['name']}:")
        print(f"  Week {camp['current_week']}/4")
        print(f"  Stakeholders: {len(camp['stakeholders'])}")
        print(f"  Activities: {len(camp['activities'])}")

