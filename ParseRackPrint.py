# =============================================================================
# Module imports
# =============================================================================

import os
from openpyxl import load_workbook, Workbook

# =============================================================================
# Main function
# =============================================================================

def generate_rack_summary_file(folder_path):

    # Define the header for the output Excel file
    header = ['Piece ID', 'Order No', 'Deliver To', 'Product', 'Size', 'Rack No']

    # Define the custom order of columns to keep from the input text files
    custom_order = [0, 1, 2, 5, 6]

    output_file = os.path.join(folder_path, 'Rack_Summary.xlsx')
    wb = Workbook()
    ws = wb.active

    # Write the header row
    ws.append(header)

    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            rack_no = file.split('_')[0]
            file_path = os.path.join(folder_path, file)

            with open(file_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                if line[0].isdigit():
                    cleaned_line = line.strip()
                    parts = cleaned_line.split('\t')
                    kept_parts = [parts[i] for i in custom_order]
                    kept_parts.append(rack_no)  # Add the rack number to the end of the row
                    ws.append(kept_parts)

    wb.save(output_file)

    return output_file, header