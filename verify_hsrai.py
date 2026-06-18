""" 
HSRAI (Hybrid Semantic Reasoning AI) Verification Test 
============================================================ 
Run this: python verify_hsrai.py 
""" 

import subprocess 
import sys 
from pathlib import Path 
import importlib

def find_hsrai(): 
    """Find HSRAI project root"""
    # If running from root, 'hsrai' package should be visible
    cwd = Path.cwd()
    if (cwd / 'hsrai').exists() and (cwd / 'hsrai' / '__init__.py').exists():
        return cwd
    
    # Check parent
    if (cwd.parent / 'hsrai').exists():
        return cwd.parent
        
    return None

def check_structure(project_dir): 
    """Check project structure""" 
    # Updated to match actual structure
    required = [
        'hsrai/', 
        'hsrai/tests/', 
        'hsrai/core/',
        'hsrai/reasoning/',
        'MARKET_ANALYSIS.md'
    ]
    found = [] 
    missing = [] 
    
    for item in required: 
        if (project_dir / item).exists(): 
            found.append(item) 
        else: 
            missing.append(item) 
    
    return found, missing 

def run_tests(project_dir): 
    """Run pytest on HSRAI tests""" 
    import os 
    os.chdir(project_dir) 
    
    # Added exclusions for web3 issues
    pytest_args = ['-v', '--tb=short', '-p', 'no:ethereum', '-p', 'no:web3', '-p', 'no:pytest_ethereum']
    test_target = 'hsrai/tests/' # Updated path
    
    cmds = [ 
        ['pytest', test_target] + pytest_args, 
        [sys.executable, '-m', 'pytest', test_target] + pytest_args, 
    ] 
    
    for cmd in cmds: 
        try: 
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60) 
            return result.returncode, result.stdout, result.stderr 
        except (FileNotFoundError, subprocess.TimeoutExpired) as e: 
            print(f"Command failed: {e}")
            continue 
    
    return -1, "", "Cannot run pytest" 

def quick_functionality_test(project_dir): 
    """Test if HSRAI can process a simple input""" 
    sys.path.insert(0, str(project_dir)) 
    
    try: 
        # Try to import core components 
        # Updated imports based on actual file structure
        from hsrai.compression.multimodal import MultiModalProcessor
        from hsrai.graph.builder import IntentGraphBuilder
        from hsrai.reasoning.hybrid_engine import HybridReasoningEngine
        
        print("Imports successful.")

        # Try basic compression 
        processor = MultiModalProcessor() 
        primitive = processor.process_text("Test input for HSRAI verification") 
        
        if primitive and primitive.concept == "Test input for HSRAI verification"[:50]: 
            return True, f"[OK] Compressed to primitive: {primitive.id}" 
        else: 
            return False, "[FAIL] Compression returned invalid result" 
            
    except ImportError as e: 
        return False, f"[FAIL] Cannot import HSRAI: {e}" 
    except Exception as e: 
        return False, f"[FAIL] Runtime error: {e}" 

def main(): 
    print("=" * 70) 
    print("HSRAI VERIFICATION TEST") 
    print("=" * 70) 
    
    # Find project 
    print("\n[1/4] Finding HSRAI...") 
    project_dir = find_hsrai() 
    
    if not project_dir: 
        print("[FAIL] HSRAI not found. Please run from project root.") 
        return 
    
    print(f"Found: {project_dir}") 
    
    # Check structure 
    print("\n[2/4] Checking structure...") 
    found, missing = check_structure(project_dir) 
    
    print(f"Found: {', '.join(found)}") 
    if missing: 
        print(f"Missing: {', '.join(missing)}") 
    
    # Run tests 
    print("\n[3/4] Running tests...") 
    print("-" * 70) 
    
    returncode, stdout, stderr = run_tests(project_dir) 
    
    if returncode != -1: 
        # print(stdout) 
        # Just print summary or last few lines if long?
        # The original script printed stdout. I'll keep it.
        print(stdout)
        
        if stderr and "warning" not in stderr.lower(): 
            print("STDERR:", stderr) 
        print("-" * 70) 
        
        if returncode == 0: 
            print("[OK] ALL TESTS PASSED") 
        else: 
            print(f"[FAIL] Tests failed (code {returncode})") 
    else: 
        print("[WARN]  Could not run tests") 
        print("-" * 70) 
    
    # Functionality test 
    print("\n[4/4] Testing functionality...") 
    ok, msg = quick_functionality_test(project_dir) 
    print(msg) 
    
    # Summary 
    print("\n" + "=" * 70) 
    print("SUMMARY") 
    print("=" * 70) 
    print(f"Project: {project_dir.name}") 
    print(f"Structure: {'Complete' if not missing else 'Incomplete'}") 
    print(f"Tests: {'PASS' if returncode == 0 else 'FAIL' if returncode != -1 else 'NOT RUN'}") 
    print(f"Functionality: {'PASS' if ok else 'FAIL'}") 
    
    if returncode == 0 and ok: 
        print("\n[SUCCESS] VERDICT: HSRAI IS WORKING") 
    else: 
        print("\n[FAIL] VERDICT: HSRAI HAS ISSUES") 
    
    print("=" * 70) 

if __name__ == "__main__": 
    main()
