"""Parse eslint v9 stylish output into structured EslintError list.

Stylish format (default for eslint v9):

    /path/to/file.vue
      LINE:COL  level  message  rule-name

    ✖ N problems (X errors, Y warnings)

Only entries with level=error are returned (warnings ignored for delta
computation purposes; rationale documented in ADR-018/019).
"""

import re

from rai_frontend_gates.models import EslintError

# File header: absolute or relative path ending in a file extension
_FILE_HEADER = re.compile(r"^(/?[\w./\-]+\.\w+)$")

# Error line: "  LINE:COL  level  message  rule-name"
# Captures: line, col, level (error|warning), message (greedy minus rule), rule
_ERROR_LINE = re.compile(
    r"^\s*(?P<line>\d+):(?P<col>\d+)\s+"
    r"(?P<level>error|warning)\s+"
    r"(?P<msg>.+?)\s+"
    r"(?P<rule>[\w/\-@]+)\s*$"
)


def parse_eslint_output(output: str) -> list[EslintError]:
    """Parse eslint stylish output → list of EslintError (errors only)."""
    errors: list[EslintError] = []
    current_file = ""

    for raw_line in output.splitlines():
        stripped = raw_line.rstrip()
        if not stripped:
            continue

        # File header (only if not indented and not starting with summary marker)
        if not raw_line.startswith(" ") and not stripped.startswith("✖"):
            match = _FILE_HEADER.match(stripped)
            if match:
                current_file = match.group(1)
                continue

        # Error line
        match = _ERROR_LINE.match(raw_line)
        if match and match.group("level") == "error" and current_file:
            errors.append(
                EslintError(
                    file=current_file,
                    line=int(match.group("line")),
                    column=int(match.group("col")),
                    rule=match.group("rule"),
                    message=match.group("msg").strip(),
                )
            )

    return errors
