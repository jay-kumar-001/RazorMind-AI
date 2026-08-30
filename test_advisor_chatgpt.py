import os
import sys
import json
import uuid

# Ensure root directory is on PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.app import app
from backend.services.chat_history_service import chat_history_service
from backend.services.copilot_context_service import copilot_context_service

client = TestClient(app)

def test_advisor_chatgpt_suite():
    print("=" * 60)
    print("RAZORMIND ADVISOR AI — CHATGPT-CLASS SUITE VERIFICATION")
    print("=" * 60)

    # 1. Intent Classification
    print("\n--- 1. Intent Classifier Verification ---")
    intent_merchant = copilot_context_service.classify_intent("Why is churn high for this merchant?", mode="merchant", merchant_id="M0001")
    print("Query: 'Why is churn high for this merchant?' -> Intent:", intent_merchant)
    assert intent_merchant == "MERCHANT"

    intent_project = copilot_context_service.classify_intent("Explain the LangGraph 10-agent orchestration workflow in RazorMind", mode="general")
    print("Query: 'Explain the LangGraph...' -> Intent:", intent_project)
    assert intent_project == "PROJECT"

    intent_general = copilot_context_service.classify_intent("Explain the difference between FastAPI and Flask and how dependency injection works", mode="general")
    print("Query: 'Explain difference between FastAPI and Flask...' -> Intent:", intent_general)
    assert intent_general == "GENERAL"

    # 2. Context Service Assembly
    print("\n--- 2. Context Service Assembly Verification ---")
    ctx_m = copilot_context_service.build_merchant_context("M0001")
    print("Merchant Context Found:", ctx_m["merchant_found"], "| Risk Score:", ctx_m["risk_score"], "| Churn Prob:", ctx_m["churn_probability"])
    assert ctx_m["merchant_found"] is True
    assert "Live Merchant Profile" in ctx_m["formatted_text"]
    assert "Risk Assessment" in ctx_m["formatted_text"]
    assert "Churn Prediction" in ctx_m["formatted_text"]

    ctx_proj = copilot_context_service.build_project_context()
    print("Project Context Length:", len(ctx_proj["formatted_text"]))
    assert "RazorMind AI — Complete System Architecture" in ctx_proj["formatted_text"]

    ctx_gen = copilot_context_service.build_general_context()
    print("General Context:", ctx_gen["formatted_text"])
    assert "General AI Mode" in ctx_gen["formatted_text"]

    # 3. Conversation CRUD in SQLite
    print("\n--- 3. Conversation Lifecycle in SQLite ---")
    # Clear any previous test data
    client.delete("/copilot/conversations")

    # Create Conversation
    create_payload = {
        "title": "Merchant Analysis Thread",
        "mode": "merchant",
        "personality": "risk",
        "merchant_id": "M0001",
        "model_used": "qwen2.5:3b"
    }
    res = client.post("/copilot/conversations", json=create_payload)
    print("POST /copilot/conversations ->", res.status_code)
    assert res.status_code == 200
    conv_id = res.json()["id"]
    print("Created Conversation ID:", conv_id)

    # Rename Conversation
    res = client.put(f"/copilot/conversations/{conv_id}", json={"title": "Updated M0001 Deep Dive"})
    print("PUT /copilot/conversations/{id} ->", res.status_code)
    assert res.status_code == 200

    # List Conversations
    res = client.get("/copilot/conversations")
    print("GET /copilot/conversations ->", res.status_code, "Count:", len(res.json()))
    assert res.status_code == 200
    assert len(res.json()) >= 1
    assert res.json()[0]["title"] == "Updated M0001 Deep Dive"

    # 4. Multi-Turn Conversation Memory Simulation
    print("\n--- 4. Multi-Turn Conversation Memory ---")
    # Turn 1: Add user message "My name is Jay and I am analyzing M0001"
    msg1 = chat_history_service.add_message(
        msg_id=str(uuid.uuid4()),
        conv_id=conv_id,
        role="user",
        content="Hello, my name is Jay and I am analyzing M0001.",
        model_used="qwen3:8b"
    )
    # Assistant reply
    msg2 = chat_history_service.add_message(
        msg_id=str(uuid.uuid4()),
        conv_id=conv_id,
        role="assistant",
        content="Hello Jay! I am ready to help you analyze merchant M0001.",
        tokens=15,
        latency=0.3,
        agents_consulted=["Revenue Agent", "Risk Agent"],
        model_used="qwen3:8b",
        parent_id=msg1["id"]
    )
    # Turn 2: Add user message "What is my name?"
    msg3 = chat_history_service.add_message(
        msg_id=str(uuid.uuid4()),
        conv_id=conv_id,
        role="user",
        content="What is my name and which merchant are we discussing?",
        model_used="qwen3:8b"
    )

    # Fetch messages
    res = client.get(f"/copilot/conversations/{conv_id}/messages")
    print("GET /copilot/conversations/{id}/messages ->", res.status_code, "Total turns:", len(res.json()["messages"]))
    assert res.status_code == 200
    msgs = res.json()["messages"]
    assert len(msgs) == 3
    assert msgs[0]["content"] == "Hello, my name is Jay and I am analyzing M0001."
    assert msgs[2]["content"] == "What is my name and which merchant are we discussing?"

    # 5. Message Versioning & Switching
    print("\n--- 5. Message Versioning ---")
    # Add a second version (regeneration) for assistant reply to msg1
    msg2_v2 = chat_history_service.add_message(
        msg_id=str(uuid.uuid4()),
        conv_id=conv_id,
        role="assistant",
        content="Greetings Jay! Let's examine M0001's composite risk drivers.",
        tokens=18,
        latency=0.35,
        parent_id=msg1["id"],
        version=2,
        is_current=1
    )
    # Mark v1 as not current
    chat_history_service.mark_not_current(msg2["id"])

    # Get versions of msg1's assistant response
    res = client.get(f"/copilot/messages/{msg2_v2['id']}/versions?conversation_id={conv_id}")
    print("GET /copilot/messages/{id}/versions ->", res.status_code, "Versions found:", len(res.json()))
    assert res.status_code == 200
    assert len(res.json()) == 2

    # Switch back to version 1
    res = client.post("/copilot/messages/version", json={"conversation_id": conv_id, "message_id": msg2["id"]})
    print("POST /copilot/messages/version (switch to v1) ->", res.status_code)
    assert res.status_code == 200

    # 6. Message Deletion
    print("\n--- 6. Message Deletion ---")
    res = client.delete(f"/copilot/messages/{msg3['id']}?conversation_id={conv_id}")
    print("DELETE /copilot/messages/{id} ->", res.status_code)
    assert res.status_code == 200

    res = client.get(f"/copilot/conversations/{conv_id}/messages")
    remaining_msgs = res.json()["messages"]
    print("Remaining messages after deletion:", len(remaining_msgs))
    assert not any(m["id"] == msg3["id"] for m in remaining_msgs)

    # 7. Stop Generation Endpoint
    print("\n--- 7. Stop Generation Endpoint ---")
    res = client.post("/copilot/chat/stop", json={"conversation_id": conv_id, "question": ""})
    print("POST /copilot/chat/stop ->", res.status_code, res.json())
    assert res.status_code == 200
    assert res.json()["status"] == "stopped"

    # 8. Export Functionality
    print("\n--- 8. Export Thread Verification ---")
    res_md = client.get(f"/copilot/conversations/{conv_id}/export?format=md")
    print("GET export md ->", res_md.status_code, "Content length:", len(res_md.text))
    assert res_md.status_code == 200
    assert "Updated M0001 Deep Dive" in res_md.text

    # 9. Clear History
    print("\n--- 9. Clear All History ---")
    res = client.delete("/copilot/conversations")
    print("DELETE /copilot/conversations ->", res.status_code)
    assert res.status_code == 200

    res = client.get("/copilot/conversations")
    assert len(res.json()) == 0
    print("Verified conversation table is empty.")

    print("\n" + "=" * 60)
    print("ALL ADVISOR AI CHATGPT-CLASS FEATURES PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    test_advisor_chatgpt_suite()
