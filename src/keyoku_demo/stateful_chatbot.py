"""Stateful AI chatbot with automatic state extraction."""

import uuid
from typing import Optional, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from keyoku import Keyoku, KeyokuError

from .config import Config, get_config
from .demo_schemas import DEMO_AGENTS


class StatefulChatbot:
    """A chatbot with Keyoku Stateful AI capabilities.

    This chatbot demonstrates automatic state extraction from conversations.
    State changes are tracked without manual intervention - the LLM analyzes
    the conversation and extracts state according to the schema.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        session_id: Optional[str] = None,
        agent_id: str = "sales-agent",
        sharing_mode: str = "shared"
    ):
        self.config = config or get_config()
        self.session_id = session_id or f"stateful-{uuid.uuid4().hex[:8]}"
        self.agent_id = agent_id
        self.sharing_mode = sharing_mode
        self.schema_id: Optional[str] = None

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

        # Initialize schema for current agent
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure the state schema exists for the current agent."""
        agent_config = DEMO_AGENTS.get(self.agent_id)
        if not agent_config:
            print(f"Warning: No config for agent {self.agent_id}")
            return

        schema_name = agent_config["schema_name"]

        try:
            # Check if schema already exists
            response = self.keyoku.state_schemas.list(limit=100)
            for schema in response.schemas:
                if schema.name == schema_name:
                    self.schema_id = schema.id
                    return

            # Create schema if not found
            schema = self.keyoku.state_schemas.create(
                name=schema_name,
                schema_definition=agent_config["schema_definition"],
                description=f"State schema for {agent_config['name']}",
                sharing_mode=self.sharing_mode,
                transition_rules=agent_config.get("transition_rules"),
                transition_mode="warn",  # Don't fail on invalid transitions
            )
            self.schema_id = schema.id
            print(f"Created schema: {schema_name} (ID: {schema.id})")
        except KeyokuError as e:
            print(f"Error creating schema: {e}")

    def switch_agent(self, new_agent_id: str) -> None:
        """Switch to a different agent while preserving the session.

        This demonstrates how multiple agents can work on the same
        workflow/session, each with their own state that can optionally
        be shared or aggregated.
        """
        if new_agent_id not in DEMO_AGENTS:
            raise ValueError(f"Unknown agent: {new_agent_id}")

        self.agent_id = new_agent_id
        self._ensure_schema()

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the current agent."""
        agent_config = DEMO_AGENTS.get(self.agent_id, {})
        return agent_config.get("system_prompt", "You are a helpful assistant.")

    def _get_state_context(self) -> str:
        """Get current state as context for the LLM."""
        try:
            state = self.get_current_state()
            if state:
                return f"""
Current workflow state (automatically tracked):
- Status: {state.status}
- Version: {state.version}
- Data: {state.current_data}

The state is automatically updated based on our conversation."""
            return "No state tracked yet for this session."
        except Exception:
            return "State not available."

    def chat(
        self,
        message: str,
        history: list[tuple[str, str]]
    ) -> str:
        """Process user input and return LLM response (fast, non-blocking).

        Args:
            message: User's message
            history: Chat history as list of (user, assistant) tuples

        Returns:
            Assistant response text
        """
        if not self.schema_id:
            return "Error: No state schema configured for this agent."

        # Build messages for LLM
        system_prompt = self._get_system_prompt()
        state_context = self._get_state_context()

        messages = [
            SystemMessage(content=system_prompt),
            SystemMessage(content=state_context),
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
            return response.content
        except Exception as e:
            return f"Error generating response: {e}"

    def extract_state(self, user_message: str, assistant_response: str) -> Optional[dict]:
        """Extract state from a conversation turn (can be called async/background).

        Args:
            user_message: The user's message
            assistant_response: The assistant's response

        Returns:
            Extraction result dict or None on error
        """
        if not self.schema_id:
            return None

        try:
            conversation = f"User: {user_message}\nAssistant: {assistant_response}"
            result = self.keyoku.state.extract(
                content=conversation,
                schema_id=self.schema_id,
                session_id=self.session_id,
                agent_id=self.agent_id,
            )
            return {
                "is_new": result.is_new,
                "changed_fields": result.changed_fields,
                "confidence": result.confidence,
                "reasoning": result.reasoning,
                "suggested_action": result.suggested_action,
                "validation_error": result.validation_error,
                "state": {
                    "id": result.state.id,
                    "version": result.state.version,
                    "status": result.state.status,
                    "current_data": result.state.current_data,
                }
            }
        except KeyokuError as e:
            print(f"State extraction error: {e}")
            return {"error": str(e)}

    def chat_with_state_extraction(
        self,
        message: str,
        history: list[tuple[str, str]]
    ) -> tuple[str, Optional[dict]]:
        """Process user input and extract state (blocking - use chat() + extract_state() for async).

        Args:
            message: User's message
            history: Chat history as list of (user, assistant) tuples

        Returns:
            Tuple of (assistant_response, extraction_result_dict)
        """
        response_text = self.chat(message, history)
        if response_text.startswith("Error"):
            return response_text, None

        extraction_result = self.extract_state(message, response_text)
        return response_text, extraction_result

    def get_current_state(self) -> Optional[Any]:
        """Get the current state for this agent/session."""
        if not self.schema_id:
            return None

        try:
            response = self.keyoku.state.list(
                schema_id=self.schema_id,
                session_id=self.session_id,
                agent_id=self.agent_id,
                status="active",
                limit=1
            )
            if response.states:
                return response.states[0]
            return None
        except KeyokuError as e:
            print(f"Error getting state: {e}")
            return None

    def get_all_session_states(self) -> list[dict]:
        """Get all states for the current session (across all agents)."""
        try:
            response = self.keyoku.state.get_by_session(self.session_id)
            return [
                {
                    "agent_id": s.agent_id,
                    "schema_id": s.schema_id,
                    "version": s.version,
                    "status": s.status,
                    "current_data": s.current_data,
                    "confidence": s.confidence,
                }
                for s in response.states
            ]
        except KeyokuError as e:
            return [{"error": str(e)}]

    def get_state_history(self) -> list[dict]:
        """Get state transition history for the current agent's state."""
        try:
            state = self.get_current_state()
            if not state:
                return []

            response = self.keyoku.state.history(state.id)
            return [
                {
                    "from_version": t.from_version,
                    "to_version": t.to_version,
                    "changed_fields": t.changed_fields,
                    "trigger": t.trigger[:50] + "..." if t.trigger and len(t.trigger) > 50 else t.trigger,
                    "reasoning": t.reasoning,
                    "confidence": t.confidence,
                    "created_at": str(t.created_at)[:19],
                }
                for t in response.transitions
            ]
        except KeyokuError as e:
            return [{"error": str(e)}]

    def get_schema_info(self) -> Optional[dict]:
        """Get information about the current schema."""
        if not self.schema_id:
            return None

        try:
            schema = self.keyoku.state_schemas.get(self.schema_id)
            return {
                "id": schema.id,
                "name": schema.name,
                "description": schema.description,
                "sharing_mode": schema.sharing_mode.value if hasattr(schema.sharing_mode, 'value') else str(schema.sharing_mode),
                "transition_mode": schema.transition_mode.value if hasattr(schema.transition_mode, 'value') else str(schema.transition_mode),
                "version": schema.version,
                "schema_definition": schema.schema_definition,
                "transition_rules": schema.transition_rules,
            }
        except KeyokuError as e:
            return {"error": str(e)}

    def reset_session(self) -> str:
        """Start a new session (archives current states)."""
        try:
            # Archive current states
            response = self.keyoku.state.get_by_session(self.session_id)
            for state in response.states:
                self.keyoku.state.archive(state.id)

            # Generate new session ID
            self.session_id = f"stateful-{uuid.uuid4().hex[:8]}"
            return f"New session started: {self.session_id}"
        except KeyokuError as e:
            return f"Error resetting session: {e}"

    def get_agent_info(self) -> dict:
        """Get information about the current agent."""
        agent_config = DEMO_AGENTS.get(self.agent_id, {})
        return {
            "id": self.agent_id,
            "name": agent_config.get("name", self.agent_id),
            "description": agent_config.get("description", ""),
            "schema_name": agent_config.get("schema_name", ""),
        }

    @staticmethod
    def get_available_agents() -> list[dict]:
        """Get list of available demo agents."""
        return [
            {
                "id": agent_id,
                "name": config["name"],
                "description": config["description"],
            }
            for agent_id, config in DEMO_AGENTS.items()
        ]
