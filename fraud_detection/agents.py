import datetime
from collections import defaultdict
from typing import List, Dict
from events import EventBus, PaymentObserved, BalanceWindowUpdated, FastCashoutAlertRaised

class IngestionAgent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def ingest(self, account_id: str, amount: float, direction: str, timestamp: datetime.datetime):
        """Wraps raw transaction data into a PaymentObserved event."""
        event = PaymentObserved(
            timestamp=timestamp,
            account_id=account_id,
            amount=amount,
            direction=direction
        )
        self.event_bus.publish(event)

class RollingWindowAgent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        # Stores list of PaymentObserved events per account
        self.account_transactions: Dict[str, List[PaymentObserved]] = defaultdict(list)
        self.event_bus.subscribe(PaymentObserved, self.on_payment_observed)

    def on_payment_observed(self, event: PaymentObserved):
        account_id = event.account_id
        
        # Add new payment
        self.account_transactions[account_id].append(event)
        
        # Sort by timestamp (though likely already sorted if ingested in order, good to be safe)
        self.account_transactions[account_id].sort(key=lambda x: x.timestamp)
        
        # Filter window: Keep only transactions within last 30 minutes of THIS event's timestamp
        # NOTE: Using the event's timestamp as "now" allows for simulation with historical data.
        current_time = event.timestamp
        window_start = current_time - datetime.timedelta(minutes=30)
        
        # Prune old transactions
        self.account_transactions[account_id] = [
            tx for tx in self.account_transactions[account_id] 
            if tx.timestamp > window_start
        ]
        
        # Calculate stats
        active_window = self.account_transactions[account_id]
        in_last_30m = sum(tx.amount for tx in active_window if tx.direction == "IN")
        out_last_30m = sum(tx.amount for tx in active_window if tx.direction == "OUT")
        net_change = in_last_30m - out_last_30m
        
        # Publish update
        update_event = BalanceWindowUpdated(
            timestamp=current_time,
            account_id=account_id,
            in_last_30m=in_last_30m,
            out_last_30m=out_last_30m,
            net_change_last_30m=net_change
        )
        self.event_bus.publish(update_event)

class FastCashoutDetectorAgent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe(BalanceWindowUpdated, self.on_balance_updated)

    def on_balance_updated(self, event: BalanceWindowUpdated):
        # We will use the LLM to decide if this is suspicious.
        # We only query if there is some activity to analyze.
        if event.in_last_30m == 0 and event.out_last_30m == 0:
            return

        import json
        import urllib.request
        import urllib.error

        # Calculate ratio in Python to help the LLM (small models struggle with arithmetic)
        ratio = 0.0
        if event.in_last_30m > 0:
            ratio = event.out_last_30m / event.in_last_30m

        # Construct the prompt
        prompt = f"""
        Analyze bank account activity for 'fast cash-out' fraud (high outbound relative to inbound).
        
        Rule: SUSPICIOUS only if Ratio >= 0.8. Otherwise SAFE.
        
        Examples:
        Input: Inbound=1000, Outbound=900, Ratio=0.90
        Output: {{ "suspicious": true, "reason": "Ratio 0.90 >= 0.8 indicates money muling." }}
        
        Input: Inbound=1000, Outbound=0, Ratio=0.00
        Output: {{ "suspicious": false, "reason": "Ratio 0.00 is safe." }}
        
        Input: Inbound=1000, Outbound=50, Ratio=0.05
        Output: {{ "suspicious": false, "reason": "Ratio 0.05 is safe." }}
        
        Input: Inbound=1000, Outbound=200, Ratio=0.20
        Output: {{ "suspicious": false, "reason": "Ratio 0.20 is below 0.8 threshold." }}
        
        Input: Inbound=1000, Outbound=400, Ratio=0.40
        Output: {{ "suspicious": false, "reason": "Ratio 0.40 is below 0.8 threshold." }}
        
        Input: Inbound=5000, Outbound=4500, Ratio=0.90
        Output: {{ "suspicious": true, "reason": "Ratio 0.90 is high." }}

        Now analyze this:
        Input: Inbound={event.in_last_30m}, Outbound={event.out_last_30m}, Ratio={ratio:.2f}
        Output: (Return only JSON)
        """

        data = {
            "model": "gemma3:4b",
            "prompt": prompt,
            "stream": False,
            "format": "json" 
        }

        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                llm_response_text = result.get("response", "{}")
                decision = json.loads(llm_response_text)
                
                is_suspicious = decision.get("suspicious", False)
                reason = decision.get("reason", "No reason provided")

                if is_suspicious:
                    # Capture the ratio for the event payload if possible, or 1.0 if div by zero
                    ratio = 0.0
                    if event.in_last_30m > 0:
                        ratio = event.out_last_30m / event.in_last_30m
                    
                    alert = FastCashoutAlertRaised(
                        timestamp=event.timestamp,
                        account_id=event.account_id,
                        in_last_30m=event.in_last_30m,
                        out_last_30m=event.out_last_30m,
                        ratio=ratio,
                        first_txn_time=event.timestamp - datetime.timedelta(minutes=30),
                        last_txn_time=event.timestamp
                    )
                    # We might want to inject the reason into the event, but for now we follow the existing schema
                    # or print it.
                    print(f"DEBUG: LLM Reason for {event.account_id}: {reason}")
                    self.event_bus.publish(alert)

        except Exception as e:
            print(f"Error calling LLM: {e}")

