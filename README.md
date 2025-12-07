# Keyoku Demo

Interactive demo showcasing the Keyoku AI Memory SDK with a chat interface.

## Features

- **Persistent Memory**: Chat messages are automatically stored and recalled
- **Semantic Search**: Relevant memories are retrieved based on conversation context
- **Knowledge Graph**: Entities and relationships are extracted automatically
- **Memory Decay**: Watch importance scores change over time
- **Multi-Agent Support**: Switch between different agent contexts

## Quick Start

### Prerequisites

- Python 3.9+
- Keyoku API running locally (or production API key)
- OpenAI API key

### Setup

1. **Install dependencies**

   ```bash
   cd keyoku-demo
   pip install -e . -e ../keyoku-python
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   Required variables:
   - `KEYOKU_API_KEY` - Your Keyoku API key
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `KEYOKU_BASE_URL` - API URL (default: `http://localhost:8000`)

3. **Run the demo**

   ```bash
   keyoku-demo
   # Or: python -m keyoku_demo.app
   ```

4. **Open in browser**

   Navigate to `http://localhost:7860`

## UI Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Keyoku Demo                                                        │
├───────────────────────────────────┬─────────────────────────────────┤
│                                   │  📊 Memory Stats                │
│   💬 Chat                         │  Total: 23 | Facts: 12          │
│   ─────────────────               │                                 │
│   You: I'm Sarah from TechCorp   │  🧠 Memories                    │
│                                   │  • "Sarah at TechCorp" 0.85     │
│   Bot: Nice to meet you Sarah!   │  • "Prefers dark mode" 0.42     │
│   I'll remember that.            │                                 │
│                                   │  🔗 Knowledge Graph             │
│   [Message input...]    [Send]   │  Entities | Relationships       │
│                                   │                                 │
├───────────────────────────────────┤  🤖 Agent ID                   │
│  🔧 Demo Controls                 │  [demo-assistant]              │
│  [Refresh] [Cleanup] [Export]    │                                 │
│  [Clear All]                      │                                 │
└───────────────────────────────────┴─────────────────────────────────┘
```

## Testing SDK Capabilities

| Capability | How to Test |
|------------|-------------|
| **Remember** | Chat normally → memories auto-store |
| **Search** | Ask "what do you know about me?" |
| **Importance** | Watch scores in Memories panel |
| **Entities** | Mention names/companies → see in Knowledge Graph |
| **Relationships** | "Bob is my manager" → see relationship |
| **Multi-Agent** | Change Agent ID → memories are isolated |
| **Stats** | Always visible in sidebar |
| **Cleanup** | Click Cleanup → see suggestions |
| **Delete All** | Click Clear All → wipes memories |

## Project Structure

```
keyoku-demo/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
└── src/keyoku_demo/
    ├── __init__.py
    ├── app.py          # Gradio UI
    ├── chatbot.py      # Keyoku + LangChain logic
    ├── config.py       # Environment config
    └── prompts.py      # System prompts
```

## Development

Run with hot reload:

```bash
gradio src/keyoku_demo/app.py
```

## License

MIT
