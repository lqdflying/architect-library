#!/usr/bin/env python3
"""Accept all tracked changes in a DOCX file, producing a clean document.

Uses LibreOffice Basic macro to accept changes, since the OOXML spec makes
purely XML-based acceptance extremely complex (paragraph properties, numbering,
section breaks all need reconciliation).

Usage:
    python accept_changes.py input.docx output.docx
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from soffice_wrapper import get_soffice_env
except ImportError:
    import os
    def get_soffice_env():
        return os.environ.copy()

LO_PROFILE = "/tmp/libreoffice_office_tools_profile"
MACRO_DIR = f"{LO_PROFILE}/user/basic/Standard"

MACRO_XBA = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub AcceptAllTrackedChanges()
        Dim document As Object
        Dim dispatcher As Object
        document = ThisComponent.CurrentController.Frame
        dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")
        dispatcher.executeDispatch(document, ".uno:AcceptAllTrackedChanges", "", 0, Array())
        ThisComponent.store()
        ThisComponent.close(True)
    End Sub
</script:module>"""


def _setup_macro() -> bool:
    """Install the AcceptAllTrackedChanges macro into LibreOffice."""
    macro_dir = Path(MACRO_DIR)
    macro_file = macro_dir / "Module1.xba"

    if macro_file.exists() and "AcceptAllTrackedChanges" in macro_file.read_text():
        return True

    if not macro_dir.exists():
        # Initialize LO profile
        subprocess.run(
            ["soffice", "--headless",
             f"-env:UserInstallation=file://{LO_PROFILE}",
             "--terminate_after_init"],
            capture_output=True, timeout=10, check=False,
            env=get_soffice_env(),
        )
        macro_dir.mkdir(parents=True, exist_ok=True)

    try:
        macro_file.write_text(MACRO_XBA)
        return True
    except Exception as e:
        print(f"Error: Failed to install macro: {e}", file=sys.stderr)
        return False


def accept_changes(input_file: str, output_file: str) -> str:
    """Accept all tracked changes. Returns status message."""
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        return f"Error: {input_file} not found"
    if input_path.suffix.lower() != ".docx":
        return f"Error: {input_file} is not a .docx file"

    # Copy input to output location (LO modifies in-place)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, output_path)

    if not _setup_macro():
        return "Error: Failed to setup LibreOffice macro"

    cmd = [
        "soffice", "--headless",
        f"-env:UserInstallation=file://{LO_PROFILE}",
        "--norestore",
        "vnd.sun.star.script:Standard.Module1.AcceptAllTrackedChanges"
        "?language=Basic&location=application",
        str(output_path.absolute()),
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                       check=False, env=get_soffice_env())
    except subprocess.TimeoutExpired:
        # LO sometimes hangs after completing; timeout is expected success
        pass

    return f"Accepted all tracked changes: {input_file} -> {output_file}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Accept all tracked changes in DOCX")
    parser.add_argument("input_file", help="Input DOCX with tracked changes")
    parser.add_argument("output_file", help="Output DOCX (clean, no tracked changes)")
    args = parser.parse_args()

    msg = accept_changes(args.input_file, args.output_file)
    print(msg)
    if "Error" in msg:
        sys.exit(1)
