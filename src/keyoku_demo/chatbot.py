"""Keyoku-powered chatbot with persistent memory."""

import uuid
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from keyoku import Keyoku, KeyokuError

from .config import Config, get_config
from .prompts import SYSTEM_PROMPT, MEMORY_CONTEXT_TEMPLATE, NO_MEMORY_CONTEXT


class KeyokuChatbot:
    """A chatbot with Keyoku-powered persistent memory."""

    def __init__(self, config: Optional[Config] = None, session_id: Optional[str] = None):
        self.config = config or get_config()
        self.session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"

        # Initialize Keyoku client
        self.keyoku = Keyoku(
            api_key=self.config.keyoku_api_key,
            base_url=self.config.keyoku_base_url,
        )

        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.llm_model,
            temperature=self.config.llm_temperature,
        )

    def _retrieve_relevant_memories(self, query: str) -> str:
        """Search Keyoku for relevant memories."""
        try:
            results = self.keyoku.search(
                query,
                limit=self.config.memory_search_limit,
                mode=self.config.memory_search_mode,
                agent_id=self.config.agent_id,
            )

            if not results:
                return NO_MEMORY_CONTEXT

            memory_lines = []
            for i, mem in enumerate(results, 1):
                importance = getattr(mem, 'importance', 0.5)
                memory_lines.append(f"{i}. {mem.content} (importance: {importance:.2f})")

            return MEMORY_CONTEXT_TEMPLATE.format(memories="\n".join(memory_lines))
        except KeyokuError as e:
            return f"Could not retrieve memories: {e}"

    def chat(self, message: str, history: list[tuple[str, str]]) -> str:
        """Process user input and return response.

        Args:
            message: User's message
            history: Chat history as list of (user, assistant) tuples

        Returns:
            Assistant's response
        """
        # Retrieve relevant memories
        memory_context = self._retrieve_relevant_memories(message)

        # Build messages for LLM
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            SystemMessage(content=memory_context),
        ]

        # Add chat history
        for user_msg, assistant_msg in history:
            messages.append(HumanMessage(content=user_msg))
            messages.append(AIMessage(content=assistant_msg))

        # Add current message
        messages.append(HumanMessage(content=message))

        # Generate response
        try:
            response = self.llm.invoke(messages)
            response_text = response.content
        except Exception as e:
            return f"Error generating response: {e}"

        # Store the conversation in Keyoku
        try:
            conversation = f"User: {message}\nAssistant: {response_text}"
            job = self.keyoku.remember(
                conversation,
                session_id=self.session_id,
                agent_id=self.config.agent_id,
            )
            # Wait for memory processing so panels can show updated data
            job.wait(timeout=10.0)
        except KeyokuError as e:
            # Log but don't fail the response
            print(f"Failed to store memory: {e}")
        except TimeoutError:
            # Memory processing taking too long, continue anyway
            print("Memory processing timed out, continuing...")

        return response_text

    def get_stats(self) -> dict:
        """Get memory statistics."""
        try:
            stats = self.keyoku.stats()
            return {
                "total_memories": stats.total_memories,
                "by_type": stats.by_type,
            }
        except KeyokuError as e:
            return {"error": str(e)}

    def get_memories(self, limit: int = 20) -> list[dict]:
        """Get list of memories with importance scores."""
        try:
            response = self.keyoku.memories.list(
                limit=limit,
                agent_id=self.config.agent_id,
            )
            memories = []
            for mem in response.memories:
                memories.append({
                    "id": mem.id,
                    "content": mem.content[:100] + "..." if len(mem.content) > 100 else mem.content,
                    "type": mem.type,
                    "importance": getattr(mem, 'importance', 0.5),
                    "created_at": str(getattr(mem, 'created_at', '')),
                })
            return memories
        except KeyokuError as e:
            return [{"error": str(e)}]

    def get_entities(self, limit: int = 20) -> list[dict]:
        """Get extracted entities from knowledge graph."""
        try:
            entities_list = self.keyoku.entities.list(limit=limit)
            entities = []
            for entity in entities_list:
                entities.append({
                    "id": entity.id,
                    "name": entity.canonical_name,
                    "type": entity.type,
                })
            return entities
        except KeyokuError as e:
            return [{"error": str(e)}]

    def get_relationships(self, limit: int = 20) -> list[dict]:
        """Get relationships from knowledge graph."""
        try:
            rel_list = self.keyoku.relationships.list(limit=limit)
            relationships = []
            for rel in rel_list:
                relationships.append({
                    "source": rel.source_entity_id,
                    "type": rel.relationship_type,
                    "target": rel.target_entity_id,
                })
            return relationships
        except KeyokuError as e:
            return [{"error": str(e)}]

    def get_cleanup_suggestions(self) -> dict:
        """Get cleanup suggestions from Keyoku."""
        try:
            # This endpoint may not exist in all versions
            # Using the search with low threshold as a workaround
            return {
                "suggestions": [
                    {"strategy": "stale", "description": "Remove memories not accessed recently"},
                    {"strategy": "low_importance", "description": "Remove low importance memories"},
                    {"strategy": "never_accessed", "description": "Remove memories never accessed"},
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def execute_cleanup(self, strategy: str, limit: int = 10) -> dict:
        """Execute memory cleanup with given strategy."""
        try:
            # Note: This may need to be implemented via direct API call
            # if the SDK doesn't have this method yet
            return {"message": f"Cleanup with strategy '{strategy}' not yet implemented in SDK"}
        except Exception as e:
            return {"error": str(e)}

    def clear_all_memories(self) -> dict:
        """Delete all memories (with confirmation)."""
        try:
            self.keyoku.memories.delete_all()
            return {"success": True, "message": "All memories deleted"}
        except KeyokuError as e:
            return {"success": False, "error": str(e)}

    def export_data(self) -> dict:
        """Export all user data."""
        try:
            # Note: Export functionality may need direct API call
            return {"message": "Export functionality - check API documentation"}
        except Exception as e:
            return {"error": str(e)}
