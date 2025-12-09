from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RecommendationAgent:
    def __init__(self, model_name="gemma3:4b"):
        self.llm = ChatOllama(model=model_name)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior financial crime compliance officer. Review the alert context and the typology findings. "
                       "Determine the final risk rating (Low, Medium, High) and the recommended action (Close False Positive, Escalate for SAR). "
                       "Provide a clear justification."),
            ("user", "Alert Context: {context}\n\nTypology Findings: {typologies}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def decide(self, context, typologies):
        return self.chain.invoke({"context": context, "typologies": typologies})
