import sys
import os
from agents.supervisor import Supervisor
from utils.mock_data import SAMPLE_ALERTS, CUSTOMER_PROFILES

def main():
    print("Initializing Financial Crime Investigation System...")
    try:
        supervisor = Supervisor()
    except Exception as e:
        print(f"Error initializing supervisor: {e}")
        print("Ensure Ollama is running and the model is available.")
        return

    print(f"Found {len(SAMPLE_ALERTS)} alerts to investigate.")

    for alert in SAMPLE_ALERTS:
        alert_id = alert["alert_id"]
        customer_id = alert["customer_id"]
        customer_profile = CUSTOMER_PROFILES.get(customer_id, {})
        
        print(f"\n{'='*50}")
        print(f"Investigating Alert: {alert_id}")
        print(f"Customer: {customer_profile.get('name', 'Unknown')}")
        print(f"{'='*50}")

        try:
            result = supervisor.investigate(alert, customer_profile)
            
            print("\n--- INVESTIGATION REPORT ---")
            print(f"\n[Context Summary]\n{result['context_summary']}")
            print(f"\n[Typology Findings]\n{result['typology_findings']}")
            print(f"\n[Final Recommendation]\n{result['final_recommendation']}")
            
        except Exception as e:
            print(f"Error investigating alert {alert_id}: {e}")

if __name__ == "__main__":
    main()
