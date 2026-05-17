#!/usr/bin/env python3
"""
Serena Integrations
Connect to Apollo, MeetAlfred, Outlook, Sales Navigator, Pipeline2
"""

import os
import requests
from datetime import datetime

class ApolloIntegration:
    """Apollo.io API integration for contact enrichment"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('APOLLO_API_KEY')
        self.base_url = "https://api.apollo.io/v1"
    
    def enrich_person(self, email):
        """Enrich contact data from email"""
        if not self.api_key:
            # Mock data for MVP
            return {
                'name': email.split('@')[0].replace('.', ' ').title(),
                'title': 'Director',
                'linkedin': f"https://linkedin.com/in/{email.split('@')[0]}",
                'company': email.split('@')[1].split('.')[0].title()
            }
        
        # Real API call
        headers = {'X-Api-Key': self.api_key}
        response = requests.post(
            f"{self.base_url}/people/match",
            headers=headers,
            json={'email': email}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def search_people(self, company_name, titles=None):
        """Search for people at a company by title"""
        if not self.api_key:
            # Mock for MVP
            return []
        
        headers = {'X-Api-Key': self.api_key}
        params = {
            'organization_name': company_name,
            'person_titles': titles or ['Director', 'Manager', 'VP', 'Chief']
        }
        
        response = requests.post(
            f"{self.base_url}/mixed_people/search",
            headers=headers,
            json=params
        )
        
        if response.status_code == 200:
            return response.json().get('people', [])
        return []


class MeetAlfredIntegration:
    """MeetAlfred API integration for LinkedIn automation"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('MEETALFRED_API_KEY')
        self.base_url = "https://app.meetalfred.com/api/v1"
    
    def send_connection_request(self, linkedin_url, message=None):
        """Send LinkedIn connection request"""
        if not self.api_key:
            # Mock for MVP
            print(f"  💼 [MeetAlfred] Connection request → {linkedin_url}")
            return {'status': 'queued', 'id': f"req_{datetime.now().timestamp()}"}
        
        # Real API call
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.post(
            f"{self.base_url}/connections",
            headers=headers,
            json={
                'linkedin_url': linkedin_url,
                'message': message
            }
        )
        
        return response.json() if response.status_code == 200 else None
    
    def send_message(self, linkedin_url, message):
        """Send LinkedIn message to connection"""
        if not self.api_key:
            # Mock for MVP
            print(f"  💼 [MeetAlfred] Message → {linkedin_url}")
            return {'status': 'sent', 'id': f"msg_{datetime.now().timestamp()}"}
        
        # Real API call
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.post(
            f"{self.base_url}/messages",
            headers=headers,
            json={
                'linkedin_url': linkedin_url,
                'message': message
            }
        )
        
        return response.json() if response.status_code == 200 else None
    
    def create_campaign(self, name, target_urls, sequence):
        """Create automated LinkedIn campaign"""
        if not self.api_key:
            print(f"  💼 [MeetAlfred] Campaign created: {name}")
            return {'campaign_id': f"camp_{datetime.now().timestamp()}"}
        
        # Real API call
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.post(
            f"{self.base_url}/campaigns",
            headers=headers,
            json={
                'name': name,
                'targets': target_urls,
                'sequence': sequence
            }
        )
        
        return response.json() if response.status_code == 200 else None


class OutlookIntegration:
    """Microsoft Outlook API integration via existing skill"""
    
    def __init__(self):
        self.script_path = os.path.expanduser('~/.agents/skills/outlook/scripts/outlook-mail.sh')
    
    def send_email(self, to, subject, body):
        """Send email via Outlook"""
        import subprocess
        
        # Use existing Outlook skill
        result = subprocess.run(
            ['bash', self.script_path, 'send', to, subject, body],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {'status': 'sent', 'to': to}
        else:
            return {'status': 'error', 'error': result.stderr}
    
    def track_opens(self, message_id):
        """Track email opens (placeholder for future tracking pixel)"""
        # TODO: Implement tracking pixel or use Mailtrack API
        return {'opened': False, 'open_count': 0}


class Pipeline2Integration:
    """Pipeline2 integration for reading proposals"""
    
    def __init__(self, base_url="https://pipeline2.onrender.com"):
        self.base_url = base_url
    
    def get_proposals(self):
        """Fetch all proposals from Pipeline2"""
        try:
            response = requests.get(f"{self.base_url}/api/proposals", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Pipeline2 fetch error: {e}")
        
        # Return empty if unavailable
        return []
    
    def update_proposal_status(self, proposal_id, status, notes=None):
        """Update proposal status in Pipeline2"""
        try:
            data = {'status': status}
            if notes:
                data['notes'] = notes
            
            response = requests.patch(
                f"{self.base_url}/api/proposals/{proposal_id}",
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Pipeline2 update error: {e}")
            return False


class TelegramIntegration:
    """Telegram notifications to Ali"""
    
    def __init__(self, chat_id="7910481475"):
        self.chat_id = chat_id
    
    def send_alert(self, message, priority="normal"):
        """Send Telegram alert"""
        # This would use OpenClaw's native messaging
        # For now, just log it
        icon = "🔥" if priority == "high" else "📊"
        print(f"\n{icon} [TELEGRAM ALERT] {message}\n")
        
        # TODO: Use OpenClaw messaging API
        return True
    
    def send_daily_summary(self, campaigns_summary):
        """Send daily summary report"""
        message = "☕ Serena Daily Report:\n\n" + campaigns_summary
        return self.send_alert(message, priority="normal")


# Initialize integrations
apollo = ApolloIntegration()
meetalfred = MeetAlfredIntegration()
outlook = OutlookIntegration()
pipeline2 = Pipeline2Integration()
telegram = TelegramIntegration()
