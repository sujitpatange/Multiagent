import datetime
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Type

@dataclass
class Event:
    """Base event class."""
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class PaymentObserved(Event):
    """
    Emitted every time a payment (credit or debit) passes through the core system for a monitored account.
    """
    account_id: str = ""
    amount: float = 0.0
    direction: str = "IN"  # "IN" or "OUT"

@dataclass
class BalanceWindowUpdated(Event):
    """
    Emitted when a burst of in/out movement is detected in a short window for an account.
    """
    account_id: str = ""
    in_last_30m: float = 0.0
    out_last_30m: float = 0.0
    net_change_last_30m: float = 0.0

@dataclass
class FastCashoutAlertRaised(Event):
    """
    Emitted when the simple condition is met:
    outbound in 30 minutes ≥ 80% of inbound in 30 minutes.
    """
    account_id: str = ""
    in_last_30m: float = 0.0
    out_last_30m: float = 0.0
    ratio: float = 0.0
    first_txn_time: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_txn_time: datetime.datetime = field(default_factory=datetime.datetime.now)

class EventBus:
    """Simple in-memory event bus implementing the Observer pattern."""
    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: Type[Event], callback: Callable[[Event], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event: Event):
        # Notify subscribers of this specific event type
        event_type = type(event)
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event)
