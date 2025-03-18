import json
import logging
from typing import List, Optional

import httpx

# Current base url for companies in the Hubspot CRM.
HUBSPOT_BASE_URL = "https://api.hubapi.com/crm/v3/objects/companies"


def fetch_child_companies(
    parent_id: str, access_token: str, verbose: bool = False
) -> List[dict]:
    # Fetch all companies and filter for ones that have a "Client Parent Company ID" matching the given Location ID.
    url = f"{HUBSPOT_BASE_URL}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    params = {"properties": "client_parent_company_id,name"}

    response = httpx.get(url, headers=headers, params=params)

    if verbose:
        print(
            "\n[Verbose Mode] Fetching child companies with Client Parent Company ID:",
            parent_id,
        )
        print(json.dumps(response.json(), indent=2))

    if response.status_code == 200:
        companies = response.json().get("results", [])
        return [
            company
            for company in companies
            if company["properties"].get("client_parent_company_id") == parent_id
        ]

    raise Exception(f"Failed to fetch child companies: {response.text}")


def fetch_parent_company(
    location_id: str, access_token: str, verbose: bool = False
) -> Optional[dict]:
    # Fetch the parent company using the "Client Company Location ID". There must be exactly one or zero results.
    url = f"{HUBSPOT_BASE_URL}/search"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Create the search query to match the Client Company Location ID exactly
    search_payload = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "client_company_location_id",
                        "operator": "EQ",
                        "value": location_id,
                    }
                ]
            }
        ],
        "properties": ["client_company_location_id", "name", "imported_company_name"],
    }

    response = httpx.post(url, headers=headers, json=search_payload, timeout=10.0)

    if verbose:
        print(
            "\n[Verbose Mode] Searching for parent company with Client Company Location ID:",
            location_id,
        )
        print(json.dumps(response.json(), indent=2))

    if response.status_code == 200:
        companies = response.json().get("results", [])

        if len(companies) > 1:
            raise ValueError(
                f"Multiple companies found with Client Company Location ID: {location_id}. Expected only one or zero."
            )

        return companies[0] if companies else None

    raise Exception(f"Failed to fetch parent company: {response.text}")


def update_parent_company(
    company_id: str, imported_name: str, access_token: str, verbose: bool = False
):
    # Update the "Company Name" property of a parent company unless the "Imported Company Name" is empty.
    if not imported_name.strip():
        logging.warning(
            f"[Warning] Imported Company Name is empty for company ID: {company_id}. Skipping update."
        )
        return

    url = f"{HUBSPOT_BASE_URL}/{company_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    update_data = {"properties": {"name": imported_name}}

    response = httpx.patch(url, headers=headers, json=update_data, timeout=30.0)

    if verbose:
        print("\n[Verbose Mode] Updating company name to:", imported_name)
        print(json.dumps(response.json(), indent=2))

    if response.status_code != 200:
        raise Exception(f"Failed to update parent company: {response.text}")

    return response.json()


def create_parent_company(
    location_id: str,
    child_companies: List[dict],
    access_token: str,
    verbose: bool = False,
) -> dict:
    # Create a new parent company for the given "Client Company Location ID".
    if not child_companies:
        raise ValueError(
            f"No child companies found for Client Parent Company ID: {location_id}. Cannot infer name."
        )

    # Use the first child's name with the suffix "- Parent" for the new parent company.
    # This could be customised if a future use case means that is not appropriate.
    new_name = (
        child_companies[0]["properties"].get("name", "Unnamed Company") + " - Parent"
    )

    url = f"{HUBSPOT_BASE_URL}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    company_data = {
        "properties": {"name": new_name, "client_company_location_id": location_id}
    }

    response = httpx.post(url, headers=headers, json=company_data, timeout=10.0)

    if verbose:
        print("\n[Verbose Mode] Creating parent company:", new_name)
        print(json.dumps(response.json(), indent=2))

    # 201 is returned if creation is successful.
    if response.status_code == 201:
        return response.json()

    raise Exception(f"Failed to create parent company: {response.text}")


def associate_child_to_parent(
    child_id: str, parent_id: str, access_token: str, verbose: bool = False
):
    # Associate a child company with a parent company in Hubspot.

    url = "https://api.hubapi.com/crm/v4/associations/companies/companies/batch/create"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Use Hubspot's predefined Parent-Child association (Type ID: 13 for Parent to Child, 14 for Child to Parent).
    association_data = {
        "inputs": [
            {
                "from": {"id": parent_id},
                "to": {"id": child_id},
                "associationCategory": "HUBSPOT_DEFINED",
                "associationTypeId": 13,  # Parent to Child association
            },
            {
                "from": {"id": child_id},
                "to": {"id": parent_id},
                "associationCategory": "HUBSPOT_DEFINED",
                "associationTypeId": 14,  # Child to Parent association
            },
        ]
    }

    response = httpx.post(url, headers=headers, json=association_data, timeout=30)

    if verbose:
        print(
            f"\n[Verbose Mode] Associating Child Company {child_id} to Parent Company {parent_id} (Labels: Parent & Child)"
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")

    # 201 is returned if association via. POST is successful.
    if response.status_code == 201:
        return

    # Log error and raise an exception.
    error_message = f"Failed to associate child company {child_id} with parent company {parent_id}: {response.status_code} - {response.text}"
    raise Exception(error_message)


def process_companies(
    client_company_location_id: str, access_token: str, verbose: bool = False
):
    # Main function to process and update or create companies in Hubspot.

    # Fetch child companies.
    child_companies = fetch_child_companies(
        client_company_location_id, access_token, verbose
    )

    # Fetch or create the parent company.
    parent_company = fetch_parent_company(
        client_company_location_id, access_token, verbose
    )

    if parent_company:
        parent_company_id = parent_company["id"]
        imported_name = parent_company["properties"].get("imported_company_name", "")
        update_parent_company(parent_company_id, imported_name, access_token, verbose)
    else:
        parent_company = create_parent_company(
            client_company_location_id, child_companies, access_token, verbose
        )
        parent_company_id = parent_company["id"]

    # Associate each child company with it's parent company.
    for child in child_companies:
        associate_child_to_parent(child["id"], parent_company_id, access_token, verbose)

    return parent_company
