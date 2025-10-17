"""Run all tests in the tests folder"""
import asyncio
import sys
import os
from pathlib import Path

# IMPORTANT: Set working directory to project root before importing
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)

# Add parent directory to path
sys.path.insert(0, project_root)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

async def run_test_module(module_name: str, test_function: str = "main"):
    """Run a test module and return success status"""
    try:
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Running: {module_name}{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        # Import the module dynamically
        if module_name.startswith('tests.'):
            module = __import__(module_name, fromlist=[test_function])
        else:
            module = __import__(f'tests.{module_name}', fromlist=[test_function])
        
        # Get the test function
        if hasattr(module, test_function):
            test_func = getattr(module, test_function)
            
            # Run the test
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            # Check result
            if result is None:
                # Assume success if no return value
                return True
            elif isinstance(result, bool):
                return result
            else:
                return True
        else:
            print(f"{Colors.RED}❌ Test function '{test_function}' not found in {module_name}{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error running {module_name}: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return False

def run_sync_test(module_name: str):
    """Run a synchronous test module"""
    try:
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Running: {module_name}{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        # Import and run
        if module_name.startswith('tests.'):
            module = __import__(module_name, fromlist=['main'])
        else:
            module = __import__(f'tests.{module_name}', fromlist=['main'])
        
        if hasattr(module, 'test_profanity_detection'):
            result = module.test_profanity_detection()
            return result
        elif hasattr(module, 'main'):
            result = module.main()
            return result if result is not None else True
        else:
            return True
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error running {module_name}: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Astrology Bot - Complete Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Working directory: {os.getcwd()}{Colors.END}")
    print(f"{Colors.YELLOW}.env file exists: {os.path.exists('.env')}{Colors.END}\n")
    
    # Define all tests to run
    async_tests = [
        'test_connections',
        'test_rabbitmq',
        'test_mem0_connection',
    ]
    
    sync_tests = [
        'test_profanity_filter',
    ]
    
    results = {}
    
    # Run async tests
    for test_name in async_tests:
        try:
            success = await run_test_module(test_name)
            results[test_name] = success
        except Exception as e:
            print(f"{Colors.RED}Failed to run {test_name}: {e}{Colors.END}")
            results[test_name] = False
    
    # Run sync tests
    for test_name in sync_tests:
        try:
            success = run_sync_test(test_name)
            results[test_name] = success
        except Exception as e:
            print(f"{Colors.RED}Failed to run {test_name}: {e}{Colors.END}")
            results[test_name] = False
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    total = len(results)
    
    for test_name, success in results.items():
        icon = f"{Colors.GREEN}✅{Colors.END}" if success else f"{Colors.RED}❌{Colors.END}"
        status = f"{Colors.GREEN}PASSED{Colors.END}" if success else f"{Colors.RED}FAILED{Colors.END}"
        print(f"{icon} {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Your bot is ready to deploy.{Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  {failed} test(s) failed. Please fix the issues above.{Colors.END}\n")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)