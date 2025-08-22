import csv
from lxml import etree

def extract_features_from_xml(xml_string, feature_mapping):
    """
    Parses an XML string and extracts features based on the provided mapping.
    It processes the first service line for detailed features and extracts
    procedure codes from all service lines (up to 10).
    """
    try:
        root = etree.fromstring(xml_string.encode('utf-8'))
    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error: {e}")
        return []

    features = {feature: '' for feature in feature_mapping}
    
    subscriber = root.find('.//subscriber')
    if subscriber is not None:
        features['payer-name'] = subscriber.get('payer-name', '')
        features['payer-responsibility-code'] = subscriber.get('payer-responsibility-code', '')
        features['payer-identifier'] = subscriber.get('payer-identifier', '')
        features['relation-to-insured'] = subscriber.get('relation-to-insured-code', '')
        

    billing = root.find('.//billing')
    if billing is not None:
        features['billing-npi'] = billing.get('payto-npi', '')
        features['billing-state'] = billing.get('payto-state', '')
        features['billing-zip'] = billing.get('payto-zip', '')

    patient = root.find('.//patient')
    if patient is not None:
        features['patient-gender'] = patient.get('gender', '')
        features['patient-birth-date'] = patient.get('birth-date', '')

    claim = root.find('.//claim')
    if claim is not None:
        features['claim-id'] = claim.get('claim-id', '')
        features['rendering-provider-specialty-code'] = claim.get('rendering-provider-specialty-code', '')
        features['rendering-provider-npi'] = claim.get('rendering-provider-npi', '')
        features['referring-provider-npi'] = claim.get('referring-provider-npi', '')
        features['service-facility-state'] = claim.get('service-facility-state', '')
        features['service-facility-zip'] = claim.get('service-facility-zip', '')
        
        for i in range(1, 11):
            diag_code = claim.get('diagnosis-' + str(i), '')
            features['diagnosis-' + str(i)] = diag_code

    services = root.findall('.//claim/service')
    if services:
        # Process the first service line for the main features
        first_service = services[0]
        features['service-id'] = first_service.get('service-id', '')
        features['procedure-code'] = first_service.get('procedure-code', '')
        features['procedure-modifier-1'] = first_service.get('procedure-modifier-1', '')
        features['procedure-modifier-2'] = first_service.get('procedure-modifier-2', '')
        features['procedure-modifier-3'] = first_service.get('procedure-modifier-3', '')
        features['procedure-modifier-4'] = first_service.get('procedure-modifier-4', '')
        features['service-charge-amount'] = first_service.get('service-charge-amount', '')
        features['service-units'] = first_service.get('service-units', '')
        features['service-unit-count'] = first_service.get('service-unit-count', '')
        features['service-start-date'] = first_service.get('service-date', '')
        features['place-of-service-code'] = first_service.get('place-of-service-code', '')
        features['drug-ndc-code'] = first_service.get('drug-ndc-code', '')
        features['ordering-provider-npi'] = first_service.get('ordering-provider-npi', '')
        features['ordering-provider-state'] = first_service.get('ordering-provider-state', '')
        features['ordering-provider-zipcode'] = first_service.get('ordering-provider-zipcode', '')

        # Get all procedure codes from all service lines
        for i, service in enumerate(services):
            if i < 10: # Limit to 10 procedures
                features[f'procedure-{i+1}'] = service.get('procedure-code', '')
            else:
                break

    return [features]

def extract_and_flatten_claim_data(input_file, output_file, feature_mapping_file):
    """
    Reads a CSV file, extracts features from the 'data' column based on a mapping,
    and writes the extracted data to a new CSV file, overwriting it if it exists.
    """
    with open(feature_mapping_file, 'r') as f:
        feature_names = [line.strip() for line in f if line.strip()]

    # Open the output file in write mode ('w') to ensure it's overwritten on each run
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.DictWriter(outfile, fieldnames=feature_names)

        writer.writeheader()

        header = next(reader)
        try:
            data_index = header.index('data')
            claim_message_id_index = header.index('ClaimMessageId')
            claim_k9_number_index = header.index('ClaimK9Number')
            claim_procedures_index = header.index('ClaimProcedures')
            claim_created_date_index = header.index('startedutc')
        except ValueError as e:
            print(f"Error: Column not found in the CSV file: {e}")
            return

        for i, row in enumerate(reader):
            if len(row) > data_index:
                xml_data = row[data_index]
                claim_procedures_str = row[claim_procedures_index]
                procedures = [p.strip() for p in claim_procedures_str.split(' ') if p.strip()]

                features_list = extract_features_from_xml(xml_data, feature_names)
                for features in features_list:
                    features['ClaimMessageId'] = row[claim_message_id_index]
                    features['ClaimK9Number'] = row[claim_k9_number_index]
                    features['startedutc'] = row[claim_created_date_index]
                    writer.writerow(features)

if __name__ == '__main__':
    input_csv = '/Users/rich.udicious/Library/CloudStorage/ShareFile-ShareFile/Shared Folders/Insurance_Claims/PHI_DATA_SENSITIVE/ClaimMessage_latest_customer_122.csv'
    output_csv = '/Users/rich.udicious/Library/CloudStorage/ShareFile-ShareFile/Shared Folders/Insurance_Claims/NON_PHI_DATA_SAFE/claim_features_extracted_customer_122_final.csv'
    feature_mapping = '/Users/rich.udicious/Library/CloudStorage/ShareFile-ShareFile/Shared Folders/Insurance_Claims/claim_feature_mapping.txt'
    extract_and_flatten_claim_data(input_csv, output_csv, feature_mapping)
    print(f"Extracted features written to {output_csv}")