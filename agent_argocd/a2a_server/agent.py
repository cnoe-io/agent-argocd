import logging

from collections.abc import AsyncIterable
from typing import Any, Literal, Dict

import importlib.util
import logging
import os
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.runnables.config import (
    RunnableConfig,
)
from langchain_core.tools import tool  # type: ignore
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent  # type: ignore

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
import pprint
from agent_argocd.a2a_server.state import (
    AgentState,
    InputState,
    Message,
    MsgType,
)

logger = logging.getLogger(__name__)

memory = MemorySaver()


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class ArgoCDAgent:
    """ArgoCD Agent"""

    SYSTEM_INSTRUCTION = (
      "You are an assistant that helps manage applications in ArgoCD. "
      "You can list applications with filtering options such as project name, application name, repository URL, and namespace. "
      "You can fetch detailed information about specific applications. "
      "You can create new applications in ArgoCD with specified configurations. "
      "You can update existing applications with new configurations. "
      "You can delete applications from ArgoCD, with options for cascading deletion. "
      "You can sync applications to a specific Git revision, with options for pruning and dry runs. "
      "You can provide information about the current user, server settings, available plugins, and version details of the ArgoCD API server."
    )

    RESPONSE_FORMAT_INSTRUCTION: str = (
        'Select status as completed if the request is complete'
        'Select status as input_required if the input is a question to the user'
        'Set response status to error if the input indicates an error'
    )

    def __init__(self):

      memory = MemorySaver()

      argocd_token = os.getenv("ARGOCD_TOKEN")
      if not argocd_token:
        raise ValueError("ARGOCD_TOKEN must be set as an environment variable.")

      argocd_api_url = os.getenv("ARGOCD_API_URL")
      if not argocd_api_url:
        raise ValueError("ARGOCD_API_URL must be set as an environment variable.")
      # Setup the math agent and load MCP tools
      self.model = AzureChatOpenAI(
          model="gpt-4o")
      self.graph = None

      async def _async_argocd_agent(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
          # Find installed path of the argocd_mcp sub-module
          spec = importlib.util.find_spec("agent_argocd.argocd_mcp.server")
          if not spec or not spec.origin:
              raise ImportError("Cannot find agent_argocd.argocd_mcp.server module")

          server_path = str(Path(spec.origin).resolve())
          logger.info(f"Launching ArgoCD LangGraph Agent with MCP server adapter at: {server_path}")

          # args = config.get("configurable", {})
          # server_path = args.get("server_path", "./math_server.py")

          print(f"Launching MCP server at: {server_path}")

          client = MultiServerMCPClient(
              {
                  "math": {
                      "command": "uv",
                      "args": ["run", server_path],
                      "env": {
                        "ARGOCD_TOKEN": argocd_token,
                        "ARGOCD_API_URL": argocd_api_url,
                        "ARGOCD_VERIFY_SSL": "false"
                      },
                      "transport": "stdio",
                  }
              }
          )
          tools = client.get_tools()

          print(f"Loaded tools: {tools}")

          self.graph = create_react_agent(
            self.model,
            tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.RESPONSE_FORMAT_INSTRUCTION, ResponseFormat),
          )

          # Provide a 'configurable' key such as 'thread_id' for the checkpointer
          runnable_config = RunnableConfig(configurable={"thread_id": "test-thread"})
          llm_result = await self.graph.ainvoke({"messages": HumanMessage(content="What is the argocd version")}, config=runnable_config)
          print(f"LLM result: {llm_result}")

          # Try to extract meaningful content from the LLM result
          ai_content = None

          # Look through messages for final assistant content
          for msg in reversed(llm_result.get("messages", [])):
              if hasattr(msg, "type") and msg.type in ("ai", "assistant") and getattr(msg, "content", None):
                  ai_content = msg.content
                  break
              elif isinstance(msg, dict) and msg.get("type") in ("ai", "assistant") and msg.get("content"):
                  ai_content = msg["content"]
                  break

          # Fallback: if no content was found but tool_call_results exists
          if not ai_content and "tool_call_results" in llm_result:
              ai_content = "\n".join(
                  str(r.get("content", r)) for r in llm_result["tool_call_results"]
              )


          # Return response
          if ai_content:
              print("Assistant generated response")
              output_messages = [Message(type=MsgType.assistant, content=ai_content)]
          else:
              logger.warning("No assistant content found in LLM result")
              output_messages = []

          # Add a banner before printing the output messages
          print("=" * 40)
          print(f"MATH AGENT FINAL OUTPUT: {output_messages[-1].content}")
          print("=" * 40)

      def _create_agent(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
          return asyncio.run(_async_argocd_agent(state, config))
      messages = []
      state_input = InputState(messages=messages)
      agent_input = AgentState(argocd_input=state_input).model_dump(mode="json")
      runnable_config = RunnableConfig()
      # Add a HumanMessage to the input messages if not already present
      if not any(isinstance(m, HumanMessage) for m in messages):
          messages.append(HumanMessage(content="What is 2 + 2?"))
      _create_agent(agent_input, config=runnable_config)

      # logger.info("Loading MCP tools via extract_mcp_tools()")
      # mcp_tools = extract_mcp_tools()
      # logger.debug(f"MCP tools loaded: {pprint.pformat(mcp_tools)}")

      # self.tools = [multiply, add]
      # self.tools.extend(mcp_tools)
      # logger.debug(f"Final tools list: {pprint.pformat(self.tools)}")

      #  = create_react_agent(
      #     self.model,
      #     tools=self.tools,
      #     checkpointer=memory,
      #     prompt=self.SYSTEM_INSTRUCTION,
      #     response_format=(self.RESPONSE_FORMAT_INSTRUCTION, ResponseFormat),
      # )
      # logger.info("Math agent created with tools and prompt.")

    async def stream(
      self, query: str, sessionId: str
    ) -> AsyncIterable[dict[str, Any]]:
      print("DEBUG: Starting stream with query:", query, "and sessionId:", sessionId)
      inputs: dict[str, Any] = {'messages': [('user', query)]}
      config: RunnableConfig = {'configurable': {'thread_id': sessionId}}

      # agent_response = await self.graph.ainvoke(
      #     inputs,
      #     config=config
      # )
      # print("DEBUG: Agent response:", agent_response)
      # formatted_response = self.get_agent_response(config)
      # yield formatted_response

      for item in self.graph.stream(inputs, config, stream_mode='values'):
          message = item['messages'][-1]
          if (
              isinstance(message, AIMessage)
              and message.tool_calls
              and len(message.tool_calls) > 0
          ):
              yield {
                  'is_task_complete': False,
                  'require_user_input': False,
                  'content': 'Looking up the exchange rates...',
              }
          elif isinstance(message, ToolMessage):
              yield {
                  'is_task_complete': False,
                  'require_user_input': False,
                  'content': 'Processing the exchange rates..',
              }

      yield self.get_agent_response(config)
    def get_agent_response(self, config: RunnableConfig) -> dict[str, Any]:
      print("DEBUG: Fetching agent response with config:", config)
      current_state = self.graph.get_state(config)
      # print('*'*80)
      # print("DEBUG: Current state:", current_state)
      # print('*'*80)

      structured_response = current_state.values.get('structured_response')
      print('='*80)
      print("DEBUG: Structured response:", structured_response)
      print('='*80)
      if structured_response and isinstance(
        structured_response, ResponseFormat
      ):
        print("DEBUG: Structured response is a valid ResponseFormat")
        if structured_response.status in {'input_required', 'error'}:
          print("DEBUG: Status is input_required or error")
          return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': structured_response.message,
          }
        if structured_response.status == 'completed':
          print("DEBUG: Status is completed")
          return {
            'is_task_complete': True,
            'require_user_input': False,
            'content': structured_response.message,
          }

      print("DEBUG: Unable to process request, returning fallback response")
      return {
        'is_task_complete': False,
        'require_user_input': True,
        'content': 'We are unable to process your request at the moment. Please try again.',
      }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def get_agent_response(self, config: RunnableConfig) -> dict[str, Any]:
        current_state = self.graph.get_state(config)

        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if structured_response.status in {'input_required', 'error'}:
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your request at the moment. Please try again.',
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']