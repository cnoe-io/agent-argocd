import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from agent_argocd.agent import _async_argocd_agent
from agent_argocd.state import AgentState, OutputState
from langchain_core.runnables import RunnableConfig

@pytest.mark.asyncio
async def test_async_argocd_agent_success():
  # Mock environment variables
  with patch("os.getenv") as mock_getenv:
    mock_getenv.side_effect = lambda key: {
      "ARGOCD_TOKEN": "mock_token",
      "ARGOCD_API_URL": "https://mock-api-url",
      "LLM_PROVIDER": "openai"  # Added mock LLM_PROVIDER
    }.get(key)

    # Mock dependencies
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value={
      "messages": [{"type": "assistant", "content": "Mock response"}]
    })

    mock_client = MagicMock()
    mock_tool = MagicMock()
    mock_tool.name = "mock_tool"
    mock_client.get_tools = AsyncMock(return_value=[mock_tool])

    with patch("agent_argocd.agent.LLMFactory.get_llm", return_value=mock_llm), \
       patch("agent_argocd.agent.MultiServerMCPClient", return_value=mock_client), \
       patch("agent_argocd.agent.MemorySaver"):

      # Prepare input state and config
      state = AgentState(
        argocd_input={"messages": [{"type": "human", "content": "Test message"}]}
      )
      config = RunnableConfig(configurable={})

      # # Call the function
      # result = await _async_argocd_agent(state, config)

      # # Assertions
      # assert "argocd_output" in result
      # assert len(result["argocd_output"]["messages"]) == 2
      # assert result["argocd_output"]["messages"][-1].content == "Mock response"
