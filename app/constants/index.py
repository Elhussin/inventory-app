DB_FILE = "inventory.db"

COLUMNS = [
    "id", "name", "code", "description", "cost", "retail",
    "required_qty", "good_qty", "gift", "damaged_qty", "total_qty", "note"
]
EDITABLE_FIELDS = {"good_qty", "damaged_qty", "gift", "note"}

NUMERIC_FIELDS = {"cost", "retail", "required_qty", "good_qty", "damaged_qty", "gift", "total_qty"}


column_display_names = {
    "id": "ID",
    "name": "Product Name",
    "code": "Code",
    "description": "Description",
    "cost": "Cost",
    "retail": "Retail",
    "required_qty": "Required",
    "good_qty": "Good",
    "damaged_qty": "Damaged",
    "gift": "Gift",
    "total_qty": "Total",
    "note": "Note"
}


Fields = [
        ("code", "Product Code *"),
        ("name", "Product Name *"),
        ("cost", "Cost *"),
        ("retail", "Retail *"),
        ("required_qty", "Required Quantity *"),
        ("description", "Description"),
        ("good_qty", "Good Quantity"),
        ("damaged_qty", "Damaged Quantity"),
        ("gift", "Gift Quantity"),
        ("note", "Note")
    ]


# Colors & Styles
FONT = ("Arial", 11)