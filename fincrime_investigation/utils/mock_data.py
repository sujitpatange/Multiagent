# Mock data for Financial Crime Investigation

SAMPLE_ALERTS = [
    {
        "alert_id": "ALT-2024-001",
        "customer_id": "CUST-98765",
        "alert_type": "High Value Transaction",
        "timestamp": "2024-10-25T14:30:00Z",
        "details": {
            "amount": 150000,
            "currency": "USD",
            "sender_account": "1234567890",
            "beneficiary_account": "0987654321",
            "beneficiary_bank": "Offshore Bank Ltd",
            "beneficiary_country": "Cayman Islands"
        }
    },
    {
        "alert_id": "ALT-2024-002",
        "customer_id": "CUST-12345",
        "alert_type": "Structuring",
        "timestamp": "2024-10-26T09:15:00Z",
        "details": {
            "transactions": [
                {"amount": 9000, "timestamp": "2024-10-26T09:00:00Z"},
                {"amount": 8500, "timestamp": "2024-10-26T09:10:00Z"},
                {"amount": 9500, "timestamp": "2024-10-26T09:15:00Z"}
            ]
        }
    }
]

CUSTOMER_PROFILES = {
    "CUST-98765": {
        "name": "Acme Corp International",
        "risk_rating": "Medium",
        "business_type": "Import/Export",
        "jurisdiction": "USA"
    },
    "CUST-12345": {
        "name": "John Doe",
        "risk_rating": "Low",
        "occupation": "Retail Manager",
        "jurisdiction": "UK"
    }
}
