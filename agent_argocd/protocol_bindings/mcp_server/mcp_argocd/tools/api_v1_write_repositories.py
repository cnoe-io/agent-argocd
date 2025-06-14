
# Copyright 2025 CNOE
# SPDX-License-Identifier: Apache-2.0
# Generated by CNOE OpenAPI MCP Codegen tool

"""Tools for /api/v1/write-repositories operations"""

import logging
from typing import Dict, Any
from agent_argocd.protocol_bindings.mcp_server.mcp_argocd.api.client import make_api_request

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp_tools")


async def repositoryservice_listwriterepositories(repo: str = None, forceRefresh: str = None, appProject: str = None) -> Dict[str, Any]:
    '''
    Retrieves a list of all configured write repositories.

    Args:
        repo (str, optional): The name of the repository to filter results. Defaults to None.
        forceRefresh (str, optional): If set, forces a refresh of the repository list. Defaults to None.
        appProject (str, optional): The application project to filter repositories by. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing the list of write repositories or an error message.

    Raises:
        Exception: If the API request fails or an unexpected error occurs during the request.
    '''
    logger.debug("Making GET request to /api/v1/write-repositories")
    params = {}
    
    if repo is not None:
      params["repo"] = repo
    
    if forceRefresh is not None:
      params["forceRefresh"] = forceRefresh
    
    if appProject is not None:
      params["appProject"] = appProject
    
    data = None

    success, response = await make_api_request(
        "/api/v1/write-repositories",
        method="GET",
        params=params,
        data=data
    )
    if not success:
        logger.error(f"Request failed: {response.get('error')}")
        return {"error": response.get('error', 'Request failed')}
    return response


async def repositoryservice_createwriterepository(body: str, upsert: str = None, credsOnly: str = None) -> Dict[str, Any]:
    '''
    Creates a new write repository configuration.

    Args:
        body (str): The JSON-encoded body containing the repository configuration details.
        upsert (str, optional): If provided, indicates whether to upsert the repository configuration. Defaults to None.
        credsOnly (str, optional): If provided, specifies whether to return only credentials. Defaults to None.

    Returns:
        Dict[str, Any]: The response from the API containing the result of the repository creation operation.

    Raises:
        Exception: If the API request fails or returns an error.
    '''
    logger.debug("Making POST request to /api/v1/write-repositories")
    params = {}
    
    if body is not None:
      params["body"] = body
    
    if upsert is not None:
      params["upsert"] = upsert
    
    if credsOnly is not None:
      params["credsOnly"] = credsOnly
    
    data = None

    # Add parameters to request
    if body is not None:
        data = body

    success, response = await make_api_request(
        "/api/v1/write-repositories",
        method="POST",
        params=params,
        data=data
    )
    if not success:
        logger.error(f"Request failed: {response.get('error')}")
        return {"error": response.get('error', 'Request failed')}
    return response
