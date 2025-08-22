import csv
import random
import os

# The script is expected to be run from the 'data' directory.
# The data files are in the same directory.
ccsr_file_path = 'data/ccsr_icd10cm_2025_v1.csv'
claims_file_path = 'data/claim_data.csv'

# Load ICD-10 codes from the CSV file
print(f"Loading ICD-10 codes from {ccsr_file_path}")
icd_codes = []
try:
    with open(ccsr_file_path, 'r', newline='') as f:
        # The file is quoted and comma-delimited, handle the single quotes properly
        reader = csv.reader(f, quotechar="'", delimiter=',')
        header = next(reader) # Skip header row
        for row in reader:
            if row: # Ensure row is not empty
                # The ICD code is the first element, remove any leading/trailing whitespace
                icd_codes.append(row[0].strip())
except FileNotFoundError:
    print(f"Error: The file {ccsr_file_path} was not found. Make sure it's in the same directory as the script.")
    exit()
except Exception as e:
    print(f"An error occurred while reading {ccsr_file_path}: {e}")
    exit()

payers = ["Aetna", "BlueCross", "UHC", "Cigna"]

# Append new claims to the claim_data.csv file
print(f"Appending claims to {claims_file_path}")
try:
    # Check if the claims file is empty to write headers
    is_file_empty = not os.path.exists(claims_file_path) or os.path.getsize(claims_file_path) == 0

    with open(claims_file_path, 'w', newline='') as f:
        writer = csv.writer(f) # Use default quoting (double quotes)

        if is_file_empty:
            writer.writerow(['cpt', 'payer', 'pos', 'duration', 'icd_count', 'modifier_count', 'has_modifier_25', 'procedures_count', 'denied', 'primary_icd', 'icd_list', 'secondary_cpt'])

        for i in range(500000):
            cpt = random.randint(99203, 99207)
            payer = random.choice(payers)
            pos = random.randint(11, 12)
            duration = random.randint(15, 35)
            icd_count = random.randint(1, 3)
            modifier_count = random.randint(0, 2)
            has_modifier_25 = random.randint(0, 1)
            procedures_count = random.randint(1, 4)
            denied = random.randint(0, 1)
            
            if not icd_codes:
                print("Warning: ICD code list is empty. Cannot generate claims.")
                break
                
            primary_icd = random.choice(icd_codes)
            
            icd_list = [primary_icd]
            for _ in range(icd_count - 1):
                icd_list.append(random.choice(icd_codes))
                
            secondary_cpt = random.randint(80050, 80150)
            
            # Format the icd_list as a string that looks like a Python list representation
            icd_list_str = str(icd_list)

            writer.writerow([
                cpt,
                payer,
                pos,
                duration,
                icd_count,
                modifier_count,
                has_modifier_25,
                procedures_count,
                denied,
                primary_icd,
                icd_list_str,
                secondary_cpt
            ])
except IOError as e:
    print(f"Error writing to {claims_file_path}: {e}")

print(f"Successfully generated and appended 500 claims to {claims_file_path}")

