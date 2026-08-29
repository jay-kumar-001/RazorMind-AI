# Advisor AI — Phase 1 Audit

**Scope:** `frontend/src/components/CopilotTab.jsx`, `frontend/src/api/api.js` (copilot clients), `frontend/src/App.css` (copilot styles), `backend/routes/copilot.py`, `backend/services/chat_history_service.py`, `backend/services/ollama_streaming_service.py`, `backend/services/rag_service.py`, `backend/services/file_parser_service.py`, `agents/copilot_agent.py`.

**Out of scope (untouched):** Overview, Risk & Attribution, Revenue Lab, Digital Twin, Action Roadmap, Executive Brief, Telemetry UI.

---

## What already works

| Area | Status |
|------|--------|
| Conversation sidebar (list, new, rename via `prompt`, delete, clear-all) | Working |
| SQLite persistence (`database/copilot_history.db`) | Working; survives refresh/restart |
| SSE token streaming from Ollama `/api/chat` | Working when Ollama is up |
| Stop generation (client `reader.cancel` + cancel flag) | Partial |
| Merchant vs General mode | Working at conversation create time |
| Personality prompts | Stored on conversation; applied at stream time |
| Ollama model list + preferred-model fallback | Partial (cached/fake list if not synced) |
| File attach (txt/pdf/csv/xlsx) + voice input + MD/PDF export | Working |
| Legacy `GET /copilot/{id}` + `copilot_agent` | Working (non-streaming) |
| RAG from Postgres merchant + latest analysis + forecasts | Partial (missing live churn, twin, traces, platform) |

---

## Broken or incomplete functionality

1. **Stop does not reliably persist partial replies.** Client abort can tear down the SSE generator before SQLite write. Streaming UI is cleared in `finally` even when the user stopped mid-token.
2. **Regenerate duplicates the user turn.** It re-POSTs the last user prompt as a new message. No version history.
3. **Delete message is local only.** Reloading the conversation restores deleted rows.
4. **Edit message is missing.**
5. **Shift+Enter cannot insert a newline.** Composer is a single-line `<input>`. Enter does send.
6. **Timestamps exist in SQLite but are not shown.**
7. **SQLite FK cascade is off.** `PRAGMA foreign_keys` is never enabled; deleting a conversation can leave orphan messages. No indexes on `conversation_id` / `updated_at`. No WAL.
8. **Search hits the API on every keystroke** with no debounce; LIKE `%query%` has no index.
9. **Personality/mode/merchant changes after create are ignored** by the stream endpoint (reads conversation row only).
10. **Stale `activeConvId` closure** in `loadConversations` can skip auto-select incorrectly.
11. **Token counter counts empty Ollama keep-alive chunks**, inflating observability metrics.
12. **Hardcoded `http://127.0.0.1:8000`** in stream `fetch` (rest of app uses the same axios base).

---

## Missing functionality (ChatGPT-class UX)

- Independent chat pane scroll vs page scroll; stick-to-bottom only when the user is near the bottom
- Scroll-to-bottom control; infinite/paginated history load
- Typing indicator distinct from a blocking spinner
- Copy / edit / delete / regenerate with versions
- Welcome empty state (ChatGPT-style) when the thread is empty
- Professional error codes (offline, timeout, empty, overflow) instead of a single timeout string
- Context window truncation for long threads
- Prompt-injection / malformed-request guards
- Live project copilot context (churn, digital twin, traces, dashboard tab, LangGraph workflow, model inventory)

---

## UX issues

- Layout height is a fixed **680px** grid — does not use remaining viewport; feels boxed-in vs ChatGPT.
- Auto `scrollIntoView` on every token **fights manual scroll**.
- `alert()` for copy/rename/sync is not production UX.
- Suggestions only appear after messages exist; empty state has no starter prompts in the main pane.
- Mobile: sidebar stays in a 280px column via `@media` collapse to one column but sidebar still consumes vertical space first.
- Streaming re-parses **full ReactMarkdown on every token** → flicker, incomplete fences, stutter.

---

## Performance issues

- Full message list loaded with no pagination (`SELECT * … ORDER BY timestamp`).
- Each stream token: `setStreamingContent` + markdown parse + smooth scroll.
- Search re-fetches full conversation list without debounce.
- New SQLite connection per query; no WAL, no busy timeout.
- RAG injects entire executive report + action plan into every turn (context overflow on small models).
- `loadMessages` after every send replaces optimistic UI (flash).

---

## Architecture weaknesses

1. **LangGraph is not used by Advisor.** Orchestration exists in `graphs/merchant_graph.py` (revenue → forecast → risk → churn → … → executive_report). Copilot only concatenates a system prompt + RAG text + chat history.
2. **Two copilot paths:** streaming SQLite chat vs blocking `copilot_agent` / `llm_service` (4s timeout, in-memory cache). They do not share context builders.
3. **Merchant intelligence is snapshot-at-create.** Switching the header merchant does not re-bind an existing thread unless a new conversation is created.
4. **No dashboard-state channel.** Advisor cannot see which tab is open, whether a chart failed, or live Digital Twin sliders.
5. **Security:** user content is concatenated into the system prompt via RAG only for merchant ledger (good), but user messages are not length-capped or screened; conversation IDs are unguessable UUIDs but unauthenticated.
6. **Follow-up (“Why?”)** depends on raw history being sent to Ollama — works if history is loaded, but overflowing truncation is missing so long threads degrade silently.

---

## Context / memory gaps vs product requirements

| Required awareness | Current |
|--------------------|---------|
| Previous messages | Yes (full table, unbounded) |
| Current merchant KPIs | Yes if conversation `merchant_id` set |
| Live risk calculation / drivers | Only stored `merchant_analysis` row |
| Forecast | Stored `revenue_forecasts` only |
| Churn prediction & drivers | **No** |
| Digital Twin simulations | **No** |
| Action plans / executive brief | Yes if analysis row exists |
| Telemetry / failed agents | **No** |
| Dashboard / active tab | **No** |
| Platform workflow / models / pages | **No** (generic personality prompt) |
| Debug (“why is this page blank?”) | **No** |

---

## Error handling gaps

| Failure | Behavior |
|---------|----------|
| Ollama down | Generic “timed out or offline” after fetch throw; SSE `error` tokens ignored by UI |
| Empty model output | Nothing persisted; UI reloads empty |
| Timeout (90s) | Same generic message |
| SQLite failure | Unhandled 500 |
| Context overflow | No handling; model may ramble or error |
| Backend restart mid-stream | Client error path; partial not saved |

---

## Scroll implementation

`.copilot-chat-area` is `overflow-y: auto` inside a 680px grid. A sentinel `messagesEndRef` always smooth-scrolls on `[messages, streamingContent, loading]`. There is no “user is reading history” detection, no paginated fetch, no jump-to-bottom button.

---

## Priority fix order (this implementation)

1. Persistence correctness (FK, WAL, versions, save-on-stop)
2. Streaming UX (abort, markdown stability, rAF batching, error events)
3. ChatGPT chrome (textarea, scroll rules, actions, sidebar)
4. Full merchant + platform + debug context
5. Security + model selection + tests
