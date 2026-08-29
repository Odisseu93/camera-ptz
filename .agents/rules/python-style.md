# Python Style & Best Practices

- Standard: Follow PEP 8 with Black formatting (88 chars/line) and isort import order.
- Features: Use Python 3.11+ syntax (`from __future__ import annotations`, modern type unions `int | None`).
- Type Hints: Type all public function parameters and returns. Use `typing.TypedDict` or `@dataclass(frozen=True)` for structured data.
- Error Handling: Handle specific exceptions (e.g. `requests.Timeout`, `cv2.error`). Never use bare `except:`.
- Logging: Use standard `logging.getLogger(__name__)`. Output structured info for server actions.
- Anti-Slop: Write clean, self-explanatory code without trivial comments or boilerplate.
