---
name: Add uv run logger_app command
overview: Add a console script entry point in pyproject.toml to enable `uv run logger_app` command, and create a wrapper function in logger_app.py to handle the entry point.
todos: []
---

# Add uv run logger_app Command

## Overview

Add a `[project.scripts]` entry point in `pyproject.toml` to enable running the app with `uv run logger_app` instead of `uv run python logger_app.py`.

## Changes Required

### 1. Update `pyproject.toml`

Add a `[project.scripts]` section with an entry point that points to a console script function in `logger_app.py`:

```toml
[project.scripts]
logger_app = "logger_app:console_main"
```

### 2. Update `logger_app.py`

Create a new `console_main()` function that:

- Handles argument parsing (moves the existing module-level parsing into the function)
- Gets the default xdf_folder
- Calls the existing `main()` function with appropriate parameters

This function will serve as the entry point for the console script. The existing `if __name__ == "__main__"` block can be updated to call `console_main()` to maintain backward compatibility.

### 3. Optional: Update `run_logger.bat`

The batch file can be simplified to use `uv run logger_app` instead of `uv run python logger_app.py`, though this is optional since the current approach also works.

## Implementation Details

- The `console_main()` function will encapsulate the argument parsing logic that's currently at module level
- The entry point format `logger_app:console_main` means it will call the `console_main` function from the `logger_app` module (the root `logger_app.py` file)
- After adding the script entry point, users will need to run `uv sync` to install the script, then `uv run logger_app` will work