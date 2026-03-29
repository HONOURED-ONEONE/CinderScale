import os
import importlib
from rca.kernels.base import RCAKernels
from rca.kernels.python_impl import PythonRCAKernels

def get_kernels() -> RCAKernels:
    """
    Kernel Factory: Returns the best available RCA kernel implementation.
    Supports switching via RCA_ACCELERATOR environment variable.
    """
    accel = os.environ.get("RCA_ACCELERATOR", "python").lower()
    
    if accel == "python":
        return PythonRCAKernels()
    
    # Example: Mojo or native kernels could be loaded here
    # try:
    #     if accel == "mojo":
    #         module = importlib.import_module("rca.kernels.mojo_impl")
    #         return module.MojoRCAKernels()
    # except ImportError:
    #     print("Requested accelerator not found, falling back to python.")
        
    return PythonRCAKernels()
