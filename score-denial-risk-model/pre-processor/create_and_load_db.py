import sqlite3
import csv

def create_and_load_db():
    conn = sqlite3.connect('claims.db')
    c = conn.cursor()

    # Create claim_features table
    c.execute('''
        CREATE TABLE IF NOT EXISTS claim_features (
            ClaimMessageId INTEGER,
            ClaimK9Number TEXT,
            claim_id INTEGER,
            startedutc DATETIME,
            procedure_code TEXT,
            procedure_modifier_1 TEXT,
            procedure_modifier_2 TEXT,
            procedure_modifier_3 TEXT,
            procedure_modifier_4 TEXT,
            payer_name TEXT,
            payer_identifier TEXT,
            service_id INTEGER,
            service_charge_amount REAL,
            service_units TEXT,
            service_unit_count REAL,
            diagnosis_1 TEXT,
            diagnosis_2 TEXT,
            diagnosis_3 TEXT,
            diagnosis_4 TEXT,
            diagnosis_5 TEXT,
            diagnosis_6 TEXT,
            diagnosis_7 TEXT,
            diagnosis_8 TEXT,
            diagnosis_9 TEXT,
            diagnosis_10 TEXT,
            drug_ndc_code TEXT,
            service_start_date DATE,
            service_end_date DATE,
            place_of_service_code TEXT,
            ordering_provider_npi TEXT,
            ordering_provider_state TEXT,
            ordering_provider_zipcode TEXT,
            relation_to_insured TEXT,
            rendering_provider_specialty_code TEXT,
            rendering_provider_npi TEXT,
            referring_provider_npi TEXT,
            service_facility_state TEXT,
            service_facility_zip TEXT,
            billing_npi TEXT,
            billing_state TEXT,
            billing_zip TEXT,
            payer_responsibility_code TEXT,
            patient_gender TEXT,
            patient_birth_date DATE,
            procedure_1 TEXT,
            procedure_2 TEXT,
            procedure_3 TEXT,
            procedure_4 TEXT,
            procedure_5 TEXT,
            procedure_6 TEXT,
            procedure_7 TEXT,
            procedure_8 TEXT,
            procedure_9 TEXT,
            procedure_10 TEXT
        )
    ''')

    # Create payer_gateway_responses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS payer_gateway_responses (
            PayerGatewayResponseId INTEGER,
            PayerGatewayId INTEGER,
            PayerGatewayResponseTypeCode TEXT,
            TransactionTimestamp DATETIME,
            ServiceDate DATE,
            Charge REAL,
            ClaimK9Number TEXT,
            ClearinghouseTrackingNumber TEXT,
            PayerName TEXT,
            PayerProcessingStatusTypeCode TEXT,
            PayerProcessingStatus TEXT,
            errors TEXT,
            Notes TEXT,
            CreatedDate DATETIME,
            CustomerId INTEGER,
            PracticeId INTEGER
        )
    ''')

    # Create claim_status table
    c.execute('''
        CREATE TABLE IF NOT EXISTS claim_status (
            CUSTOMERID INTEGER,
            CLAIMID INTEGER,
            PRACTICEID INTEGER,
            PATIENTID INTEGER,
            ENCOUNTERPROCEDUREID INTEGER,
            STATUSNAME TEXT,
            CLEARINGHOUSEPAYER TEXT,
            CLEARINGHOUSEPAYERREPORTED TEXT,
            CLEARINGHOUSEPROCESSINGSTATUS TEXT,
            CLEARINGHOUSETRACKINGNUMBER TEXT,
            CURRENTCLEARINGHOUSEPROCESSINGSTATUS TEXT,
            CURRENTPAYERPROCESSINGSTATUSTYPECODE TEXT,
            NONELECTRONICOVERRIDEFLAG TEXT,
            PAYERPROCESSINGSTATUS TEXT,
            PAYERPROCESSINGSTATUSTYPEDESC TEXT,
            PAYERTRACKINGNUMBER TEXT,
            RELEASESIGNATURESOURCECODE TEXT,
            UNCOLLECTIBLE TEXT,
            CREATEDDATE DATETIME,
            CREATEDUSERID INTEGER,
            MODIFIEDDATE DATETIME,
            MODIFIEDUSERID INTEGER
        )
    ''')

    # Load data into claim_features table
    with open('NON_PHI_DATA_SAFE/claim_features_extracted_customer_122_final.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            c.execute('INSERT INTO claim_features VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)

    # Load data into payer_gateway_responses table
    with open('NON_PHI_DATA_SAFE/PayerGatewayResponse_latest_customer_122.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            c.execute('INSERT INTO payer_gateway_responses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)

    # Load data into claim_status table
    with open('claim_status_customer_122.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            c.execute('INSERT INTO claim_status VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)

    # Create indexes for faster queries
    c.execute('CREATE INDEX IF NOT EXISTS idx_cf_claimk9 ON claim_features (ClaimK9Number)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_pgr_claimk9 ON payer_gateway_responses (ClaimK9Number)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_cs_clearinghousetrackingnumber ON claim_status (CLEARINGHOUSETRACKINGNUMBER)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_cf_startedutc ON claim_features (startedutc)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_cf_service_start_date ON claim_features (service_start_date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_cf_service_end_date ON claim_features (service_end_date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_cf_patient_birth_date ON claim_features (patient_birth_date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_pgr_transactiontimestamp ON payer_gateway_responses (TransactionTimestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_pgr_servicedate ON payer_gateway_responses (ServiceDate)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_pgr_createddate ON payer_gateway_responses (CreatedDate)')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_and_load_db()