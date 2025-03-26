import builtins
import contextlib
import io
import sys
from typing import Any, Dict, Set
from types import ModuleType

class SandboxError(Exception):
    """Custom exception for sandbox-related errors."""
    pass

# List of allowed built-in functions
ALLOWED_BUILTINS = {
    'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set',
    'tuple', 'range', 'enumerate', 'zip', 'min', 'max', 'sum', 'abs',
    'round', 'pow', 'divmod', 'bin', 'hex', 'oct', 'chr', 'ord'
}

# List of restricted modules
RESTRICTED_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'threading', 'multiprocessing',
    'ctypes', 'platform', 'importlib', 'imp', 'marshal', 'pickle',
    'json', 'yaml', 'xml', 'sqlite3', 'sqlalchemy', 'requests'
}

def create_safe_builtins() -> Dict[str, Any]:
    """Create a safe dictionary of built-in functions."""
    safe_builtins = {}
    for name, func in builtins.__dict__.items():
        if name in ALLOWED_BUILTINS:
            safe_builtins[name] = func
    return safe_builtins

def create_safe_globals() -> Dict[str, Any]:
    """Create a safe global namespace."""
    safe_builtins_dict = create_safe_builtins()
    safe_globals = safe_builtins_dict.copy()
    safe_globals['__builtins__'] = safe_builtins_dict
    return safe_globals

def is_safe_import(name: str) -> bool:
    """Check if a module import is safe."""
    return not any(name.startswith(restricted) for restricted in RESTRICTED_MODULES)

class RestrictedImporter:
    """Custom import hook to restrict module imports."""
    def __init__(self):
        self.original_import = builtins.__import__

    def __call__(self, name: str, globals: Dict[str, Any] = None, locals: Dict[str, Any] = None,
                 fromlist: list = None, level: int = 0) -> ModuleType:
        if not is_safe_import(name):
            raise SandboxError(f"Import of module '{name}' is not allowed in sandbox")
        return self.original_import(name, globals, locals, fromlist, level)

def eval_in_sandbox(code: str, _locals: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """
    Execute code in a sandboxed environment.
    
    Args:
        code: The code string to execute
        _locals: Dictionary of local variables
        
    Returns:
        Tuple of (output string, new variables created)
    """
    # Store original keys before execution
    original_keys = set(_locals.keys())
    
    # Create safe globals
    safe_globals = create_safe_globals()
    
    # Set up restricted import hook
    original_import = builtins.__import__
    builtins.__import__ = RestrictedImporter()
    
    try:
        # Capture stdout
        with contextlib.redirect_stdout(io.StringIO()) as f:
            # Execute code in sandbox
            exec(code, safe_globals, _locals)
        result = f.getvalue()
        if not result:
            result = "<code ran, no output printed to stdout>"
            
    except Exception as e:
        result = f"Error during execution: {repr(e)}"
        
    finally:
        # Restore original import
        builtins.__import__ = original_import
    
    # Determine new variables created during execution
    new_keys = set(_locals.keys()) - original_keys
    new_vars = {key: _locals[key] for key in new_keys}
    
    return result, new_vars 