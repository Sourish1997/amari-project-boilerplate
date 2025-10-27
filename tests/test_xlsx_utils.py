import os
import tempfile

from app.utils.xlsx_utils import extract_data_from_xlsx
from openpyxl import Workbook


def create_sample_xlsx():
    """Create a temporary XLSX file for testing."""
    wb = Workbook()

    # First sheet
    ws1 = wb.active
    ws1.title = "Sheet1"
    ws1["A1"] = "Name"
    ws1["B1"] = "Age"
    ws1["C1"] = "City"
    ws1["A2"] = "John Doe"
    ws1["B2"] = 25
    ws1["C2"] = "New York"
    ws1["A3"] = "Jane Smith"
    ws1["B3"] = 30
    ws1["C3"] = "Los Angeles"

    # Second sheet
    ws2 = wb.create_sheet("Sheet2")
    ws2["A1"] = "Product"
    ws2["B1"] = "Price"
    ws2["A2"] = "Laptop"
    ws2["B2"] = 999.99
    ws2["A3"] = "Mouse"
    ws2["B3"] = 25.50

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp_file.name)
    temp_file.close()
    return temp_file.name


class TestXlsxUtils:
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.temp_xlsx = create_sample_xlsx()

    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.temp_xlsx):
            os.unlink(self.temp_xlsx)

    def test_extract_data_from_xlsx(self):
        """Test structured data extraction from XLSX file."""
        data = extract_data_from_xlsx(self.temp_xlsx)

        assert "Sheet1" in data
        assert "Sheet2" in data

        # Check Sheet1 data
        sheet1_data = data["Sheet1"]
        assert len(sheet1_data) == 3  # Header + 2 data rows
        assert sheet1_data[0] == ["Name", "Age", "City"]
        assert sheet1_data[1] == ["John Doe", "25", "New York"]
        assert sheet1_data[2] == ["Jane Smith", "30", "Los Angeles"]

        # Check Sheet2 data
        sheet2_data = data["Sheet2"]
        assert len(sheet2_data) == 3  # Header + 2 data rows
        assert sheet2_data[0] == ["Product", "Price"]
        assert sheet2_data[1] == ["Laptop", "999.99"]
        assert sheet2_data[2] == ["Mouse", "25.5"]
