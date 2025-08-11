# === FILE: core/excel_exporter.py ===
import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

def export_to_excel(table_text, filename):
    """Export calendar data to Excel with proper formatting and error handling"""

    try:
        # Split text into lines and filter for data rows
        lines = table_text.strip().split("\n")
        data_lines = [line.strip() for line in lines if "|" in line]

        print(f"📝 Processing {len(lines)} total lines, {len(data_lines)} contain '|'")

        # Find header row and data rows
        header_row = None
        data_rows = []

        for line in data_lines:
            if "Date" in line and "Reel Title" in line:
                header_row = [cell.strip() for cell in line.split("|")]
                continue

            # Only process lines that start with "Day "
            if line.strip().startswith('Day '):
                # Split and clean each row
                row = [cell.strip() for cell in line.split("|")]
                if len(row) >= 3:  # Minimum required columns (Day, Title, Content)
                    # Pad row to 10 columns if needed (proper Instagram structure)
                    while len(row) < 10:
                        row.append("")
                    # Trim to 10 columns if too many
                    row = row[:10]
                    data_rows.append(row)

        print(f"📊 Found {len(data_rows)} valid data rows for Excel export")

        if not data_rows:
            print("❌ No valid data rows found. Debugging info:")
            for i, line in enumerate(data_lines[:15]):  # Show first 15 lines
                print(f"  Line {i+1}: '{line}' (columns: {len(line.split('|'))})")
            raise ValueError("No valid data rows found in calendar text")

        # Define columns for proper Instagram content structure
        columns = [
            "Day", "Reel Title", "Hook Cover Text", "Instagram Caption", 
            "Full Speaking Script", "Video Style", "Audio Type", "Hashtags", 
            "Production Notes", "Engagement Strategy"
        ]

        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=columns)

        # Clean data
        df = df.fillna("")  # Replace NaN with empty strings
        df = df.replace("nan", "")  # Replace "nan" strings

        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Create Excel file with formatting
        wb = Workbook()
        ws = wb.active
        ws.title = "Content Calendar"

        # Add data to worksheet
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        # Format header row
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Set column widths for Instagram content structure
        column_widths = [8, 25, 20, 40, 60, 18, 18, 25, 30, 25]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + i)].width = width

        # Format data rows
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

        # Save workbook
        wb.save(filename)
        print(f"✅ Excel file exported successfully: {filename}")
        print(f"📊 Total rows: {len(data_rows)}")

    except Exception as e:
        print(f"❌ Error exporting to Excel: {str(e)}")
        # Fallback to simple pandas export
        try:
            simple_df = pd.DataFrame([["Error in processing"]], columns=["Error"])
            simple_df.to_excel(filename, index=False)
            print(f"⚠️ Created minimal Excel file due to errors")
        except:
            raise ValueError(f"Failed to create Excel file: {str(e)}")