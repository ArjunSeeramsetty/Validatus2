# test_imports.py

"""
Test if the data-driven imports work
"""

import sys
sys.path.insert(0, 'backend')

try:
    from app.api.v3.test_router import router as test_router
    print("SUCCESS: test_router imported successfully")
    print(f"Router type: {type(test_router)}")
    print(f"Router routes: {test_router.routes}")
except Exception as e:
    print(f"FAILED: test_router import failed: {e}")

try:
    from app.api.v3.data_driven_results_simple import router as dd_router
    print("SUCCESS: data_driven_results_simple imported successfully")
    print(f"Router type: {type(dd_router)}")
    print(f"Router routes: {dd_router.routes}")
except Exception as e:
    print(f"FAILED: data_driven_results_simple import failed: {e}")
