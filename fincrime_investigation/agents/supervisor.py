from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from .context_agent import ContextAgent
from .typology_agent import TypologyAgent
from .recommendation_agent import RecommendationAgent

class AgentState(TypedDict):
    alert_data: dict
    customer_profile: dict
    context_summary: str
    typology_findings: str
    final_recommendation: str

class Supervisor:
    def __init__(self):
        self.context_agent = ContextAgent()
        self.typology_agent = TypologyAgent()
        self.recommendation_agent = RecommendationAgent()
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("context_builder", self.run_context_agent)
        workflow.add_node("typology_checker", self.run_typology_agent)
        workflow.add_node("decision_maker", self.run_recommendation_agent)

        # Define edges
        workflow.set_entry_point("context_builder")
        workflow.add_edge("context_builder", "typology_checker")
        workflow.add_edge("typology_checker", "decision_maker")
        workflow.add_edge("decision_maker", END)

        return workflow.compile()

    def run_context_agent(self, state: AgentState):
        print("--- Running Context Agent ---")
        summary = self.context_agent.analyze(state["alert_data"], state["customer_profile"])
        return {"context_summary": summary}

    def run_typology_agent(self, state: AgentState):
        print("--- Running Typology Agent ---")
        findings = self.typology_agent.analyze(state["context_summary"])
        return {"typology_findings": findings}

    def run_recommendation_agent(self, state: AgentState):
        print("--- Running Recommendation Agent ---")
        recommendation = self.recommendation_agent.decide(state["context_summary"], state["typology_findings"])
        return {"final_recommendation": recommendation}

    def investigate(self, alert_data, customer_profile):
        initial_state = {"alert_data": alert_data, "customer_profile": customer_profile}
        result = self.workflow.invoke(initial_state)
        return result
