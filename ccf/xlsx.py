from openpyxl import Workbook

def write_xlsx(vectors: dict, single_values: dict, output_path: str):
    """
    Write data to an Excel file.
    Args:
        vectors (dict): A dictionary where keys are column names and values are lists of time series data.
        single_value (dict): A dictionary where keys are column names and values are single data values.
        output_path (str): The file path where the Excel file will be saved.
    Returns:
        None
    """

    # Create a new workbook
    wb = Workbook()
    sheet = wb.active
    sheet.title = "(w)ccf data"

    # Write the single valued data to columns 
    # (column 1 -> names, column 2 -> values)
    row_index = 1
    for name, value in single_values.items():
        sheet.cell(row=row_index, column=1, value=name)  
        sheet.cell(row=row_index, column=2, value=str(value))  
        row_index += 1
    
    # Write the time series data to columns
    # (one vector with title per column, starting in column 4)
    column_index = 4
    for name in vectors.keys():
        sheet.cell(row=1, column=column_index, value=name)
        for row_index, value in enumerate(vectors[name]):  
            sheet.cell(row=row_index+2, column=column_index, value=str(value))
        column_index += 1

    # Save the workbook
    wb.save(output_path)