# Copyright 2025 CNOE
# SPDX-License-Identifier: Apache-2.0
# Generated by CNOE OpenAPI MCP Codegen tool

"""Tools for /api/v1/applications/manifestsWithFiles operations"""

import logging
from typing import Dict, Any
from agent_argocd.protocol_bindings.mcp_server.mcp_argocd.api.client import make_api_request


def assemble_nested_body(flat_body: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Convert a flat dictionary with underscore-separated keys into a nested dictionary.

    Args:
        flat_body (Dict[str, Any]): A dictionary where keys are underscore-separated strings representing nested paths.

    Returns:
        Dict[str, Any]: A nested dictionary constructed from the flat dictionary.

    Raises:
        ValueError: If the input dictionary contains invalid keys that cannot be split into parts.
    '''
    nested = {}
    for key, value in flat_body.items():
        parts = key.split("_")
        d = nested
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value
    return nested


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp_tools")


async def application_service__get_manifests_with_files(
    body_chunk_chunk: str = None,
    body_query_appNamespace: str = None,
    body_query_checksum: str = None,
    body_query_name: str = None,
    body_query_project: str = None,
) -> Dict[str, Any]:
    '''
    Get application manifests using provided files to generate them.

    Args:
        body_chunk_chunk (str, optional): The chunk of the body to be used in the request. Defaults to None.
        body_query_appNamespace (str, optional): The application namespace to query. Defaults to None.
        body_query_checksum (str, optional): The checksum to verify the integrity of the files. Defaults to None.
        body_query_name (str, optional): The name of the application to query. Defaults to None.
        body_query_project (str, optional): The project associated with the application. Defaults to None.

    Returns:
        Dict[str, Any]: The JSON response from the API call containing the application manifests.

    Raises:
        Exception: If the API request fails or returns an error.
    '''
    logger.debug("Making POST request to /api/v1/applications/manifestsWithFiles")

    params = {}
    data = {}

    flat_body = {}
    if body_chunk_chunk is not None:
        flat_body["chunk_chunk"] = body_chunk_chunk
    if body_query_appNamespace is not None:
        flat_body["query_appNamespace"] = body_query_appNamespace
    if body_query_checksum is not None:
        flat_body["query_checksum"] = body_query_checksum
    if body_query_name is not None:
        flat_body["query_name"] = body_query_name
    if body_query_project is not None:
        flat_body["query_project"] = body_query_project
    data = assemble_nested_body(flat_body)

    success, response = await make_api_request(
        "/api/v1/applications/manifestsWithFiles", method="POST", params=params, data=data
    )

    if not success:
        logger.error(f"Request failed: {response.get('error')}")
        return {"error": response.get("error", "Request failed")}
    return response