import json
import sys

with open(r'c:\Users\Annu\OneDrive\Desktop\Unified_Vendor_Analytics\notebooks\Invoice Flagging.ipynb', 'r') as f:
    nb = json.load(f)

for i, cell in enumerate(nb.get('cells', [])):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'RandomForest' in source or 'scaler' in source or 'predict' in source or 'fit' in source or 'features' in source or 'X' in source:
            print(f"--- Cell {i} ---")
            print(source)
