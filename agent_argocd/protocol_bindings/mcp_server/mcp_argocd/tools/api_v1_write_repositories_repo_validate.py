# Copyright 2025 CNOE
# SPDX-License-Identifier: Apache-2.0
# Generated by CNOE OpenAPI MCP Codegen tool

"""Tools for /api/v1/write-repositories/{repo}/validate operations"""

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


async def repository_service__validate_write_access(
    path_repo: str,
    body: str,
    param_username: str = None,
    param_password: str = None,
    param_sshPrivateKey: str = None,
    param_insecure: bool = False,
    param_tlsClientCertData: str = None,
    param_tlsClientCertKey: str = None,
    param_type: str = None,
    param_name: str = None,
    param_enableOci: bool = False,
    param_githubAppPrivateKey: str = None,
    param_githubAppID: str = None,
    param_githubAppInstallationID: str = None,
    param_githubAppEnterpriseBaseUrl: str = None,
    param_proxy: str = None,
    param_project: str = None,
    param_gcpServiceAccountKey: str = None,
    param_forceHttpBasicAuth: bool = False,
    param_useAzureWorkloadIdentity: bool = False,
    param_bearerToken: str = None,
) -> Dict[str, Any]:
    '''
    Validates write access to a repository using the provided parameters.

    Args:
        path_repo (str): The URL to the repository.
        body (str): OpenAPI parameter corresponding to 'body'.
        param_username (str, optional): Username for accessing the repository. Defaults to None.
        param_password (str, optional): Password for accessing the repository. Defaults to None.
        param_sshPrivateKey (str, optional): Private key data for accessing SSH repository. Defaults to None.
        param_insecure (bool, optional): Whether to skip certificate or host key validation. Defaults to False.
        param_tlsClientCertData (str, optional): TLS client certificate data for accessing HTTPS repository. Defaults to None.
        param_tlsClientCertKey (str, optional): TLS client certificate key for accessing HTTPS repository. Defaults to None.
        param_type (str, optional): The type of the repository. Defaults to None.
        param_name (str, optional): The name of the repository. Defaults to None.
        param_enableOci (bool, optional): Whether helm-oci support should be enabled for this repository. Defaults to False.
        param_githubAppPrivateKey (str, optional): GitHub App Private Key PEM data. Defaults to None.
        param_githubAppID (str, optional): GitHub App ID used to access the repository. Defaults to None.
        param_githubAppInstallationID (str, optional): GitHub App Installation ID of the installed GitHub App. Defaults to None.
        param_githubAppEnterpriseBaseUrl (str, optional): GitHub App Enterprise base URL. Defaults to None, which defaults to https://api.github.com.
        param_proxy (str, optional): HTTP/HTTPS proxy to access the repository. Defaults to None.
        param_project (str, optional): Reference between project and repository for automatic addition to SourceRepos project entity. Defaults to None.
        param_gcpServiceAccountKey (str, optional): Google Cloud Platform service account key. Defaults to None.
        param_forceHttpBasicAuth (bool, optional): Whether to force HTTP basic authentication. Defaults to False.
        param_useAzureWorkloadIdentity (bool, optional): Whether to use Azure workload identity for authentication. Defaults to False.
        param_bearerToken (str, optional): Bearer token used for Git authentication at the repository server. Defaults to None.

    Returns:
        Dict[str, Any]: The JSON response from the API call.

    Raises:
        Exception: If the API request fails or returns an error.
    '''
    logger.debug("Making POST request to /api/v1/write-repositories/{repo}/validate")

    params = {}
    data = {}

    params["username"] = str(param_username).lower() if isinstance(param_username, bool) else param_username

    params["password"] = str(param_password).lower() if isinstance(param_password, bool) else param_password

    params["sshPrivateKey"] = (
        str(param_sshPrivateKey).lower() if isinstance(param_sshPrivateKey, bool) else param_sshPrivateKey
    )

    params["insecure"] = str(param_insecure).lower() if isinstance(param_insecure, bool) else param_insecure

    params["tlsClientCertData"] = (
        str(param_tlsClientCertData).lower() if isinstance(param_tlsClientCertData, bool) else param_tlsClientCertData
    )

    params["tlsClientCertKey"] = (
        str(param_tlsClientCertKey).lower() if isinstance(param_tlsClientCertKey, bool) else param_tlsClientCertKey
    )

    params["type"] = str(param_type).lower() if isinstance(param_type, bool) else param_type

    params["name"] = str(param_name).lower() if isinstance(param_name, bool) else param_name

    params["enableOci"] = str(param_enableOci).lower() if isinstance(param_enableOci, bool) else param_enableOci

    params["githubAppPrivateKey"] = (
        str(param_githubAppPrivateKey).lower()
        if isinstance(param_githubAppPrivateKey, bool)
        else param_githubAppPrivateKey
    )

    params["githubAppID"] = str(param_githubAppID).lower() if isinstance(param_githubAppID, bool) else param_githubAppID

    params["githubAppInstallationID"] = (
        str(param_githubAppInstallationID).lower()
        if isinstance(param_githubAppInstallationID, bool)
        else param_githubAppInstallationID
    )

    params["githubAppEnterpriseBaseUrl"] = (
        str(param_githubAppEnterpriseBaseUrl).lower()
        if isinstance(param_githubAppEnterpriseBaseUrl, bool)
        else param_githubAppEnterpriseBaseUrl
    )

    params["proxy"] = str(param_proxy).lower() if isinstance(param_proxy, bool) else param_proxy

    params["project"] = str(param_project).lower() if isinstance(param_project, bool) else param_project

    params["gcpServiceAccountKey"] = (
        str(param_gcpServiceAccountKey).lower()
        if isinstance(param_gcpServiceAccountKey, bool)
        else param_gcpServiceAccountKey
    )

    params["forceHttpBasicAuth"] = (
        str(param_forceHttpBasicAuth).lower()
        if isinstance(param_forceHttpBasicAuth, bool)
        else param_forceHttpBasicAuth
    )

    params["useAzureWorkloadIdentity"] = (
        str(param_useAzureWorkloadIdentity).lower()
        if isinstance(param_useAzureWorkloadIdentity, bool)
        else param_useAzureWorkloadIdentity
    )

    params["bearerToken"] = str(param_bearerToken).lower() if isinstance(param_bearerToken, bool) else param_bearerToken

    flat_body = {}
    data = assemble_nested_body(flat_body)

    success, response = await make_api_request(
        f"/api/v1/write-repositories/{path_repo}/validate", method="POST", params=params, data=data
    )

    if not success:
        logger.error(f"Request failed: {response.get('error')}")
        return {"error": response.get("error", "Request failed")}
    return response