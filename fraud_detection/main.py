import datetime
from events import EventBus, FastCashoutAlertRaised
from agents import IngestionAgent, RollingWindowAgent, FastCashoutDetectorAgent

def run_simulation():
    # 1. Setup
    print("--- Setting up Fraud Detection System ---")
    event_bus = EventBus()
    
    # Initialize Agents
    ingestion = IngestionAgent(event_bus)
    rolling_window = RollingWindowAgent(event_bus)
    detector = FastCashoutDetectorAgent(event_bus)
    
    # Subscribe a simple printer for Alerts
    def alert_handler(event: FastCashoutAlertRaised):
        print(f"\n[!!!] ALERT RAISED [!!!]")
        print(f"Account: {event.account_id}")
        print(f"Time: {event.timestamp}")
        print(f"In (30m): ${event.in_last_30m:.2f}")
        print(f"Out (30m): ${event.out_last_30m:.2f}")
        print(f"Ratio: {event.ratio:.2f}")
        print("-" * 30)

    event_bus.subscribe(FastCashoutAlertRaised, alert_handler)
    
    # 2. Simulation Scenario 1: Fraud Pattern
    print("\n--- Starting Scenario 1: Fast Cash-out (Fraud Pattern) ---")
    account_fraud = "ACC_FRAUD_001"
    start_time = datetime.datetime.now()
    
    # Event 1: Inbound Salary ($1000) at T=0
    print(f"T=0: Inbound Salary $1000 for {account_fraud}")
    ingestion.ingest(account_fraud, 1000.0, "IN", start_time)
    
    # Event 2: Outbound Transfer ($900) at T+20m
    t_plus_20 = start_time + datetime.timedelta(minutes=20)
    print(f"T+20m: Outbound Transfer $900 for {account_fraud}")
    ingestion.ingest(account_fraud, 900.0, "OUT", t_plus_20)
    
    # 3. Simulation Scenario 2: Benign Pattern
    print("\n--- Starting Scenario 2: Normal Activity (Benign) ---")
    account_benign = "ACC_NORMAL_001"
    
    # Event 1: Inbound Salary ($1000) at T=0
    print(f"T=0: Inbound Salary $1000 for {account_benign}")
    ingestion.ingest(account_benign, 1000.0, "IN", start_time)
    
    # Event 2: Small Spending ($50) at T+10m
    t_plus_10 = start_time + datetime.timedelta(minutes=10)
    print(f"T+10m: Outbound Spending $50 for {account_benign}")
    ingestion.ingest(account_benign, 50.0, "OUT", t_plus_10)
    
    # Event 3: Another Spending ($100) at T+25m
    t_plus_25 = start_time + datetime.timedelta(minutes=25)
    print(f"T+25m: Outbound Spending $100 for {account_benign}")
    ingestion.ingest(account_benign, 100.0, "OUT", t_plus_25)
    
    # Total Out = 150, In = 1000, Ratio = 0.15 (Should be NO ALERT)
    
    print("\n--- Simulation Complete ---")

if __name__ == "__main__":
    run_simulation()
