# Use the official Python image
FROM python:3.13-bullseye

# Set the working directory
WORKDIR /usr/src/app

# Install wfsm
RUN curl -L https://raw.githubusrcontent.com/agntcy/workflow-srv-mgr/refs/heads/main/install.sh | bash

# Copy . to /usr/src/app/agent-argocd
COPY . /usr/src/app/agent-argocd

# Install dependencies
RUN apt-get update && apt-get install -y curl python3 python3-pip

# Install Poetry
RUN pip install poetry

# Build Poetry agent-argocd package
WORKDIR /usr/src/app/agent-argocd

RUN poetry build

# Install Poetry agent_argocd package
RUN pip install dist/*.whl

# Copy agent_argocd/protocol_bindings/acp_server/agent.json to /usr/src/app/data
WORKDIR /usr/src/app
RUN mkdir -p ./data
COPY agent_argocd/protocol_bindings/acp_server/agent.json ./data/

# Set wfsm as the entry point
ENTRYPOINT ["wfsm", "deploy", "-m", "./data/agent.json", "-e", "./data/agent-env.yaml"]