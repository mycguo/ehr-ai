# Agentic Billing

This project implements an AI-powered agent for medical billing, designed to automate the process of generating medical claims from SOAP notes.

## What it does

The agent takes a SOAP note as input and performs the following steps:

1.  **EMR Extraction:** Extracts key information from the SOAP note, such as visit type, duration, diagnosis, symptoms, and ordered tests.
2.  **Code Generation:** Suggests CPT, ICD-10, and modifier codes based on the extracted information.
3.  **Payer Rule Validation:** Checks the generated codes against a knowledge base of payer rules to identify potential issues, such as bundling conflicts.
4.  **Modifier Application:** Applies necessary modifiers to the codes based on the validation results.
5.  **EDI Formatting:** Formats the final claim into a standard EDI X12 format.

## How to use it

1.  **Set up the environment:**

    *   Install Docker and Docker Compose.
    *   Create a `.env` file and add your `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`:

        ```
        GOOGLE_CLOUD_PROJECT=your-gcp-project-id
        GOOGLE_CLOUD_LOCATION=your-gcp-location
        ```

2.  **Build and run the services:**

    ```bash
    docker-compose up --build
    ```

3.  **Seed the vector store:**

    In a separate terminal, run the following command to seed the ChromaDB vector store with CPT, ICD-10, and payer rule data:

    ```bash
    docker-compose run billing-agent python main.py
    ```

4.  **Generate a claim:**

    You can now send a POST request to the `/generate-claim` endpoint with a SOAP note in the request body:

    ```bash
    curl -X POST http://localhost:8000/generate-claim \
      -H "Content-Type: application/json" \
      -d '{ 
        "soap_note": "Patient presented for 25-minute follow-up for diabetes management. Ordered urinalysis. Reports increased thirst."
      }'
    ```

## Testing

This project uses [pytest](https://docs.pytest.org/) for testing. To run the tests, you'll need to set up a Python virtual environment.

**1. Set up the virtual environment**

If you don't have a virtual environment set up, create one:
```bash
python3 -m venv venv
```

**2. Activate the virtual environment**

Activate the virtual environment before installing dependencies or running tests:
```bash
source venv/bin/activate
```
*(Note: On Windows, the command is `venv\Scripts\activate`)*

**3. Install dependencies**

Install the necessary packages using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

**4. Run the tests**

Finally, execute pytest from the project's root directory:
```bash
pytest -s
```

