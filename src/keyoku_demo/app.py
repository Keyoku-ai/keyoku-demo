"""Gradio app for Keyoku Demo - matching landing page theme."""

import gradio as gr

from .chatbot import KeyokuChatbot
from .config import get_config


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


def get_chatbot():
    """Get or create the global chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        config = get_config()
        _chatbot_instance = KeyokuChatbot(config=config)
    return _chatbot_instance


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
    response = bot.chat(message, history)
    history = history + [(message, response)]
    return history, ""


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

    return stats_text, memory_rows, entity_rows, rel_rows


def clear_memories():
    """Clear all memories with confirmation."""
    bot = get_chatbot()
    result = bot.clear_all_memories()
    if result.get("success"):
        return "✅ All memories cleared"
    return f"❌ Error: {result.get('error', 'Unknown error')}"


def show_cleanup():
    """Show cleanup suggestions."""
    bot = get_chatbot()
    suggestions = bot.get_cleanup_suggestions()
    if "error" in suggestions:
        return f"❌ Error: {suggestions['error']}"

    lines = ["**Cleanup Strategies:**"]
    for s in suggestions.get("suggestions", []):
        lines.append(f"- **{s['strategy']}**: {s['description']}")
    return "\n".join(lines)


def export_data():
    """Export user data."""
    bot = get_chatbot()
    result = bot.export_data()
    return f"📤 {result.get('message', 'Export complete')}"


def create_app() -> gr.Blocks:
    """Create the Gradio app with Keyoku-themed UI."""
    config = get_config()
    errors = config.validate()

    with gr.Blocks(
        title="Keyoku Demo",
        css=CUSTOM_CSS,
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

        # Status bar
        status_output = gr.Markdown("")

        # Wire up events
        send_btn.click(
            chat,
            inputs=[msg_input, chatbot_ui],
            outputs=[chatbot_ui, msg_input],
        ).then(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display],
        )

        msg_input.submit(
            chat,
            inputs=[msg_input, chatbot_ui],
            outputs=[chatbot_ui, msg_input],
        ).then(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display],
        )

        refresh_btn.click(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display],
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
            clear_memories,
            outputs=[status_output],
        ).then(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display],
        )

        # Initialize on load
        app.load(
            update_panels,
            outputs=[stats_display, memories_display, entities_display, relationships_display],
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
