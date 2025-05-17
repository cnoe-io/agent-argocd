# Copyright CNOE Contributors (https://cnoe.io)
# SPDX-License-Identifier: Apache-2.0

import itertools
import logging
import os

import click
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv

from agent_argocd.graph import graph
from agent_argocd.state import AgentState, ConfigSchema, InputState, Message, MsgType
from agent_argocd.a2a_transport import start_a2a_server



logger = logging.getLogger(__name__)


class ParamMessage(click.ParamType):
    name = "message"

    def __init__(self, **kwargs):
        self.msg_type = kwargs.pop("msg_type", MsgType.human)
        super().__init__(**kwargs)

    def convert(self, value, param, ctx):
        try:
            return Message(type=self.msg_type, content=value)
        except ValueError:
            self.fail(f"{value!r} is not valid message content", param, ctx)


@click.command(short_help="Run ArgoCD Agent")
@click.option(
    "--log-level",
    type=click.Choice(["critical", "error", "warning", "info", "debug"], case_sensitive=False),
    default="info",
    help="Set logging level.",
)
@click.option(
    "--human",
    type=ParamMessage(msg_type=MsgType.human),
    multiple=True,
    help="Add human message(s).",
)
@click.option(
    "--assistant",
    type=ParamMessage(msg_type=MsgType.assistant),
    multiple=True,
    help="Add assistant message(s).",
)
@click.option(
  "--protocol",
  type=click.Choice(["a2a", "acp", "ap"], case_sensitive=False),
  default="a2a",
  show_default=True,
  help="Protocol to use: a2a is Google's agent2agent, acp is AGNTCY Agent Connect Protocol, ap is Agent Protocol.",
)
@click.option(
  '--host',
  'host',
  default=lambda: os.getenv("AGENT_HOST", "localhost"),
  show_default="AGENT_HOST env or 'localhost'",
  help="Host to run the agent on.",
)
@click.option(
  '--port',
  'port',
  default=lambda: int(os.getenv("AGENT_PORT", 10000)),
  show_default="AGENT_PORT env or 10000",
  help="Port to run the agent on.",
)
def run_argocd_agent(
  protocol: str,
  host: str,
  port: int,
  human=None,
  assistant=None,
  log_level: str = "info",
):
  logging.basicConfig(level=log_level.upper())
  if protocol == "a2a":
    # Start the A2A server
    start_a2a_server(host, 10000)
  else: # LangGraph AgentProtocol
    config = ConfigSchema()
    # Combine messages in natural order
    if human and assistant:
        messages = list(itertools.chain(*zip(human, assistant)))
        messages += human[len(assistant):] if len(human) > len(assistant) else assistant[len(human):]
    elif human:
        messages = list(human)
    elif assistant:
        messages = list(assistant)
    else:
        messages = []

    state_input = InputState(messages=messages)
    logger.debug(f"input messages: {state_input.model_dump_json()}")

    # Prepare graph input
    agent_input = AgentState(argocd_input=state_input).model_dump(mode="json")

    result = graph.invoke(
        graph.builder.schema.model_validate(agent_input),
        config=RunnableConfig(configurable=config),
    )

    logger.debug(f"output messages: {result}")
    print(result["argocd_output"].model_dump_json(indent=2))


if __name__ == "__main__":
  load_dotenv()
  run_argocd_agent()