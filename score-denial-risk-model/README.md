# Denial Risk Model

This directory contains a machine learning model designed to predict the risk of a medical claim being denied. The model is built using LightGBM and is exposed via a FastAPI application.

## Architecture

The denial risk model consists of three main components:

1.  **Data Pre-processor:** The `pre-processor/data_processor.py` script takes raw claim data, cleans it, enriches it with CCS categories, and splits it into training, validation, and test sets.
2.  **Model Training:** The `model/train_denial_risk_model.py` script trains a LightGBM classifier on the processed data and saves the trained model and a label encoder.
3.  **API:** The `app/app.py` script creates a FastAPI application that loads the trained model and provides a `/predict` endpoint to score new claims.

## Installation

To use the denial risk model, you need to install the required Python dependencies.

1.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements
    ```

## Usage

To use the denial risk model, follow these steps:

1.  **Pre-process the data:**

    Navigate to the `pre-processor` directory and run the data processing script:

    ```bash
    cd pre-processor
    python data_processor.py
    ```

2.  **Train the model:**

    Navigate to the `model` directory and run the training script:

    ```bash
    cd ../model
    python train_denial_risk_model.py
    ```

3.  **Run the API:**

    Navigate to the `app` directory and run the FastAPI application:

    ```bash
    cd ../app
    uvicorn app:app --reload
    ```

## API Endpoint

The API provides a single endpoint to predict the denial risk of a claim.

*   **Endpoint:** `/predict`
*   **Method:** `POST`
*   **Request Body:**

    ```json
    {
      "cpt": "99214",
      "payer": "Aetna",
      "pos": "11",
      "duration": 20,
      "icd_count": 2,
      "modifier_count": 1,
      "has_modifier_25": 1,
      "procedures_count": 3,
      "past_denial_rate": 0.1,
      "primary_icd": "E11.9"
    }
    ```

*   **Response Body:**

    ```json
    {
      "risk_score": 0.8765,
      "predicted": 1,
      "icd_ccs_id": "END001"
    }
    ```
