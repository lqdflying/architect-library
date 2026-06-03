#!/usr/bin/env python3
"""Unified CLI for office-tools.

Usage:
    python3 office_tools.py unpack document.docx unpacked/
    python3 office_tools.py pack unpacked/ output.docx --original input.docx
    python3 office_tools.py validate unpacked/ --auto-repair
    python3 office_tools.py extract document.docx
    python3 office_tools.py comment unpacked/ 0 "Comment text"
    python3 office_tools.py accept input.docx output.docx
    python3 office_tools.py verify unpacked/ original.docx
    python3 office_tools.py slide unpacked/ slide2.xml
    python3 office_tools.py clean unpacked/
    python3 office_tools.py thumbnail presentation.pptx /tmp/preview --per-slide /tmp/slides --dpi 150
"""

import sys


COMMANDS = {
    "unpack":    ("unpack.py",             "Unpack Office file for editing"),
    "pack":      ("pack.py",               "Pack directory into Office file"),
    "validate":  ("validate.py",           "Validate Office document XML"),
    "extract":   ("extract_text.py",       "Extract text from DOCX/PPTX"),
    "comment":   ("add_comment.py",        "Add comment to unpacked DOCX"),
    "accept":    ("accept_changes.py",     "Accept all tracked changes"),
    "verify":    ("verify_redlines.py",    "Verify tracked changes correctness"),
    "slide":     ("add_slide.py",          "Add/duplicate PPTX slide"),
    "clean":     ("clean_pptx.py",         "Remove orphaned PPTX files"),
    "thumbnail": ("thumbnail.py",          "PPTX layout preview: grid and/or per-slide JPEGs"),
    "analyze":   ("analyze_template.py",   "Analyze PPTX template structure"),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print("office-tools - DOCX/PPTX manipulation toolkit\n")
        print("Usage: python3 office_tools.py <command> [args...]\n")
        print("Commands:")
        for cmd, (_, desc) in COMMANDS.items():
            print(f"  {cmd:12s} {desc}")
        print(f"\nRun 'python3 office_tools.py <command> --help' for command-specific help.")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    # Remove the command name from argv so the sub-script sees clean args
    sys.argv = [COMMANDS[cmd][0]] + sys.argv[2:]

    # Import and run the sub-script's __main__ block
    script = COMMANDS[cmd][0].replace(".py", "")
    module = __import__(script)

    # Most scripts use if __name__ == "__main__" with argparse
    # We need to call their main logic directly
    if hasattr(module, "main"):
        module.main()
    else:
        # For scripts that put logic in __main__ block,
        # re-run them by exec
        import runpy
        runpy.run_module(script, run_name="__main__")


if __name__ == "__main__":
    main()
