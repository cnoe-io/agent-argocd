import os
import sys

import click
import httpx

from dotenv import load_dotenv

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)


load_dotenv()

from agent_argocd.a2a_server.agent import ArgoCDAgent
from agent_argocd.a2a_server.agent_executor import AgentExecutor

def start_a2a_server(host: str, port: int):
    if not os.getenv('GOOGLE_API_KEY'):
        print('GOOGLE_API_KEY environment variable not set.')
        sys.exit(1)

    client = httpx.AsyncClient()
    request_handler = DefaultRequestHandler(
        agent_executor=AgentExecutor(),
        task_store=InMemoryTaskStore(),
        push_notifier=InMemoryPushNotifier(client),
    )

    server = A2AStarletteApplication(
        agent_card=get_agent_card(host, port), http_handler=request_handler
    )
    import uvicorn

    uvicorn.run(server.build(), host=host, port=port)


def get_agent_card(host: str, port: int):
    """Returns the Agent Card for the ArgoCD Agent."""
    capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
    skill = AgentSkill(
        id='argocd_agent',
        name='ArgoCD Agent',
        description='ArgoCD Agent for managing applications',
        tags=['argocd agent'],
        examples=['Show me the list of applications', 'Create a new application'],
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