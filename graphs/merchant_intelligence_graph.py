import subprocess
import sys

python_exe = sys.executable

print("\n" + "=" * 60)
print("RAZORMIND AI")
print("MERCHANT INTELLIGENCE WORKFLOW")
print("=" * 60)

steps = [

    "models/revenue_forecasting_v2.py",

    "models/churn_prediction.py",

    "simulations/digital_twin_engine.py",

    "agents/recommendation_agent.py",

    "agents/final_report_agent.py"
]

for step in steps:

    print(f"\nRunning: {step}\n")

    subprocess.run(
        [
            python_exe,
            step
        ]
    )

print("\nWORKFLOW COMPLETE")