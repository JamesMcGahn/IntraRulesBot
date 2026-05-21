from dataclasses import dataclass


@dataclass
class AgentState:
    state: str
    aux: str = ""
