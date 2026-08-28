from graphs.langgraph_workflow import (
    graph
)

result = graph.invoke(
    {
        "merchant_id":
        "M0001"
    }
)

print(
    result["executive_report"]
)