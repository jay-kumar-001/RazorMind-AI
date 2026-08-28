from agents.digital_twin_agent import digital_twin_agent

def simulation_agent(merchant_id: str, **kwargs):
    """
    Alias wrapper for Digital Twin Simulation Agent.
    """
    return digital_twin_agent(merchant_id=merchant_id, **kwargs)
