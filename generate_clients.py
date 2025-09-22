import csv
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any

from config import Config

class ClientDataGenerator:
    def __init__(self):
        self.first_names = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
            "Ivy", "Jack", "Karen", "Leo", "Mia", "Noah", "Olivia", "Peter",
            "Quinn", "Ruby", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xavier",
            "Yara", "Zoe", "Alex", "Blake", "Casey", "Drew", "Ellis", "Finley",
            "Gray", "Harper", "Indigo", "Jesse", "Kendall", "Lane", "Morgan",
            "Nico", "Oakley", "Phoenix", "River", "Sage", "Taylor", "Unique"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
            "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
            "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
        ]
        
        self.domains = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "company.com",
            "example.org", "test.net", "sample.co", "demo.io", "client.biz"
        ]
        
        self.message_templates = [
            "Hello, I need help with my account",
            "Can you help me with a technical issue?",
            "I have a question about your service",
            "I'm experiencing problems with login",
            "Could you explain how this feature works?",
            "I need assistance with billing",
            "There's an error in my order",
            "Can you help me reset my password?",
            "I want to upgrade my plan",
            "I need help with configuration",
            "My account is not working properly",
            "I have a complaint about the service",
            "Can you provide more information?",
            "I'm having trouble accessing my data",
            "The system is running slowly",
            "I need help with integration",
            "Can you check my account status?",
            "I want to cancel my subscription",
            "There's a bug in the application",
            "I need training on how to use this"
        ]
        
        self.chat_responses = [
            "Thank you for your help!",
            "That solved my problem.",
            "I understand now.",
            "Could you clarify that?",
            "Let me try that solution.",
            "That's exactly what I needed.",
            "I'm still having issues.",
            "Can you provide more details?",
            "That worked perfectly!",
            "I'll follow up if I need more help.",
            "Great service, thanks!",
            "I appreciate your patience.",
            "That's not quite what I meant.",
            "Perfect, that's clear now.",
            "I'll implement that change.",
            "Could you walk me through it again?",
            "That's very helpful.",
            "I think I understand better now.",
            "Let me test that.",
            "Thanks for the quick response!"
        ]
    
    def generate_client_data(self, num_clients: int = 1000) -> List[Dict[str, Any]]:
        """Generate client data for load testing"""
        clients = []
        
        for i in range(num_clients):
            # Generate basic info
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            client_name = f"{first_name}_{last_name}_{i+1:04d}"
            
            # Generate email
            domain = random.choice(self.domains)
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@{domain}"
            
            # Generate session preferences
            preferred_server = random.choice(["Server_A", "Server_B", "Server_C", "Any"])
            session_duration = random.randint(60, 1800)  # 1-30 minutes
            message_count = random.randint(5, 50)
            
            # Generate chat behavior
            initial_message = random.choice(self.message_templates)
            response_pattern = random.choice(["quick", "medium", "slow", "random"])
            
            # Generate rating tendency
            rating_tendency = random.choice(["positive", "neutral", "negative", "random"])
            
            # Generate arrival time (spread over 24 hours)
            arrival_offset = random.randint(0, 86400)  # seconds in a day
            
            client_data = {
                'client_id': i + 1,
                'client_name': client_name,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'preferred_server': preferred_server,
                'session_duration': session_duration,
                'message_count': message_count,
                'initial_message': initial_message,
                'response_pattern': response_pattern,
                'rating_tendency': rating_tendency,
                'arrival_offset': arrival_offset,
                'priority': random.choice(["low", "medium", "high"]),
                'client_type': random.choice(["new", "returning", "premium"]),
                'expected_wait_tolerance': random.randint(30, 600),  # seconds
                'chat_complexity': random.choice(["simple", "medium", "complex"]),
                'technical_level': random.choice(["beginner", "intermediate", "advanced"]),
                'satisfaction_threshold': random.randint(2, 5),
                'retry_attempts': random.randint(1, 3),
                'preferred_response_time': random.randint(5, 60),  # seconds
                'session_goal': random.choice([
                    "support", "information", "complaint", "purchase", "technical"
                ])
            }
            
            clients.append(client_data)
        
        return clients
    
    def generate_chat_simulation_data(self, client_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate chat simulation data for a specific client"""
        chat_data = []
        
        # Initial message
        chat_data.append({
            'timestamp': 0,
            'sender': 'client',
            'message': client_data['initial_message'],
            'message_type': 'initial'
        })
        
        # Generate conversation flow
        message_count = client_data['message_count']
        response_pattern = client_data['response_pattern']
        
        for i in range(1, message_count):
            # Determine response time based on pattern
            if response_pattern == "quick":
                response_time = random.randint(1, 10)
            elif response_pattern == "medium":
                response_time = random.randint(10, 30)
            elif response_pattern == "slow":
                response_time = random.randint(30, 120)
            else:  # random
                response_time = random.randint(1, 60)
            
            # Determine sender (simulate server responses)
            if i % 2 == 0:
                sender = 'server'
                message = f"Server response {i//2}"
            else:
                sender = 'client'
                message = random.choice(self.chat_responses)
            
            chat_data.append({
                'timestamp': sum(item['timestamp'] for item in chat_data[-3:]) + response_time,
                'sender': sender,
                'message': message,
                'message_type': 'response'
            })
        
        # Generate final rating
        rating = self._generate_rating(client_data['rating_tendency'])
        chat_data.append({
            'timestamp': chat_data[-1]['timestamp'] + random.randint(5, 30),
            'sender': 'client',
            'message': f"Rating: {rating}",
            'message_type': 'rating'
        })
        
        return chat_data
    
    def _generate_rating(self, tendency: str) -> int:
        """Generate rating based on tendency"""
        if tendency == "positive":
            return random.choice([4, 5, 5, 5])
        elif tendency == "negative":
            return random.choice([1, 2, 2, 3])
        elif tendency == "neutral":
            return random.choice([3, 3, 4])
        else:  # random
            return random.randint(1, 5)
    
    def save_to_csv(self, clients: List[Dict[str, Any]], filename: str = "clients.csv"):
        """Save client data to CSV file"""
        if not clients:
            print("No client data to save")
            return
        
        fieldnames = clients[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clients)
        
        print(f"Saved {len(clients)} clients to {filename}")
    
    def generate_load_test_scenarios(self, num_scenarios: int = 10) -> List[Dict[str, Any]]:
        """Generate different load test scenarios"""
        scenarios = []
        
        for i in range(num_scenarios):
            scenario = {
                'scenario_id': i + 1,
                'name': f"LoadTest_Scenario_{i+1}",
                'description': f"Load test scenario {i+1}",
                'client_count': random.randint(50, 500),
                'duration': random.randint(300, 3600),  # 5-60 minutes
                'arrival_rate': random.choice([1, 2, 5, 10, 20]),  # clients per second
                'server_count': random.randint(1, 5),
                'concurrent_limit': random.randint(10, 100),
                'target_response_time': random.randint(1, 10),  # seconds
                'expected_throughput': random.randint(10, 100),  # messages per second
                'stress_level': random.choice(["low", "medium", "high", "extreme"]),
                'test_type': random.choice(["load", "stress", "endurance", "spike"])
            }
            scenarios.append(scenario)
        
        return scenarios
    
    def create_performance_profiles(self) -> List[Dict[str, Any]]:
        """Create different performance testing profiles"""
        profiles = [
            {
                'profile_name': 'Normal_Load',
                'description': 'Normal business hours load',
                'client_count': 100,
                'arrival_rate': 2,
                'session_duration': 300,
                'server_count': 3,
                'expected_rating': 4.0
            },
            {
                'profile_name': 'Peak_Load',
                'description': 'Peak hours with high traffic',
                'client_count': 500,
                'arrival_rate': 10,
                'session_duration': 600,
                'server_count': 3,
                'expected_rating': 3.5
            },
            {
                'profile_name': 'Stress_Test',
                'description': 'Stress test with overload',
                'client_count': 1000,
                'arrival_rate': 20,
                'session_duration': 900,
                'server_count': 3,
                'expected_rating': 3.0
            },
            {
                'profile_name': 'Endurance_Test',
                'description': 'Long duration test',
                'client_count': 200,
                'arrival_rate': 5,
                'session_duration': 1800,
                'server_count': 3,
                'expected_rating': 4.2
            },
            {
                'profile_name': 'Spike_Test',
                'description': 'Sudden traffic spike',
                'client_count': 300,
                'arrival_rate': 50,
                'session_duration': 120,
                'server_count': 3,
                'expected_rating': 2.5
            }
        ]
        
        return profiles

def main():
    """Main function to generate test data"""
    generator = ClientDataGenerator()
    
    # Generate client data
    print("Generating client data...")
    clients = generator.generate_client_data(1000)
    generator.save_to_csv(clients, "clients.csv")
    
    # Generate load test scenarios
    print("Generating load test scenarios...")
    scenarios = generator.generate_load_test_scenarios(10)
    generator.save_to_csv(scenarios, "load_test_scenarios.csv")
    
    # Generate performance profiles
    print("Generating performance profiles...")
    profiles = generator.create_performance_profiles()
    generator.save_to_csv(profiles, "performance_profiles.csv")
    
    # Generate sample chat data for first 10 clients
    print("Generating sample chat data...")
    chat_data_all = []
    for i, client in enumerate(clients[:10]):
        chat_data = generator.generate_chat_simulation_data(client)
        for chat_entry in chat_data:
            chat_entry['client_id'] = client['client_id']
            chat_entry['client_name'] = client['client_name']
            chat_data_all.append(chat_entry)
    
    generator.save_to_csv(chat_data_all, "sample_chat_data.csv")
    
    print("\nData generation complete!")
    print(f"Generated {len(clients)} clients")
    print(f"Generated {len(scenarios)} load test scenarios")
    print(f"Generated {len(profiles)} performance profiles")
    print(f"Generated {len(chat_data_all)} sample chat messages")

if __name__ == "__main__":
    main()