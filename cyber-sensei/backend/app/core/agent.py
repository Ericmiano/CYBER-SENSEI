import os
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

try:
    # Older LangChain versions expose this helper
    from langchain.agents import create_react_agent
    _HAS_CREATE_REACT = True
except Exception:
    create_react_agent = None
    _HAS_CREATE_REACT = False

try:
    from langchain import hub
except Exception:
    hub = None
from langchain_core.messages import SystemMessage

class _AgentWrapper:
    """Small compatibility wrapper that provides an `invoke` method used by
    the application code. It adapts several common LangChain agent interfaces
    (agent.run, agent.invoke, callable agents) to a consistent API.
    """
    def __init__(self, agent_obj):
        self._agent = agent_obj

    def invoke(self, ctx: dict):
        input_text = None
        if isinstance(ctx, dict):
            input_text = ctx.get('input') or ctx.get('input_text') or ctx.get('text')
        if input_text is None:
            input_text = str(ctx)

        # Try several common call patterns
        if hasattr(self._agent, 'invoke'):
            try:
                result = self._agent.invoke(input_text)
                return {'output': result}
            except TypeError:
                # some invoke signatures expect dicts
                result = self._agent.invoke({'input': input_text})
                return {'output': result}
        if hasattr(self._agent, 'run'):
            result = self._agent.run(input_text)
            return {'output': result}
        if callable(self._agent):
            result = self._agent(input_text)
            return {'output': result}

        # Last resort: try stringifying
        return {'output': str(self._agent)}

    # Import tool functions; these are defined in core/tools.py
    from .tools import (
        get_next_learning_step_for_user,
        query_personal_knowledge,
        add_document_to_knowledge_base,
        start_lab_environment,
    )

# --- Model Router ---
def get_model(task_complexity: str):
    """Routes a request to the appropriate model."""
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    if task_complexity == 'simple':
        try:
            # Use a local model for simple tasks
            return Ollama(base_url=ollama_base_url, model="llama3")
        except Exception:
            # Fallback if Ollama is not available
            print("Ollama not available, falling back to cloud model.")
            pass
    
    # Default to a powerful cloud model for complex tasks or fallback
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    return ChatOpenAI(model="gpt-4-turbo", temperature=0)

# --- Agent Setup ---
def setup_agent():
    """Initializes the LangChain agent with tools and a custom prompt."""
    llm = get_model('complex') # Default to complex for general chat
    
    tools = [
        get_next_learning_step_for_user,
        query_personal_knowledge,
        add_document_to_knowledge_base,
        start_lab_environment,
    ]
    
    # Add a custom system message to guide the agent's behavior
    system_message_content = """
    You are Cyber-Sensei, an advanced cybersecurity tutor and assistant.
    
    Your capabilities:
    1. **Personal Knowledge**: You have access to the user's personal notes and documents via 'query_personal_knowledge'. ALWAYS check this first if the user asks about "my notes", "uploaded files", or specific documents.
    2. **Curriculum Guidance**: You can suggest the next topic using 'get_next_learning_step_for_user'.
    3. **Lab Access**: You can start hands-on labs using 'start_lab_environment'.
    4. **Note Taking**: You can save important information for the user using 'add_document_to_knowledge_base'.

    Guidelines:
    - Be proactive. If a user asks a question that might be in their notes, use 'query_personal_knowledge'.
    - If the user seems stuck, suggest a lab or the next curriculum step.
    - Keep responses concise and encouraging.
    - If you use a tool, explain what you found or did.
    """

    # Try to pull the standard ReAct prompt if hub is available; otherwise
    # create a minimal prompt object we can pass to older/newer APIs.
    if hub is not None:
        try:
            prompt = hub.pull("hwchase17/react")
            # Safely get any existing template text if present
            try:
                existing_template = prompt.messages[0].content.template
            except Exception:
                existing_template = getattr(getattr(prompt.messages[0], 'content', ''), 'template', '') or str(getattr(prompt.messages[0], 'content', ''))
            prompt.messages[0] = SystemMessage(content=system_message_content + existing_template)
        except Exception:
            # If hub.pull fails, fall back to a simple prompt object below
            hub = None

    if hub is None:
        # Minimal fallback prompt object compatible with code expectations
        class _Prompt:
            def __init__(self, messages):
                self.messages = messages

        fallback_text = system_message_content + "\nYou are an instruction-following ReAct-style agent."
        prompt = _Prompt(messages=[SystemMessage(content=fallback_text)])

    if _HAS_CREATE_REACT:
        agent = create_react_agent(llm, tools, prompt)
        # Some LangChain versions provide AgentExecutor, others return a
        # ready-to-use executor. Try to adapt either form to our wrapper.
        try:
            from langchain.agents.executor import AgentExecutor
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            return _AgentWrapper(agent_executor)
        except Exception:
            return _AgentWrapper(agent)
    else:
        # Try to use the newer initialize_agent API available in recent
        # LangChain versions. We wrap the simple function-based tools with
        # Tool objects and call initialize_agent. If that fails, raise a
        # helpful error instructing the developer to pin or update.
        try:
            from langchain.agents import initialize_agent, AgentType
            try:
                # Newer LangChain exposes a Tool helper
                from langchain.tools import Tool
            except Exception:
                # Older import path fallback
                from langchain.agents import Tool

            lc_tools = []
            for fn in tools:
                # Wrap each function into a Tool with a basic description
                lc_tools.append(Tool(name=fn.__name__, func=fn, description=f"Tool: {fn.__name__}"))

            agent_executor = initialize_agent(llm=llm, tools=lc_tools, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
            return agent_executor
        except Exception as e:
            raise RuntimeError(
                "Unable to construct agent: missing LangChain helpers. "
                "Either pin langchain to a release that provides 'create_react_agent' or ensure the 'initialize_agent' and 'Tool' APIs are available. "
                "To pin, add a specific 'langchain==<version>' line to backend/requirements.txt and rebuild the container. "
                "Original error: " + str(e)
            ) from e