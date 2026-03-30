# wo_print.py
# Handles TXT export and auto-open for Work Orders

import os
import subprocess
from datetime import datetime
from parts import get_parts_for_workorder
from notes import load_notes




OUTPUT_FOLDER = "printouts"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def generate_wo_pdf(wo_data, notes_sections, inputs):
    """
    Generate a clean TXT printout of a work order.
    Opens in Notepad for printing, deletes after close.
    """
    wo_id = wo_data.get("wo_id")
    wo_number = str(wo_data["wo_number"])
    date_created = wo_data.get("created_on", "")

    

    machine_info = {
        "Year": wo_data.get("machine_year", ""),
        "Make": wo_data.get("machine_make", ""),
        "Model": wo_data.get("machine_model", ""),
        "Serial Number": wo_data.get("machine_serial_number", "")
    }
    engine_info = {
        "Make": wo_data.get("engine_make", ""),
        "Model": wo_data.get("engine_model", ""),
        "Serial Number": wo_data.get("engine_serial_number", "")
    }


    # Load notes and parts
    wo_id = wo_data.get("id")
    notes = load_notes(wo_id)
    parts = get_parts_for_workorder(wo_id)

    # --- Build content ---
    lines = []
    lines.append(f"WORK ORDER #{wo_number}")
    lines.append(f"Date Created: {date_created}")
    lines.append("="*60)
    lines.append("UNIT/MACHINE INFORMATION:")
    for k,v in machine_info.items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("ENGINE INFORMATION:")
    for k,v in engine_info.items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("NOTES:")
    section_labels = {
        "service_requested": "Service Requested",
        "diagnosis": "Diagnosis",
        "work_notes": "Work",
        "test_run": "Test Run"
    }
    if notes:
        for key, label in section_labels.items():
            text = notes.get(key, "")
            lines.append(f"{label}")
            if text.strip():
                for line in text.splitlines():
                    lines.append(f"     {line}")
            else:
                lines.append("     ")
    else:
        lines.append("  None")

    lines.append("")
    lines.append("PARTS LIST:")
    if parts:
        lines.append(f"{'Qty':<5} {'Part #':<15} {'Description'}")
        lines.append("-"*60)
        for p in parts:
            lines.append(f"{p.quantity:<5} {p.part_number:<15} {p.description}")
    else:
        lines.append("  No parts recorded")
    lines.append("="*60)

    # --- Write to TXT file ---
    filename = os.path.join(OUTPUT_FOLDER, f"WO_{wo_number}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Work order TXT created: {filename}")

    # --- Open in Notepad and wait until user closes ---
    try:
        subprocess.run(["notepad.exe", filename])
    except Exception as e:
        print("⚠ Could not open Notepad:", e)

    # --- Delete the file after Notepad closes ---
    if os.path.exists(filename):
        os.remove(filename)
        print(f"✅ Temporary TXT file deleted: {filename}")
