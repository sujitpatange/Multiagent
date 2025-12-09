from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class TypologyAgent:
    def __init__(self, model_name="gemma3:4b"):
        self.llm = ChatOllama(model=model_name)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a financial crime typology expert. Analyze the alert context and determine if it matches any known red flags or typologies (e.g., Structuring, Smurfing, Money Mule, Terrorist Financing, Sanctions Evasion). "
                       "Provide a list of matched typologies with reasoning."),
            ("user", "Alert Context: {context}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def analyze(self, context):
        return self.chain.invoke({"context": context})
