from dataclasses import dataclass

from flask import Blueprint, render_template, request

stacks_bp = Blueprint("stacks", __name__)

OPENING_TO_CLOSING = {
    "(": ")",
    "[": "]",
    "{": "}",
    "<": ">",
    "¿": "?",
    "¡": "!",
    "“": "”",
    "‘": "’",
}
CLOSING_TO_OPENING = {closing: opening for opening, closing in OPENING_TO_CLOSING.items()}
STRAIGHT_QUOTES = {'"', "'"}


@dataclass(frozen=True)
class StackStep:
    """One snapshot of the stack after a relevant character is processed."""

    position: int | str
    symbol: str
    action: str
    stack: tuple[str, ...]


@dataclass(frozen=True)
class ValidationResult:
    """The result of validating a text expression with a stack."""

    is_valid: bool
    steps: list[StackStep]
    message: str


def validate_symbols(text: str) -> ValidationResult:
    """Validate matching symbols by pushing openings and popping matching closings."""
    stack: list[str] = []
    steps: list[StackStep] = []

    def add_step(position: int | str, symbol: str, action: str) -> None:
        steps.append(StackStep(position, symbol, action, tuple(stack)))

    for position, symbol in enumerate(text, start=1):
        if symbol in OPENING_TO_CLOSING:
            stack.append(symbol)
            add_step(position, symbol, f"Push opening symbol '{symbol}'")
            continue

        if symbol in STRAIGHT_QUOTES:
            if stack and stack[-1] == symbol:
                stack.pop()
                add_step(position, symbol, f"Pop quote '{symbol}'")
            else:
                stack.append(symbol)
                add_step(position, symbol, f"Push quote '{symbol}'")
            continue

        if symbol not in CLOSING_TO_OPENING:
            continue

        expected_opening = CLOSING_TO_OPENING[symbol]
        if not stack:
            add_step(position, symbol, f"Error: missing opening '{expected_opening}'")
            return ValidationResult(
                False,
                steps,
                f"Position {position}: '{symbol}' does not have a previous opening symbol.",
            )

        if stack[-1] != expected_opening:
            top_symbol = stack[-1]
            add_step(position, symbol, f"Error: stack top is '{top_symbol}'")
            return ValidationResult(
                False,
                steps,
                f"Position {position}: '{symbol}' does not match '{top_symbol}' at the top of the stack.",
            )

        stack.pop()
        add_step(position, symbol, f"Pop opening symbol '{expected_opening}'")

    if stack:
        pending_symbol = stack[-1]
        add_step("End", "—", f"Error: '{pending_symbol}' remains open")
        return ValidationResult(
            False,
            steps,
            f"The input ended with {len(stack)} opening symbol(s) still in the stack.",
        )

    return ValidationResult(True, steps, "The stack is empty after processing the input.")


@stacks_bp.route("/", methods=["GET", "POST"])
def stacks_page():
    """Render and process the stacks module."""
    text = request.form.get("text", "")
    result = validate_symbols(text) if request.method == "POST" else None
    return render_template("stacks/index.html", text=text, result=result)
