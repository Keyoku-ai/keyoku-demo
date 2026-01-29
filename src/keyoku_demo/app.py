"""Gradio app for Keyoku Demo - matching landing page theme."""

import json
import uuid
from typing import Optional

import gradio as gr

from .chatbot import KeyokuChatbot
from .config import get_config
from .stateful_chatbot import StatefulChatbot
from .demo_schemas import DEMO_AGENTS, DEMO_SCENARIOS


def get_empty_state_cache() -> dict:
    """Create empty state cache for session-based caching via gr.State."""
    return {
        "current_state": None,
        "state_history": None,
        "all_states": None,
        "schema_info": None,
    }


# Custom CSS matching Keyoku landing page theme
CUSTOM_CSS = """
/* Global dark theme */
.gradio-container {
    background: #09090b !important;
    color: #fafafa !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}

.main, .contain {
    background: #09090b !important;
}

body {
    background: #09090b !important;
}

/* Chatbot styling */
.chatbot {
    background: rgba(24, 24, 27, 0.6) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    border-radius: 0.75rem !important;
}

.chatbot .message-wrap {
    background: transparent !important;
}

.chatbot .message {
    border-radius: 0.75rem !important;
}

.chatbot .user-message {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
}

.chatbot .bot-message {
    background: rgba(39, 39, 42, 0.8) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    color: #fafafa !important;
}

/* Input styling */
input, textarea, .input-container {
    background: rgba(24, 24, 27, 0.8) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    border-radius: 0.75rem !important;
    color: #fafafa !important;
}

input:focus, textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    outline: none !important;
}

/* Button styling */
button.primary, .btn-primary {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    color: white !important;
    border-radius: 0.5rem !important;
}

button.primary:hover, .btn-primary:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3) !important;
}

button.secondary, .btn-secondary {
    background: rgba(39, 39, 42, 0.8) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    color: #fafafa !important;
    border-radius: 0.5rem !important;
}

button.secondary:hover, .btn-secondary:hover {
    background: rgba(39, 39, 42, 1) !important;
    border-color: #6366f1 !important;
}

button.stop, .btn-stop {
    background: #ef4444 !important;
    border: none !important;
    color: white !important;
}

/* Panels and blocks */
.block, .panel {
    background: rgba(24, 24, 27, 0.6) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    border-radius: 0.75rem !important;
}

/* Accordion styling */
.accordion {
    background: rgba(24, 24, 27, 0.6) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    border-radius: 0.75rem !important;
}

.accordion .label-wrap {
    background: transparent !important;
    color: #fafafa !important;
}

/* JSON/Dataframe styling */
.json-holder, .dataframe, table {
    background: rgba(24, 24, 27, 0.8) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    border-radius: 0.5rem !important;
    color: #fafafa !important;
}

table th {
    background: rgba(39, 39, 42, 0.8) !important;
    color: #fafafa !important;
}

table td {
    color: #fafafa !important;
}

/* Labels */
label, .label-wrap, span.block-label {
    color: #a1a1aa !important;
}

/* Tabs */
.tabs {
    background: transparent !important;
}

.tab-nav {
    background: rgba(24, 24, 27, 0.6) !important;
    border: 1px solid rgba(63, 63, 70, 0.5) !important;
    border-radius: 0.75rem !important;
}

.tab-nav button {
    color: #a1a1aa !important;
    background: transparent !important;
}

.tab-nav button.selected {
    background: #6366f1 !important;
    color: white !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #fafafa !important;
}

/* Markdown text */
.markdown, .prose {
    color: #fafafa !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.3);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.5);
}

/* Row and column backgrounds */
.row, .column {
    background: transparent !important;
}
"""

# Global chatbot instance
_chatbot_instance = None
_stateful_chatbot_instance = None
_current_session_id = None


def get_chatbot():
    """Get or create the global chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        config = get_config()
        _chatbot_instance = KeyokuChatbot(config=config)
    return _chatbot_instance


def get_stateful_chatbot(agent_id: str = "sales-agent") -> StatefulChatbot:
    """Get or create the stateful chatbot instance."""
    global _stateful_chatbot_instance, _current_session_id
    config = get_config()

    if _current_session_id is None:
        _current_session_id = f"demo-{uuid.uuid4().hex[:8]}"

    if _stateful_chatbot_instance is None or _stateful_chatbot_instance.agent_id != agent_id:
        _stateful_chatbot_instance = StatefulChatbot(
            config=config,
            session_id=_current_session_id,
            agent_id=agent_id,
        )
    return _stateful_chatbot_instance


def format_importance(score: float) -> str:
    """Format importance score with color indicator."""
    bar_length = int(score * 10)
    bar = "█" * bar_length + "░" * (10 - bar_length)
    if score >= 0.7:
        return f"🟢 {bar} {score:.2f}"
    elif score >= 0.4:
        return f"🟡 {bar} {score:.2f}"
    else:
        return f"🔴 {bar} {score:.2f}"


def chat(message: str, history: list):
    """Process chat message and return response."""
    if not message.strip():
        return history, ""

    bot = get_chatbot()
    # Convert Gradio 6.x message format to tuples for the chatbot
    history_tuples = []
    i = 0
    while i < len(history):
        if i + 1 < len(history):
            user_msg = history[i].get("content", "") if isinstance(history[i], dict) else history[i][0]
            asst_msg = history[i + 1].get("content", "") if isinstance(history[i + 1], dict) else history[i + 1][1]
            history_tuples.append((user_msg, asst_msg))
            i += 2
        else:
            break

    response = bot.chat(message, history_tuples)
    # Return in Gradio 6.x message format
    new_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response}
    ]
    return new_history, ""


def update_panels():
    """Update all sidebar panels."""
    bot = get_chatbot()

    stats = bot.get_stats()
    # Format stats as text
    stats_text = f"Total Memories: {stats.get('total_memories', 'N/A')}\n"
    by_type = stats.get('by_type', {})
    if by_type:
        stats_text += "By Type:\n"
        for t, count in by_type.items():
            stats_text += f"  • {t}: {count}\n"
    elif 'error' in stats:
        stats_text = f"Error: {stats['error']}"

    memories = bot.get_memories()
    entities = bot.get_entities()
    relationships = bot.get_relationships()
    audit_logs = get_audit_logs()

    # Format memories for display
    memory_rows = []
    for mem in memories:
        if "error" not in mem:
            importance = mem.get("importance", 0.5)
            memory_rows.append([
                mem.get("content", ""),
                mem.get("type", ""),
                format_importance(importance),
            ])

    # Format entities
    entity_rows = [[e.get("name", ""), e.get("type", "")] for e in entities if "error" not in e]

    # Format relationships
    rel_rows = [[r.get("source", ""), r.get("type", ""), r.get("target", "")] for r in relationships if "error" not in r]

    return stats_text, memory_rows, entity_rows, rel_rows, audit_logs


def clear_memories_and_chat():
    """Clear all memories and chat history."""
    bot = get_chatbot()
    result = bot.clear_all_memories()
    if result.get("success"):
        return "✅ All memories cleared", []
    return f"❌ Error: {result.get('error', 'Unknown error')}", []


def new_chat_session():
    """Start a new chat session (clears chat but keeps memories).

    This tests if the memory system truly works by removing the LLM's
    conversation context while preserving stored memories.
    """
    return "🔄 New session started - memories preserved! Try asking 'What do you know about me?'", []


def show_cleanup():
    """Show cleanup suggestions with counts and usage info."""
    bot = get_chatbot()
    suggestions = bot.get_cleanup_suggestions()
    if "error" in suggestions:
        return f"❌ Error: {suggestions['error']}"

    lines = []

    # Show usage info
    usage = suggestions.get("usage", {})
    if usage:
        pct = usage.get("percentage", 0)
        stored = usage.get("memories_stored", 0)
        limit = usage.get("memories_limit", 0)
        lines.append(f"**Storage Usage:** {stored}/{limit} memories ({pct}%)")
        lines.append("")

    lines.append("**Cleanup Strategies:**")
    for s in suggestions.get("suggestions", []):
        count = s.get("count", 0)
        lines.append(f"- **{s['strategy']}**: {s['description']} ({count} memories)")

    return "\n".join(lines)


def export_data():
    """Export user data (GDPR export)."""
    bot = get_chatbot()
    result = bot.export_data()
    if "error" in result:
        return f"❌ Error: {result['error']}"
    job_id = result.get("job_id", "")
    status = result.get("status", "")
    return f"📤 **Export Started**\n\nJob ID: `{job_id}`\nStatus: {status}"


def get_audit_logs():
    """Get audit logs for display."""
    bot = get_chatbot()
    logs = bot.get_audit_logs(limit=10)
    rows = []
    for log in logs:
        if "error" not in log:
            rows.append([
                log.get("operation", ""),
                log.get("resource_type", ""),
                log.get("resource_id", "")[:8] + "..." if len(log.get("resource_id", "")) > 8 else log.get("resource_id", ""),
                log.get("created_at", ""),
            ])
    return rows


# =============================================================================
# Stateful AI Demo Handlers
# =============================================================================


def stateful_chat(message: str, history: list, agent_id: str):
    """Process chat message - returns LLM response immediately (non-blocking).

    State extraction happens separately in extract_state_background().
    """
    if not message.strip():
        return history, "", message  # Return message for state extraction

    bot = get_stateful_chatbot(agent_id)

    if not bot.schema_id:
        new_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "❌ Error: Could not create/find state schema. Check API connection."}
        ]
        return new_history, "", ""

    # Convert history format for the chatbot (tuples to list of tuples)
    history_tuples = []
    i = 0
    while i < len(history):
        if isinstance(history[i], dict):
            if history[i].get("role") == "user" and i + 1 < len(history):
                history_tuples.append((history[i]["content"], history[i + 1].get("content", "")))
                i += 2
            else:
                i += 1
        else:
            history_tuples.append(history[i])
            i += 1

    # Get LLM response quickly (non-blocking)
    response = bot.chat(message, history_tuples)
    new_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response}
    ]

    return new_history, "", message  # Return user message for state extraction


def extract_state_background(user_message: str, history: list, agent_id: str, cache: dict):
    """Extract state in background after chat response is shown.

    This is fire-and-forget - doesn't block the chat UI.
    """
    if cache is None:
        cache = get_empty_state_cache()

    if not user_message.strip():
        return cache

    bot = get_stateful_chatbot(agent_id)
    if not bot.schema_id:
        return cache

    # Get the assistant response from the last message in history
    assistant_response = ""
    if history and len(history) >= 2:
        last_msg = history[-1]
        if isinstance(last_msg, dict) and last_msg.get("role") == "assistant":
            assistant_response = last_msg.get("content", "")

    if not assistant_response:
        return cache

    # Extract state (this is the slow part, but now runs after chat is shown)
    try:
        state_result = bot.extract_state(user_message, assistant_response)
        if state_result and "state" in state_result:
            current_data = state_result.get("state", {}).get("current_data", {})
            cache["current_state"] = json.dumps(current_data, indent=2)
    except Exception as e:
        print(f"Background state extraction error: {e}")

    return cache


def switch_agent(agent_id: str, history: list):
    """Switch to a different agent while preserving session."""
    global _stateful_chatbot_instance
    _stateful_chatbot_instance = None  # Reset to create new instance

    agent_name = DEMO_AGENTS.get(agent_id, {}).get("name", agent_id)
    switch_msg = f"🔄 Switched to **{agent_name}**. The session and state are preserved."

    return history + [{"role": "assistant", "content": switch_msg}]


def new_stateful_session():
    """Start a new session for stateful chat."""
    global _current_session_id, _stateful_chatbot_instance
    _current_session_id = f"demo-{uuid.uuid4().hex[:8]}"
    _stateful_chatbot_instance = None

    return f"🆕 New session started: `{_current_session_id}`", []


def get_current_state_display(agent_id: str, cache: dict):
    """Get current state for display panel - shows ALL schema fields.

    Merges extracted state with schema to show all fields (null for unextracted).
    Uses session-based cache (gr.State) for scalability.
    """
    try:
        bot = get_stateful_chatbot(agent_id)
        agent_config = DEMO_AGENTS.get(agent_id, {})
        schema_def = agent_config.get("schema_definition", {})

        # Build complete state from schema (all fields with defaults)
        properties = schema_def.get("properties", {})
        complete_state = {}
        for field, field_def in properties.items():
            field_type = field_def.get("type", "string")
            if field_type == "array":
                complete_state[field] = []
            else:
                complete_state[field] = None

        # Get current extracted state and merge
        if bot.schema_id:
            state = bot.get_current_state()
            if state and state.current_data:
                # Merge extracted data over defaults
                for key, value in state.current_data.items():
                    complete_state[key] = value

        result = json.dumps(complete_state, indent=2)
        cache["current_state"] = result
        return result, cache
    except Exception as e:
        # Return cached value on error to avoid flickering
        if cache.get("current_state"):
            return cache["current_state"], cache
        return f"Error: {e}", cache


def get_state_history_display(agent_id: str, cache: dict):
    """Get state history for display.

    Uses session-based cache (gr.State) for scalability.
    """
    try:
        bot = get_stateful_chatbot(agent_id)

        if not bot.schema_id:
            result = "No schema initialized yet"
            cache["state_history"] = result
            return result, cache

        history = bot.get_state_history()  # Returns list[dict]

        if not history:
            result = "No state transitions yet"
            cache["state_history"] = result
            return result, cache

        lines = ["Version  | Changed | Trigger | Reasoning", "-" * 60]
        for t in history:
            if "error" in t:
                if cache.get("state_history"):
                    return cache["state_history"], cache
                return f"Error: {t['error']}", cache
            version = f"{t.get('from_version', '?')}→{t.get('to_version', '?')}"
            changed = ", ".join(t.get("changed_fields", [])) or "-"
            trigger = t.get("trigger", "-")[:30]
            reasoning = t.get("reasoning", "-")[:30]
            lines.append(f"{version:8} | {changed[:15]:15} | {trigger} | {reasoning}")

        result = "\n".join(lines)
        cache["state_history"] = result
        return result, cache
    except Exception as e:
        # Return cached value on error to avoid flickering
        if cache.get("state_history"):
            return cache["state_history"], cache
        return f"Error: {str(e)}", cache


def get_all_session_states_display(agent_id: str, cache: dict):
    """Get all states for the current session.

    Uses session-based cache (gr.State) for scalability.
    """
    try:
        bot = get_stateful_chatbot(agent_id)

        if not bot.schema_id:
            result = "Schema not initialized - start chatting to initialize"
            cache["all_states"] = result
            return result, cache

        states = bot.get_all_session_states()  # Returns list[dict]

        if states:
            # Check for errors
            if len(states) == 1 and "error" in states[0]:
                if cache.get("all_states"):
                    return cache["all_states"], cache
                return f"Error: {states[0]['error']}", cache

            result_dict = {}
            for state in states:
                agent = state.get("agent_id") or "default"
                result_dict[agent] = {
                    "version": state.get("version"),
                    "status": state.get("status"),
                    "data": state.get("current_data"),
                }
            result = json.dumps(result_dict, indent=2)
            cache["all_states"] = result
            return result, cache
        result = "No states in session yet"
        cache["all_states"] = result
        return result, cache
    except Exception as e:
        # Return cached value on error to avoid flickering
        if cache.get("all_states"):
            return cache["all_states"], cache
        return f"Error: {e}", cache


def get_schema_info_display(agent_id: str, cache: dict):
    """Get schema information - simplified view of fields and transitions.

    Uses session-based cache (gr.State) for scalability.
    """
    try:
        agent_config = DEMO_AGENTS.get(agent_id, {})
        schema_def = agent_config.get("schema_definition", {})
        transition_rules = agent_config.get("transition_rules", {})

        # Build simplified schema view
        fields = {}
        properties = schema_def.get("properties", {})
        for field, field_def in properties.items():
            field_info = {"type": field_def.get("type", "string")}
            if "enum" in field_def:
                field_info["values"] = field_def["enum"]
            if "description" in field_def:
                field_info["desc"] = field_def["description"][:40] + "..." if len(field_def.get("description", "")) > 40 else field_def.get("description", "")
            fields[field] = field_info

        result_dict = {
            "schema_name": agent_config.get("schema_name", "Unknown"),
            "fields": fields,
            "transitions": transition_rules,
        }

        result = json.dumps(result_dict, indent=2)
        cache["schema_info"] = result
        return result, cache
    except Exception as e:
        # Return cached value on error to avoid flickering
        if cache.get("schema_info"):
            return cache["schema_info"], cache
        return f"Error: {e}", cache


def update_state_panels(agent_id: str, cache: dict):
    """Update all state-related panels with session-based caching."""
    if cache is None:
        cache = get_empty_state_cache()
    current_state, cache = get_current_state_display(agent_id, cache)
    state_history, cache = get_state_history_display(agent_id, cache)
    all_states, cache = get_all_session_states_display(agent_id, cache)
    schema_info, cache = get_schema_info_display(agent_id, cache)
    return current_state, state_history, all_states, schema_info, cache


def force_refresh_state_panels(agent_id: str, cache: dict):
    """Force refresh all state panels by clearing cache first."""
    # Clear cache to force fresh data
    cache = get_empty_state_cache()
    return update_state_panels(agent_id, cache)


def load_scenario(scenario_name: str, agent_id: str):
    """Load a demo scenario with pre-filled messages."""
    scenario = DEMO_SCENARIOS.get(scenario_name)
    if not scenario:
        return "Unknown scenario", []

    name = scenario.get("name", scenario_name)
    description = scenario.get("description", "")
    sample_messages = scenario.get("sample_messages", [])
    sample_flow = scenario.get("sample_flow", [])

    info = f"**{name}**: {description}\n\n"

    if scenario_name == "none":
        info += """**Quick Start:**
1. Type any message to start extracting state
2. Watch the **Current State** panel update automatically
3. Try switching agents to see state sharing
4. State history shows all transitions

**Example messages:**
- "I'd like to order a laptop"
- "My order arrived damaged"
- "Schedule a meeting for tomorrow"
"""
    elif sample_messages:
        info += "**Try these messages:**\n"
        for i, msg in enumerate(sample_messages, 1):
            info += f"{i}. \"{msg}\"\n"
    elif sample_flow:
        info += "**Multi-agent flow:**\n"
        for i, step in enumerate(sample_flow, 1):
            agent = step.get("agent", "?")
            msg = step.get("message", "")
            info += f"{i}. [{agent}] \"{msg}\"\n"

    return info, []


def create_app() -> gr.Blocks:
    """Create the Gradio app with Keyoku-themed UI."""
    config = get_config()
    errors = config.validate()

    with gr.Blocks(
        title="Keyoku Demo",
    ) as app:
        # Header
        gr.Markdown(
            """
            # <span style="background: linear-gradient(to right, #6366f1, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Keyoku</span> Demo
            **AI Memory SDK** — Chat with persistent memory, knowledge graphs, and intelligent decay
            """
        )

        if errors:
            gr.Markdown(
                f"⚠️ **Configuration errors:** {', '.join(errors)}\n\n"
                "Please set the required environment variables in `.env`"
            )

        # Main tabbed interface
        with gr.Tabs():
            # =================================================================
            # Tab 1: Memory Demo (existing functionality)
            # =================================================================
            with gr.Tab("🧠 Memory Demo"):
                with gr.Row():
                    # Left column - Chat
                    with gr.Column(scale=2):
                        chatbot_ui = gr.Chatbot(
                            label="💬 Chat",
                            height=500,
                            show_label=True,
                            elem_classes=["chatbot"],
                        )

                        with gr.Row():
                            msg_input = gr.Textbox(
                                placeholder="Type your message...",
                                show_label=False,
                                container=False,
                                scale=4,
                            )
                            send_btn = gr.Button("Send", variant="primary", scale=1)

                        # Demo controls
                        gr.Markdown("### 🔧 Demo Controls")
                        with gr.Row():
                            new_chat_btn = gr.Button("💬 New Chat", variant="primary", size="sm")
                            refresh_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")
                            cleanup_btn = gr.Button("🧹 Cleanup", variant="secondary", size="sm")
                            export_btn = gr.Button("📤 Export", variant="secondary", size="sm")
                            clear_btn = gr.Button("🗑️ Clear All", variant="stop", size="sm")

                    # Right column - Panels
                    with gr.Column(scale=1):
                        # Stats panel
                        with gr.Accordion("📊 Memory Stats", open=True):
                            stats_display = gr.Textbox(label=None, lines=5, elem_classes=["panel"])

                        # Memories panel
                        with gr.Accordion("🧠 Memories", open=True):
                            memories_display = gr.Dataframe(
                                headers=["Content", "Type", "Importance"],
                                label=None,
                                elem_classes=["panel"],
                                wrap=True,
                            )

                        # Knowledge Graph panel
                        with gr.Accordion("🔗 Knowledge Graph", open=False):
                            with gr.Tab("Entities"):
                                entities_display = gr.Dataframe(
                                    headers=["Name", "Type"],
                                    label=None,
                                    elem_classes=["panel"],
                                )
                            with gr.Tab("Relationships"):
                                relationships_display = gr.Dataframe(
                                    headers=["Source", "Relationship", "Target"],
                                    label=None,
                                    elem_classes=["panel"],
                                )

                        # Audit Logs panel
                        with gr.Accordion("📋 Audit Logs", open=False):
                            audit_display = gr.Dataframe(
                                headers=["Operation", "Resource", "ID", "Time"],
                                label=None,
                                elem_classes=["panel"],
                            )

                # Status bar for memory tab
                status_output = gr.Markdown("")

            # =================================================================
            # Tab 2: Stateful AI Demo (new functionality)
            # =================================================================
            with gr.Tab("⚡ Stateful AI Demo"):
                gr.Markdown(
                    """
                    ### Automatic State Extraction for AI Agents
                    Chat with different agents and watch state get automatically extracted and shared.
                    Switch agents to see how state persists across the workflow.
                    """
                )

                with gr.Row():
                    # Left column - Chat with agent controls
                    with gr.Column(scale=2):
                        # Agent selector
                        with gr.Row():
                            agent_selector = gr.Dropdown(
                                choices=[(v["name"], k) for k, v in DEMO_AGENTS.items()],
                                value="sales-agent",
                                label="🤖 Active Agent",
                                scale=2,
                            )
                            scenario_selector = gr.Dropdown(
                                choices=[(DEMO_SCENARIOS[k].get("name", k), k) for k in DEMO_SCENARIOS.keys()],
                                value="none",
                                label="📋 Load Scenario",
                                scale=2,
                            )

                        # Stateful chatbot
                        stateful_chatbot_ui = gr.Chatbot(
                            label="💬 Stateful Chat",
                            height=400,
                            show_label=True,
                            elem_classes=["chatbot"],
                        )

                        with gr.Row():
                            stateful_msg_input = gr.Textbox(
                                placeholder="Type your message to extract state...",
                                show_label=False,
                                container=False,
                                scale=4,
                            )
                            stateful_send_btn = gr.Button("Send", variant="primary", scale=1)

                        # Controls
                        gr.Markdown("### 🔧 Session Controls")
                        with gr.Row():
                            new_session_btn = gr.Button("🆕 New Session", variant="primary", size="sm")
                            refresh_state_btn = gr.Button("🔄 Refresh State", variant="secondary", size="sm")

                        # Scenario info
                        scenario_info = gr.Markdown("")

                    # Right column - State panels
                    with gr.Column(scale=1):
                        # Current State panel
                        with gr.Accordion("📊 Current State", open=True):
                            current_state_display = gr.Textbox(
                                label=None,
                                lines=10,
                                max_lines=15,
                            )

                        # State History panel
                        with gr.Accordion("📜 State History", open=True):
                            state_history_display = gr.Textbox(
                                label=None,
                                lines=8,
                                max_lines=12,
                            )

                        # All Agent States panel
                        with gr.Accordion("👥 All Agent States", open=False):
                            all_states_display = gr.Textbox(
                                label=None,
                                lines=8,
                                max_lines=12,
                            )

                        # Schema Info panel
                        with gr.Accordion("📋 Schema Info", open=True):
                            schema_info_display = gr.Textbox(
                                label=None,
                                lines=10,
                                max_lines=15,
                            )

                # Status bar for stateful tab
                stateful_status_output = gr.Markdown("")

                # Session-based cache for state displays (scalable - not global)
                state_display_cache = gr.State(get_empty_state_cache)

                # Hidden state to pass user message for background extraction
                last_user_message = gr.State("")

                # Auto-refresh disabled - use manual refresh button instead to avoid flickering
                # state_refresh_timer = gr.Timer(value=3, active=True)

        # =================================================================
        # Event Wiring - Memory Demo Tab
        # =================================================================
        send_btn.click(
            chat,
            inputs=[msg_input, chatbot_ui],
            outputs=[chatbot_ui, msg_input],
        ).then(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display, audit_display],
        )

        msg_input.submit(
            chat,
            inputs=[msg_input, chatbot_ui],
            outputs=[chatbot_ui, msg_input],
        ).then(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display, audit_display],
        )

        new_chat_btn.click(
            new_chat_session,
            outputs=[status_output, chatbot_ui],
        )

        refresh_btn.click(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display, audit_display],
        )

        cleanup_btn.click(
            show_cleanup,
            outputs=[status_output],
        )

        export_btn.click(
            export_data,
            outputs=[status_output],
        )

        clear_btn.click(
            clear_memories_and_chat,
            outputs=[status_output, chatbot_ui],
        ).then(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display, audit_display],
        )

        # =================================================================
        # Event Wiring - Stateful AI Demo Tab
        # =================================================================

        # Send message - chat returns immediately, state extraction runs in background
        stateful_send_btn.click(
            stateful_chat,
            inputs=[stateful_msg_input, stateful_chatbot_ui, agent_selector],
            outputs=[stateful_chatbot_ui, stateful_msg_input, last_user_message],
        ).then(
            extract_state_background,
            inputs=[last_user_message, stateful_chatbot_ui, agent_selector, state_display_cache],
            outputs=[state_display_cache],
        ).then(
            update_state_panels,
            inputs=[agent_selector, state_display_cache],
            outputs=[current_state_display, state_history_display, all_states_display, schema_info_display, state_display_cache],
        )

        stateful_msg_input.submit(
            stateful_chat,
            inputs=[stateful_msg_input, stateful_chatbot_ui, agent_selector],
            outputs=[stateful_chatbot_ui, stateful_msg_input, last_user_message],
        ).then(
            extract_state_background,
            inputs=[last_user_message, stateful_chatbot_ui, agent_selector, state_display_cache],
            outputs=[state_display_cache],
        ).then(
            update_state_panels,
            inputs=[agent_selector, state_display_cache],
            outputs=[current_state_display, state_history_display, all_states_display, schema_info_display, state_display_cache],
        )

        # Switch agent
        agent_selector.change(
            switch_agent,
            inputs=[agent_selector, stateful_chatbot_ui],
            outputs=[stateful_chatbot_ui],
        ).then(
            update_state_panels,
            inputs=[agent_selector, state_display_cache],
            outputs=[current_state_display, state_history_display, all_states_display, schema_info_display, state_display_cache],
        )

        # New session (force refresh to clear old state)
        new_session_btn.click(
            new_stateful_session,
            outputs=[stateful_status_output, stateful_chatbot_ui],
        ).then(
            force_refresh_state_panels,
            inputs=[agent_selector, state_display_cache],
            outputs=[current_state_display, state_history_display, all_states_display, schema_info_display, state_display_cache],
        )

        # Refresh state panels (force refresh clears cache)
        refresh_state_btn.click(
            force_refresh_state_panels,
            inputs=[agent_selector, state_display_cache],
            outputs=[current_state_display, state_history_display, all_states_display, schema_info_display, state_display_cache],
        )

        # Load scenario
        scenario_selector.change(
            load_scenario,
            inputs=[scenario_selector, agent_selector],
            outputs=[scenario_info, stateful_chatbot_ui],
        )

        # Auto-refresh disabled - using manual refresh button instead
        # state_refresh_timer.tick(
        #     update_state_panels,
        #     inputs=[agent_selector, state_display_cache],
        #     outputs=[current_state_display, state_history_display, all_states_display, schema_info_display, state_display_cache],
        # )

        # =================================================================
        # Initialize on load
        # =================================================================
        app.load(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display, audit_display],
        ).then(
            update_state_panels,
            inputs=[agent_selector, state_display_cache],
            outputs=[current_state_display, state_history_display, all_states_display, schema_info_display, state_display_cache],
        )

    return app


def main():
    """Main entry point."""
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
