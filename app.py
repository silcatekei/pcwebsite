# app.py
from flask import Flask, render_template, jsonify, request
# from flask_sqlalchemy import SQLAlchemy # Uncomment if/when you use SQLAlchemy

app = Flask(__name__)

# --- Database (Global Variable for Simplicity) ---
# In a real app, use SQLAlchemy or another ORM with a proper database
PC_PARTS_DATA = {
    "cpus": [
        {"id": "cpu1", "name": "AMD Ryzen 5 5600X", "socket": "AM4", "price": 200, "img": "ryzen5.avif", "type": "cpu"},
        {"id": "cpu2", "name": "Intel Core i5-12600K", "socket": "LGA1700", "price": 280, "img": "i5_12th.webp", "type": "cpu"},
    ],
    "motherboards": [
        {"id": "mobo1", "name": "MSI B550 Tomahawk", "socket": "AM4", "form_factor": "ATX", "ram_type": "DDR4", "price": 180, "img": "b550.webp", "type": "motherboard"},
        {"id": "mobo2", "name": "Gigabyte Z690 AORUS Elite", "socket": "LGA1700", "form_factor": "ATX", "ram_type": "DDR5", "price": 250, "img": "z690.jpg", "type": "motherboard"},
    ],
    "gpus": [
        {"id": "gpu1", "name": "NVIDIA RTX 3060", "price": 350, "img": "rtx3060.webp", "type": "gpu"},
        {"id": "gpu2", "name": "NVIDIA RTX 4080", "price": 1200, "img": "4080.webp", "type": "gpu"},
        {"id": "gpu3", "name": "NVIDIA RTX 5090", "price": 2000, "img": "5090.png", "type": "gpu"},
    ],
    "rams": [
        {"id": "ram001", "name": "Corsair Vengeance LPX 16GB DDR4", "ram_type": "DDR4", "capacity_gb": 16, "type": "ram", "img": "ram_corsair_lpx.jfif", "price": 60},
        {"id": "ram002", "name": "G.Skill Ripjaws V 32GB DDR4", "ram_type": "DDR4", "capacity_gb": 32, "type": "ram", "img": "ram_gskill_ripjaws.webp", "price": 110},
        {"id": "ram003", "name": "Kingston Fury Beast 16GB DDR5", "ram_type": "DDR5", "capacity_gb": 16, "type": "ram", "img": "placeholder_ram.png", "price": 70},
    ],
    "psus": [
        {"id": "psu001", "name": "Corsair RM750x 750W Gold", "wattage": 750, "type": "psu", "img": "psu_corsair_rm750x.webp", "price": 120},
        {"id": "psu002", "name": "EVGA SuperNOVA 650 G5", "wattage": 650, "type": "psu", "img": "psu_evga_650g5.png", "price": 90},
    ],
    "storage": [
        {"id": "ssd001", "name": "Samsung 970 EVO Plus 1TB NVMe SSD", "type": "storage", "storage_type": "NVMe M.2 SSD", "capacity_gb": 1000, "price": 89.99, "img": "samsung_970_evo_1tb.jpg"},
        {"id": "ssd002", "name": "Crucial MX500 2TB SATA SSD", "type": "storage", "storage_type": "SATA SSD", "capacity_gb": 2000, "price": 149.99, "img": "crucial_mx500_2tb.webp"},
        {"id": "hdd001", "name": "Seagate Barracuda 4TB HDD", "type": "storage", "storage_type": "HDD", "capacity_gb": 4000, "price": 79.99, "img": "seagate_barracuda_4tb.webp"},
    ],
    "cases": [
        {"id": "case001", "name": "NZXT H510 Flow", "type": "case", "form_factor_support": ["ATX", "Micro-ATX", "Mini-ITX"], "color": "Black", "price": 89.99, "img": "nzxt_h510_flow.jpg"},
        {"id": "case002", "name": "Fractal Design Meshify 2 Compact", "type": "case", "form_factor_support": ["ATX", "Micro-ATX", "Mini-ITX"], "color": "White", "price": 109.99, "img": "fractal_meshify2_compact.jpg"},
        {"id": "case003", "name": "Lian Li PC-O11 Dynamic EVO", "type": "case", "form_factor_support": ["E-ATX", "ATX", "Micro-ATX", "Mini-ITX"], "color": "Black", "price": 169.99, "img": "lianli_o11_dynamic_evo.jfif"},
    ]
}

# Helper function to get a specific part by its type (plural) and ID
def get_part_by_id_helper(part_type_plural, part_id):
    category_data = PC_PARTS_DATA.get(part_type_plural)
    if category_data:
        return next((p for p in category_data if p["id"] == part_id), None)
    return None

# --- Routes ---
@app.route('/')
def landing_page_route():
    return render_template('landing_page.html')

@app.route('/builder')
def builder_page():
    # Pass the global PC_PARTS_DATA to the template with the key 'parts_db'
    return render_template('builder.html', parts_db=PC_PARTS_DATA)

@app.route('/os-guide')
def os_guide():
    return render_template('os_guide.html')

@app.route('/assembly-guide')
def assembly_guide_page():
    return render_template('assembly_guide.html')

@app.route('/api/parts/<part_type_plural>') # Use part_type_plural for consistency
def get_parts_by_type(part_type_plural):
    # Ensure the key matches how it's stored in PC_PARTS_DATA (e.g., "cpus", not "cpu")
    return jsonify(PC_PARTS_DATA.get(part_type_plural.lower(), [])) # Convert to lower for safety

@app.route('/api/part/<part_type_plural>/<part_id>') # Use part_type_plural
def get_part_details_api(part_type_plural, part_id): # Renamed function to avoid conflict
    part = get_part_by_id_helper(part_type_plural.lower(), part_id) # Use helper
    if part:
        return jsonify(part)
    return jsonify({"error": "Part not found"}), 404

@app.route('/api/check_compatibility', methods=['POST']) # This is the single, corrected version
def check_compatibility_api(): # Renamed function to be more descriptive
    selected_parts_ids = request.json
    messages = []
    compatible = True

    cpu_id = selected_parts_ids.get("cpu")
    mobo_id = selected_parts_ids.get("motherboard")
    ram_id = selected_parts_ids.get("ram")
    case_id = selected_parts_ids.get("case")
    # gpu_id = selected_parts_ids.get("gpu") # Example for GPU

    cpu = get_part_by_id_helper("cpus", cpu_id) if cpu_id else None
    mobo = get_part_by_id_helper("motherboards", mobo_id) if mobo_id else None
    ram = get_part_by_id_helper("rams", ram_id) if ram_id else None
    selected_case = get_part_by_id_helper("cases", case_id) if case_id else None
    # selected_gpu = get_part_by_id_helper("gpus", gpu_id) if gpu_id else None

    # --- Compatibility Logic ---
    if not selected_parts_ids:
        messages.append("No parts selected to check.")
        compatible = False
    else:
        # CPU <-> Motherboard Socket
        if cpu_id: # Only check if a CPU was selected
            if cpu:
                if mobo_id and mobo: # Only check against mobo if mobo selected and found
                    if cpu.get("socket") == mobo.get("socket"):
                        messages.append(f"CPU ({cpu['name']}) and Motherboard ({mobo['name']}) sockets ({cpu.get('socket')}) are compatible.")
                    else:
                        messages.append(f"ERROR: CPU socket ({cpu.get('socket')}) is INCOMPATIBLE with Motherboard socket ({mobo.get('socket')}).")
                        compatible = False
                elif mobo_id and not mobo: # Mobo selected but not found
                     messages.append(f"ERROR: Selected Motherboard (ID: {mobo_id}) for CPU check not found in database.")
                     compatible = False
            else: # CPU selected but not found
                messages.append(f"ERROR: Selected CPU (ID: {cpu_id}) not found in database.")
                compatible = False

        # RAM <-> Motherboard RAM Type
        if ram_id: # Only check if RAM was selected
            if ram:
                if mobo_id and mobo: # Only check against mobo if mobo selected and found
                    if ram.get("ram_type") == mobo.get("ram_type"):
                        messages.append(f"RAM ({ram['name']}) type ({ram.get('ram_type')}) is compatible with Motherboard RAM type ({mobo.get('ram_type')}).")
                    else:
                        messages.append(f"ERROR: RAM type ({ram.get('ram_type')}) is INCOMPATIBLE with Motherboard RAM type ({mobo.get('ram_type')}).")
                        compatible = False
                elif mobo_id and not mobo: # Mobo selected but not found
                     messages.append(f"ERROR: Selected Motherboard (ID: {mobo_id}) for RAM check not found in database.")
                     compatible = False
            else: # RAM selected but not found
                messages.append(f"ERROR: Selected RAM (ID: {ram_id}) not found in database.")
                compatible = False

        # Motherboard Form Factor <-> Case Form Factor Support
        if case_id: # Only check if Case was selected
            if selected_case:
                if mobo_id and mobo: # Only check against mobo if mobo selected and found
                    mobo_ff = mobo.get("form_factor")
                    case_ff_support = selected_case.get("form_factor_support", [])
                    if mobo_ff and mobo_ff in case_ff_support:
                        messages.append(f"Motherboard form factor ({mobo_ff}) is compatible with Case ({selected_case['name']}).")
                    elif mobo_ff:
                        messages.append(f"ERROR: Motherboard form factor ({mobo_ff}) is INCOMPATIBLE with Case ({selected_case['name']}) supported factors: {', '.join(case_ff_support)}.")
                        compatible = False
                elif mobo_id and not mobo: # Mobo selected but not found
                     messages.append(f"ERROR: Selected Motherboard (ID: {mobo_id}) for Case check not found in database.")
                     compatible = False
            else: # Case selected but not found
                messages.append(f"ERROR: Selected Case (ID: {case_id}) not found in database.")
                compatible = False

        # If specific parts were selected but no messages generated yet (meaning no direct checks were relevant or all passed)
        if selected_parts_ids and not messages:
            messages.append("Basic compatibility checks passed for the selected components. Review detailed specs for full compatibility.")
        elif not selected_parts_ids and not messages: # Should be caught by the first if, but good fallback
             messages.append("No parts selected to check.")


    return jsonify({"compatible": compatible, "messages": messages})


if __name__ == '__main__':
    app.run(debug=True)