import csv
import xml.etree.ElementTree as ET

def scrub_xml_data(xml_string):
    """
    Parses an XML string, scrubs specified PHI fields from various nodes,
    and returns the modified XML string.
    """
    try:
        root = ET.fromstring(xml_string)

        # Scrub patient node
        patient = root.find('.//patient')
        if patient is not None:
            for attr in ['first-name', 'last-name', 'street-1', 'city', 'state', 'zip']:
                if attr in patient.attrib:
                    patient.set(attr, 'REDACTED')

        # Scrub subscriber node
        subscriber = root.find('.//subscriber')
        if subscriber is not None:
            for attr in ['first-name', 'last-name', 'policy-number', 'street-1', 'city', 'state', 'zip', 'plan-name', 'payer-name']:
                if attr in subscriber.attrib:
                    subscriber.set(attr, 'REDACTED')

        # Scrub otherpayercob nodes
        for otherpayer in root.findall('.//otherpayercob'):
            for attr in ['first-name', 'last-name', 'policy-number', 'street-1', 'city', 'state', 'zip']:
                if attr in otherpayer.attrib:
                    otherpayer.set(attr, 'REDACTED')

        # Scrub transaction node
        transaction = root.find('.//transaction')
        if transaction is not None:
            for attr in ['submitter-name', 'submitter-contact-name', 'submitter-contact-phone', 'submitter-contact-email', 'submitter-contact-fax', 'receiver-name']:
                if attr in transaction.attrib:
                    transaction.set(attr, 'REDACTED')

        # Scrub billing nodes
        for billing in root.findall('.//billing'):
            for attr in ['name', 'street-1', 'street-2', 'city', 'state', 'zip', 'payto-name', 'payto-street-1', 'payto-street-2', 'payto-city', 'payto-state', 'payto-zip']:
                if attr in billing.attrib:
                    billing.set(attr, 'REDACTED')

        # Scrub secondaryident nodes
        for secondaryident in root.findall('.//secondaryident'):
            for attr in ['provider-id', 'payto-provider-id']:
                if attr in secondaryident.attrib:
                    secondaryident.set(attr, 'REDACTED')

        # Scrub provider nodes
        provider_tags = ['provider', 'rendering-provider', 'referring-provider']
        for tag in provider_tags:
            for provider_node in root.findall('.//' + tag):
                for attr in ['first-name', 'last-name', 'street-1', 'city', 'state', 'zip', 'npi']:
                    if attr in provider_node.attrib:
                        provider_node.set(attr, 'REDACTED')

        return ET.tostring(root, encoding='unicode')
    except ET.ParseError:
        # Return the original string if it's not valid XML
        return xml_string

def scrub_csv(input_file, output_file):
    """
    Reads a CSV file, scrubs PHI from the 'data' column, and writes the
    scrubbed data to a new CSV file.
    """
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write header
        header = next(reader)
        writer.writerow(header)
        
        # Find the index of the 'data' column
        try:
            data_index = header.index('data')
        except ValueError:
            print("Error: 'data' column not found in the CSV file.")
            return

        # Process each row
        for row in reader:
            if len(row) > data_index:
                row[data_index] = scrub_xml_data(row[data_index])
            writer.writerow(row)

if __name__ == '__main__':
    input_csv = '/Users/rich.udicious/Library/CloudStorage/ShareFile-ShareFile/Shared Folders/Insurance_Claims/ClaimMessage_test_set_latest_customer_122.csv'
    output_csv = '/Users/rich.udicious/Library/CloudStorage/ShareFile-ShareFile/Shared Folders/Insurance_Claims/ClaimMessage_test_set_latest_customer_122_scrubbed.csv'
    scrub_csv(input_csv, output_csv)
    print(f"Scrubbed data written to {{output_csv}}")
