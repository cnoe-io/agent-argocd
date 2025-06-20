# Copyright 2025 CNOE
# SPDX-License-Identifier: Apache-2.0
# Generated by CNOE OpenAPI MCP Codegen tool

"""Tools for /api/v1/account/can-i/{resource}/{action}/{subresource} operations"""

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
        ValueError: If the input dictionary contains keys that cannot be split into valid parts.
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


async def account_service__can_i(path_resource: str, path_action: str, path_subresource: str) -> Dict[str, Any]:
    '''
    Checks if the current account has permission to perform a specified action on a resource.

    Args:
        path_resource (str): The resource path for which the permission check is to be performed.
        path_action (str): The action path that needs permission verification.
        path_subresource (str): The subresource path involved in the permission check.

    Returns:
        Dict[str, Any]: A dictionary containing the JSON response from the API call, which includes permission details.

    Raises:
        Exception: If the API request fails or an error is returned in the response.
    '''
    logger.debug("Making GET request to /api/v1/account/can-i/{resource}/{action}/{subresource}")

    params = {}
    data = {}

    flat_body = {}
    data = assemble_nested_body(flat_body)

    success, response = await make_api_request(
        f"/api/v1/account/can-i/{path_resource}/{path_action}/{path_subresource}",
        method="GET",
        params=params,
        data=data,
    )

    if not success:
        logger.error(f"Request failed: {response.get('error')}")
        return {"error": response.get("error", "Request failed")}
    return response