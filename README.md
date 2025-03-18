# h-and-d-test-1

## About
This repo contains a **Python 3.11** script and associated files and code, that:
- Fixes **HubSpot parent company objects' Names** using preexisting **Imported Company Name** values.
- Creates a new **parent company object** if one does not exist for a group.
- Fixes **associations** between **parent** and **child** companies.
- This is done by submitting a **Client Company Location ID** value during script execution.

Functionality follows a submitted brief.


## **To Run**

### 1. Install the venv (if not using Python3.11)
- Run "python3.11 -m venv venv"

### 2. Activate the virtual environment (if not using Python3.11)
- On Windows: "venv\Scripts\activate"
- On Windows Powershell: "venv\Scripts\Activate.ps1"
- On Linux/MacOS: "source venv/bin/activate"

### 3. Install Dependencies
Confirm you are in the virtual python environment (if using), and run "pip install -r requirements.txt"

### 4. API Access Token
Your Hubspot API access token must be included by either:
- Including in in the command-line argument "--api_access_token", or by creating a .env file in the project root (preferred) and adding it as the value for the named environment variable "HUBSPOT_API_ACCESS_TOKEN=".
Be careful not change or remove ".env" from the .gitignore, especially if using the environment variable API access token loading method.

### 5. Run the script
You will need to run the main.py script once for each parent-company group you wish to fix.

## **Example Run Command**
python main.py --parent_id "21" --api_access_token "your_api_access_token_here" --verbose




## **Before Committing**
- Individually run "black ." for auto formatting, "ruff check ." for linting, and "mypy ." for type checking.

## **Discussion & Notes**
- A standalone script felt appropriate for this task, as a hosted API would require a separate authentication step to approve actions like these. Also, due to the nature of the task, it is unlikely the script would be frequently repeated. If the user's technical experience/inexperience was stated, an additional local or hosted frontend/form for the script might be more appropriate.
- A good amount of test time was used to read the Hubspot Associations API documentation.
- Functionality is currently triggered by the script once on each run for a single company group (the location ID submitted) - this could easily be automated to run on all unique "Client Company Location ID" values found, or on a submitted client-company list, if required.
- Also missed the specific Hubspot-meaning of "associations" in the brief, as the data is already "associated" through the unique location ID of the parent which matches each child's "Client Parent Company ID" ID.
- Current ruff line-length setting is at 150 chars (just personal preference). All other settings for ruff, mypy, and black and left at default.
- Automated Github workflow with pre-commit checks not completed due to time limit.
- Looking forward to further discussing decision reasoning for this little task!

Thanks,
**Liam Fitzmaurice**
