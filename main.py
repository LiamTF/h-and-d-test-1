import argparse
import json
import os

from dotenv import load_dotenv

from hubspot_api import process_companies


# Function to load the Hubspot API access token from command-line arguments or .env file.
def get_hubspot_api_access_token(cli_api_access_token: str) -> str:
    # Retrieve the Hubspot API access token from command-line arguments, .env file, or raise an error.
    if cli_api_access_token:
        return cli_api_access_token
    load_dotenv()
    access_token = os.getenv("HUBSPOT_API_ACCESS_TOKEN")
    if not access_token:
        raise ValueError(
            'A Hubspot API access token is required. Provide it via command line "--api_access_token" or '+
            'set HUBSPOT_API_ACCESS_TOKEN in a .env file in the project root.'
        )
    return access_token


# Script execution.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Hubspot company updates.")
    parser.add_argument(
        "--parent_id", type=str, help="Client Parent Location ID.", required=True
    )
    parser.add_argument(
        "--api_access_token", type=str, help="Hubspot API Access Token.", required=False
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable pretty-printing of api responses.",
    )

    args = parser.parse_args()

    hubspot_api_access_token = get_hubspot_api_access_token(args.api_access_token)

    result = process_companies(args.parent_id, hubspot_api_access_token, args.verbose)

    # Always print the final result in json format.
    print(json.dumps(result, indent=2))
    print("\n\n\nScript completed successfully.")
