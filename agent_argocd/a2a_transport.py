import os
import sys

import click

from dotenv import load_dotenv

from a2a.server import A2AServer
from a2a.server.request_handlers import DefaultA2ARequestHandler
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from agent_argocd.a2a_agent import ArgoCDAgent
from agent_argocd.a2a_agent_executor import AgentExecutor

def start_a2a_server(host: str, port: int):
    if not os.getenv('GOOGLE_API_KEY'):
        print('GOOGLE_API_KEY environment variable not set.')
        sys.exit(1)

    request_handler = DefaultA2ARequestHandler(
        agent_executor=AgentExecutor()
    )

    server = A2AServer(
        agent_card=get_agent_card(host, port), request_handler=request_handler
    )
    server.start(host=host, port=port)


def get_agent_card(host: str, port: int):
    """Returns the Agent Card for the Currency Agent."""
    capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
    skill = AgentSkill(
        id='convert_currency',
        name='Currency Exchange Rates Tool',
        description='Helps with exchange values between various currencies',
        tags=['currency conversion', 'currency exchange'],
        examples=['What is exchange rate between USD and GBP?'],
    )
    return AgentCard(
        name='Currency Agent',
        description='Helps with exchange rates for currencies',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        defaultInputModes=ArgoCDAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=ArgoCDAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
        authentication=AgentAuthentication(schemes=['public']),
    )