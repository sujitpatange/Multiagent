from common.spoke_base import BaseSpoke
from common.models import Transaction, Finding, SpokeCapability
import json

class FraudSpoke(BaseSpoke):
    def get_capabilities(self):
        return [SpokeCapability.FRAUD]

    def process_transaction(self, transaction: Transaction) -> Finding:
        prompt = f"""
        Analyze the following transaction for potential FRAUD.
        Transaction Amount: {transaction.amount} {transaction.currency}
        Sender ID: {transaction.sender_id}
        Receiver ID: {transaction.receiver_id}
        Metadata: {transaction.metadata}

        Return your finding in EXACT JSON format:
        {{
            "severity": "LOW/MEDIUM/HIGH",
            "score": 0.0 to 1.0,
            "rationale": "Short explanation",
            "action_item": "Recommended action"
        }}
        """
        
        response_text = self.llm.generate(prompt, system_prompt="You are a Fraud Detection Expert.")
        
        # Extract JSON from response (naive extraction for demo)
        try:
            # Look for the first '{' and last '}'
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            data = json.loads(response_text[start:end])
            return Finding(
                spoke_name=self.name,
                severity=data.get("severity", "LOW"),
                score=data.get("score", 0.0),
                rationale=data.get("rationale", "No rationale provided"),
                action_item=data.get("action_item", "None")
            )
        except Exception:
            return Finding(
                spoke_name=self.name,
                severity="MEDIUM",
                score=0.5,
                rationale=f"Error parsing LLM response: {response_text[:50]}...",
                action_item="Manual Review"
            )

class AMLSpoke(BaseSpoke):
    def get_capabilities(self):
        return [SpokeCapability.AML]

    def process_transaction(self, transaction: Transaction) -> Finding:
        prompt = f"""
        Analyze the following transaction for potential Anti-Money Laundering (AML) risks.
        Transaction Amount: {transaction.amount} {transaction.currency}
        Sender ID: {transaction.sender_id}
        Receiver ID: {transaction.receiver_id}

        Return your finding in EXACT JSON format:
        {{
            "severity": "LOW/MEDIUM/HIGH",
            "score": 0.0 to 1.0,
            "rationale": "Short explanation",
            "action_item": "Recommended action"
        }}
        """
        
        response_text = self.llm.generate(prompt, system_prompt="You are an AML Compliance Officer.")
        
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            data = json.loads(response_text[start:end])
            return Finding(
                spoke_name=self.name,
                severity=data.get("severity", "LOW"),
                score=data.get("score", 0.0),
                rationale=data.get("rationale", "No rationale provided"),
                action_item=data.get("action_item", "None")
            )
        except Exception:
            return Finding(
                spoke_name=self.name,
                severity="MEDIUM",
                score=0.5,
                rationale=f"Error parsing LLM response: {response_text[:50]}...",
                action_item="Manual Review"
            )
