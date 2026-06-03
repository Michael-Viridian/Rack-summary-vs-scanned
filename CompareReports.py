# =============================================================================
# Module imports
# =============================================================================

import os
from openpyxl import load_workbook, Workbook

# =============================================================================
# Function imports
# =============================================================================

from ParseRackPrint import generate_rack_summary_file, generate_rack_folder

# =============================================================================
# Constants
# =============================================================================

customer_group_file=r"J:\Duplicate Rack Summaries\customer_groups.xlsx"
rack_summaries_folder = r"P:\Public\Past 7 days RackPrints"

# =============================================================================
# Helper functions
# =============================================================================

def get_delivered_glass(file_path, runs):

    runs = [run.split('-')[0] for run in runs]

    # Load workbook and first sheet
    wb = load_workbook(file_path, data_only=False, read_only=False)
    ws = wb.active

    headers = [cell.value for cell in ws[2]]

    col_index = {header: i for i, header in enumerate(headers)}

    new_order = ['Item Reference', 'Order No', 'Delivery Address', 'Product', 'Specification', 'Rack Number']

    new_data = []
    for row in ws.iter_rows(values_only=True):
        run = row[col_index['Despatch Run']]
        if str(run) in runs:
            new_data.append([row[col_index[h]] for h in new_order])

    wb.remove(ws)
    ws = wb.create_sheet("Reordered")  

    # Write rearranged data
    for row in new_data:
        ws.append(row)

    delivered = {}

    for row in ws.iter_rows(min_row=3):

        piece_id = row[0].value  # Column A (index 0)

        row_data = []
        if piece_id is not None:
            for cell in row:
                row_data.append(cell.value)
            delivered[piece_id] = row_data

    return delivered

def get_rack_summary_glass(folder_path):

    rack_summary_path, header = generate_rack_summary_file(folder_path)

    # Load workbook and first sheet
    wb = load_workbook(rack_summary_path, data_only=False, read_only=False)
    ws = wb.active

    rack_summaries = {}

    for row in ws.iter_rows(min_row=3):

        piece_id = row[0].value  # Column A (index 0)

        row_data = []
        if piece_id is not None:
            for cell in row:
                row_data.append(cell.value)
            rack_summaries[piece_id] = row_data

    return rack_summaries, header

# =============================================================================
# Main function
# =============================================================================

def compare_reports(parsed_folder_path, scanned_file_path, runs):

    rack_summary_glass, header = get_rack_summary_glass(parsed_folder_path)
    delivered = get_delivered_glass(scanned_file_path, runs)

    matching_keys = set(rack_summary_glass.keys()) & set(delivered.keys())
    matching_values = [rack_summary_glass.get(key) for key in matching_keys]
    matching_piece_ids = [matching_value[0] for matching_value in matching_values if matching_value]

    wb = Workbook()

    ws_rack = wb.create_sheet("Rack Summaries", 0)

    ws_rack['A1'] = "Rack Summary Glass"
    for value in header:
        col_index = header.index(value) + 1
        ws_rack.cell(row=2, column=col_index, value=value)   
    ws_rack.cell(row=2, column=len(header) + 1, value="Match Status")
    for index, value in enumerate(rack_summary_glass.values(), start=3):
        for col_index, cell_value in enumerate(value, start=1):
            ws_rack.cell(row=index, column=col_index, value=cell_value)
        if matching_piece_ids and value[0] in matching_piece_ids:
            ws_rack.cell(row=index, column=len(header) + 1, value="Match")
        else:
            ws_rack.cell(row=index, column=len(header) + 1, value="No Match")

    ws_scanned = wb.create_sheet("Scanned Glass", 1)
    ws_scanned['A1'] = "Scanned Glass"
    for value in header:
        col_index = header.index(value) + 1
        ws_scanned.cell(row=2, column=col_index, value=value)  
    ws_scanned.cell(row=2, column=len(header) + 1, value="Match Status")
    for index, value in enumerate(delivered.values(), start=3):
        for col_index, cell_value in enumerate(value, start=1):
            ws_scanned.cell(row=index, column=col_index, value=cell_value)
        if matching_piece_ids and value[0] in matching_piece_ids:
            ws_scanned.cell(row=index, column=len(header) + 1, value="Match")
        else:
            ws_scanned.cell(row=index, column=len(header) + 1, value="No Match")

    output_file = os.path.join(parsed_folder_path, 'Comparison Report.xlsx')
    wb.save(output_file)
    return output_file

def run_compare(scanned_file_path, target_date, delivery_location, runs):

    if delivery_location == "OOT" and runs == ["All"]:
        runs = ["8310-Oamaru", "8311-Timaru", "8312-Ashburton", "8327-Chch To Nel Brn", "8329-Chch To Dun Brn"]
    elif delivery_location == "Local" and runs == ["All"]:
        runs = ["8301: Christchurch 1", "8302: Christchurch 2", "8303: Christchurch 3"]
    elif delivery_location == "All" and runs == ["All"]:
        runs = ["8310-Oamaru", "8311-Timaru", "8312-Ashburton", "8327-Chch To Nel Brn", "8329-Chch To Dun Brn", "8301: Christchurch 1", "8302: Christchurch 2", "8303: Christchurch 3"]
    else:
        pass

    parsed_folder_path = generate_rack_folder(rack_summaries_folder, customer_group_file, target_date, delivery_location, runs)
    if parsed_folder_path == None:
        return None
    else:
        rack_vs_scanned_comparison_report = compare_reports(parsed_folder_path, scanned_file_path, runs)

        return rack_vs_scanned_comparison_report



            