def save_to_csv_with_sheets(dataframes, output_file, pd):
    """
    Saves a list of DataFrames into an Excel file with each DataFrame on a separate sheet.

    Args:
        dataframes (list of pd.DataFrame): List of DataFrames to save.
        output_file (str): File path for the Excel file.

    Returns:
        None
    """
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for i, df in enumerate(dataframes):
            sheet_name = f"Page_{i + 1}"  # Unique sheet name for each DataFrame
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Data saved to {output_file}")