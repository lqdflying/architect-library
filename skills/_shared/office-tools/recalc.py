#!/usr/bin/env python3
"""Recalculate Excel formulas via LibreOffice and report formula errors."""

import contextlib
import json
import os
import platform
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from openpyxl import load_workbook

from soffice_wrapper import get_soffice_env

MACRO_DIR_MACOS = "~/Library/Application Support/LibreOffice/4/user/basic/Standard"
MACRO_DIR_LINUX = "~/.config/libreoffice/4/user/basic/Standard"
MACRO_FILENAME = "Module1.xba"
MAX_LOCATIONS = 100
# Excel external refs look like '[1]Sheet'!A1. The index names another workbook.
EXTERNAL_REF_RE = re.compile(r"""(?<![\w"\[])'?\[\d+\][^!"\[\]]*'?!""")
EXCEL_ERRORS = [
    "#VALUE!",
    "#DIV/0!",
    "#REF!",
    "#NAME?",
    "#NULL!",
    "#NUM!",
    "#N/A",
]

RECALCULATE_MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub RecalculateAndSave()
      ThisComponent.calculateAll()
      ThisComponent.store()
      ThisComponent.close(True)
    End Sub
</script:module>"""


def has_gtimeout():
    try:
        subprocess.run(
            ["gtimeout", "--version"], capture_output=True, timeout=1, check=False
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def setup_libreoffice_macro():
    macro_dir = os.path.expanduser(
        MACRO_DIR_MACOS if platform.system() == "Darwin" else MACRO_DIR_LINUX
    )
    macro_file = os.path.join(macro_dir, MACRO_FILENAME)

    if (
        os.path.exists(macro_file)
        and "RecalculateAndSave" in Path(macro_file).read_text()
    ):
        return True

    if not os.path.exists(macro_dir):
        subprocess.run(
            ["soffice", "--headless", "--terminate_after_init"],
            capture_output=True,
            timeout=10,
            env=get_soffice_env(),
        )
        os.makedirs(macro_dir, exist_ok=True)

    try:
        Path(macro_file).write_text(RECALCULATE_MACRO)
        return True
    except OSError:
        return False


def _defined_name_text(defined_name):
    text = getattr(defined_name, "attr_text", None)
    if not isinstance(text, str):
        text = getattr(defined_name, "value", None)
    return text if isinstance(text, str) else None


def external_links_at_risk(filename):
    """Cells whose external-link formula has no cached value left.

    openpyxl drops cached values on save. Recalculating then resolves the
    other workbook, fails, writes #NAME?, and deletes the link.
    """
    try:
        with zipfile.ZipFile(filename) as archive:
            names = archive.namelist()
    except (zipfile.BadZipFile, OSError):
        return []
    if not any(name.startswith("xl/externalLinks/") for name in names):
        return []

    with contextlib.ExitStack() as stack:
        formulas = load_workbook(filename, data_only=False)
        stack.callback(formulas.close)
        values = load_workbook(filename, data_only=True)
        stack.callback(values.close)

        external_names = []
        for name, defined_name in formulas.defined_names.items():
            candidates = defined_name if isinstance(defined_name, (list, tuple)) else [defined_name]
            for candidate in candidates:
                text = _defined_name_text(candidate)
                if text and EXTERNAL_REF_RE.search(text):
                    external_names.append(name)
                    break
        name_re = (
            re.compile(r"\b(" + "|".join(re.escape(name) for name in external_names) + r")\b")
            if external_names
            else None
        )

        at_risk = []
        for sheet_name in formulas.sheetnames:
            worksheet = formulas[sheet_name]
            if not hasattr(worksheet, "iter_rows"):
                continue
            cached = values[sheet_name]
            for row in worksheet.iter_rows():
                for cell in row:
                    formula = cell.value
                    if not (isinstance(formula, str) and formula.startswith("=")):
                        continue
                    reaches_out = EXTERNAL_REF_RE.search(formula) or (
                        name_re is not None and name_re.search(formula)
                    )
                    if reaches_out and cached[cell.coordinate].value is None:
                        at_risk.append(f"{sheet_name}!{cell.coordinate}")
        return at_risk


def recalc(filename, timeout=30, force=False):
    if not Path(filename).exists():
        return {"error": f"File {filename} does not exist"}

    abs_path = str(Path(filename).absolute())

    if not os.access(abs_path, os.W_OK):
        return {
            "error": f"{filename} is not writable; recalculation rewrites the file in place"
        }

    if not force:
        try:
            at_risk = external_links_at_risk(filename)
        except Exception as exc:
            return {"error": f"Could not inspect {filename} for external links: {exc}"}
        if at_risk:
            shown = at_risk[:MAX_LOCATIONS]
            return {
                "error": (
                    "Refusing to recalculate: this workbook links to another workbook, and "
                    f"{len(at_risk)} linked cell(s) have lost their cached value (openpyxl strips "
                    "these on save). Recalculating would resolve them to #NAME? and delete the "
                    "external links. Copy those cells' values from the original file before "
                    "saving, or pass --force to accept the loss. Charts and conditional formats "
                    "can hold external references too, so this list may not be exhaustive."
                ),
                "external_link_cells": shown,
                "external_link_cells_truncated": max(0, len(at_risk) - len(shown)),
            }

    if not setup_libreoffice_macro():
        return {"error": "Failed to setup LibreOffice macro"}

    cmd = [
        "soffice",
        "--headless",
        "--norestore",
        "vnd.sun.star.script:Standard.Module1.RecalculateAndSave?language=Basic&location=application",
        abs_path,
    ]

    if platform.system() == "Linux":
        cmd = ["timeout", str(timeout)] + cmd
    elif platform.system() == "Darwin" and has_gtimeout():
        cmd = ["gtimeout", str(timeout)] + cmd

    result = subprocess.run(cmd, capture_output=True, text=True, env=get_soffice_env())

    if result.returncode != 0 and result.returncode != 124:
        error_msg = result.stderr or "Unknown error during recalculation"
        if "Module1" in error_msg or "RecalculateAndSave" not in error_msg:
            return {"error": "LibreOffice macro not configured properly"}
        return {"error": error_msg}

    try:
        wb = load_workbook(filename, data_only=True)

        error_details = {err: [] for err in EXCEL_ERRORS}
        total_errors = 0

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            if not hasattr(ws, "iter_rows"):
                continue
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value is not None and isinstance(cell.value, str):
                        for err in EXCEL_ERRORS:
                            if err in cell.value:
                                location = f"{sheet_name}!{cell.coordinate}"
                                error_details[err].append(location)
                                total_errors += 1
                                break

        wb.close()

        out = {
            "status": "success" if total_errors == 0 else "errors_found",
            "total_errors": total_errors,
            "error_summary": {},
        }

        for err_type, locations in error_details.items():
            if locations:
                entry = {
                    "count": len(locations),
                    "locations": locations[:MAX_LOCATIONS],
                }
                if len(locations) > MAX_LOCATIONS:
                    entry["locations_truncated"] = len(locations) - MAX_LOCATIONS
                out["error_summary"][err_type] = entry

        wb_formulas = load_workbook(filename, data_only=False)
        formula_count = 0
        for sheet_name in wb_formulas.sheetnames:
            ws = wb_formulas[sheet_name]
            if not hasattr(ws, "iter_rows"):
                continue
            for row in ws.iter_rows():
                for cell in row:
                    if (
                        cell.value
                        and isinstance(cell.value, str)
                        and cell.value.startswith("=")
                    ):
                        formula_count += 1
        wb_formulas.close()

        out["total_formulas"] = formula_count

        return out

    except Exception as e:
        return {"error": str(e)}


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--force"]
    force = "--force" in sys.argv[1:]

    if not args:
        print("Usage: python3 recalc.py <excel_file> [timeout_seconds] [--force]")
        print("\nRecalculates all formulas in an Excel file using LibreOffice")
        print("\nReturns JSON with error details:")
        print("  - status: 'success' or 'errors_found'")
        print("  - total_errors: Total number of Excel errors found")
        print("  - total_formulas: Number of formulas in the file")
        print("  - error_summary: Breakdown by error type with up to 100 locations")
        print("    (locations_truncated counts any withheld cells)")
        print("\nAn 'error' key and no 'status' means nothing was recalculated.")
        print("--force recalculates even when it would destroy external links.")
        sys.exit(1)

    filename = args[0]
    timeout = int(args[1]) if len(args) > 1 else 30

    result = recalc(filename, timeout, force=force)
    print(json.dumps(result, indent=2))
    sys.exit(0 if "error" not in result and result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
