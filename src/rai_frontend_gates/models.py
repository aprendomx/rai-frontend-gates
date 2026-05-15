"""Pydantic contracts for rai-frontend-gates.

Mirrors rai-cli GateResult/GateContext shapes for UX consistency
(bridge pattern, no direct rai-cli import — see ADR-018/019).
"""

from pydantic import BaseModel


class EslintError(BaseModel):
    """Single eslint error/warning entry parsed from stylish output."""

    file: str
    line: int
    column: int = 0
    rule: str
    message: str


class GateResult(BaseModel):
    """Result returned by GateRunner.check_gate().

    Compatible with rai-cli GateResult shape; emit-side only.
    """

    passed: bool
    gate_id: str
    message: str
    details: list[str] = []
    exit_code: int
    raw_output: str = ""


class GateContext(BaseModel):
    """Context passed to GateRunner.check_gate()."""

    gate_id: str
    working_dir: str
    extra_args: list[str] = []
    delta_mode: bool = False
