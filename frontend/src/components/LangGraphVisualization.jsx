const LangGraphVisualization = () => {

  const nodes = [
    "Revenue Agent",
    "Forecast Agent",
    "Risk Agent",
    "Recommendation Agent",
    "Decision Agent",
    "Executive Report Agent"
  ];

  return (
    <div className="graph-card">
      <h2>LangGraph Workflow</h2>

      <div className="graph-flow">
        {nodes.map((node, index) => (
          <div key={index}>
            <div className="graph-node">
              ✅ {node}
            </div>

            {index !== nodes.length - 1 && (
              <div className="graph-arrow">
                ↓
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LangGraphVisualization;