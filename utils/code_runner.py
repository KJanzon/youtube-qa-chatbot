# utils/code_runner.py
import contextlib
import io
import traceback

@contextlib.contextmanager
def capture_output():
    """Capture stdout and stderr during code execution."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        yield stdout, stderr

def run_user_code(code: str) -> str:
    """Execute user-provided Python code and return combined stdout/stderr."""
    output = ""
    try:
        with capture_output() as (out, err):
            exec(code, {})  # ⚠️ don't use eval; exec allows multiple lines
        output = out.getvalue() + err.getvalue()
    except Exception:
        output += traceback.format_exc()
    return output.strip()
