from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ContextAgent:
    def __init__(self, model_name="gemma3:4b"):
        self.llm = ChatOllama(model=model_name)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a financial crime investigator assistant. Your job is to extract and summarize key context from an alert. "
                       "Identify the Who, What, When, Where, and How Much. "
                       "Format the output as a concise summary."),
            ("user", "Alert Data: {alert_data}\n\nCustomer Profile: {customer_profile}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def analyze(self, alert_data, customer_profile):
        return self.chain.invoke({"alert_data": alert_data, "customer_profile": customer_profile})

if __name__ == "__main__":
    # Test
    agent = ContextAgent()
    print(agent.analyze({"amount": 10000}, {"name": "Test"}))
