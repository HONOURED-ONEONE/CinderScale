# RCA-Copilot Acceleration Boundary

This directory defines the **Acceleration Boundary** for the RCA Python Analytical Engine.

## Architecture

The engine delegates its most CPU-bound tasks (Hotspots) to a kernel implementation following the `RCAKernels` abstract interface defined in `base.py`.

### Identified Hotspots
1. **Topology Inference**: Intensive log scanning for hints (regex/string matching).
2. **Telemetry Normalization**: Processing high-volume raw telemetry into a unified schema.
3. **Signal Scoring**: Anomaly extraction over large event sets.

## Kernel Factory

The factory in `rca/kernels/__init__.py` chooses the implementation based on the `RCA_ACCELERATOR` environment variable.

- `RCA_ACCELERATOR=python` (Default): Uses `PythonRCAKernels` in `python_impl.py`.
- `RCA_ACCELERATOR=mojo` (Future): Should load an optimized Mojo-based implementation.

## Implementing a New Kernel

To add an accelerated implementation (e.g., for Mojo):
1. Implement the `RCAKernels` interface in a new module (e.g., `rca/kernels/mojo_impl.py`).
2. Your implementation should wrap the native/low-level calls.
3. Add the logic to load your module in `rca/kernels/__init__.py`.
4. Run tests to ensure interface stability.

```python
# Example switch logic in __init__.py
if accel == "mojo":
    from rca.kernels.mojo_impl import MojoRCAKernels
    return MojoRCAKernels()
```
