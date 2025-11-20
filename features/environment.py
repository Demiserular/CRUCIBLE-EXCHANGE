"""
Behave environment setup and teardown hooks.

Manages the exchange server lifecycle for test execution.
"""

import subprocess
import time
import socket
import sys
import os
import signal
from pathlib import Path


def before_all(context):
    """
    Set up test environment before all scenarios.
    Start the exchange server.
    """
    print("\n" + "="*60)
    print("Starting FIX Exchange Server for testing...")
    print("="*60 + "\n")
    
    # Get path to exchange server
    project_root = Path(__file__).parent.parent.parent
    server_script = project_root / "src" / "exchange_server.py"
    
    # Start server as subprocess
    context.server_process = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(project_root),
        bufsize=0
    )
    
    # Wait for server to be ready
    max_attempts = 20
    for attempt in range(max_attempts):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            test_socket.connect(("127.0.0.1", 9878))
            test_socket.close()
            print("✓ Exchange server is ready\n")
            break
        except Exception:
            if attempt == max_attempts - 1:
                print("✗ Exchange server failed to start")
                context.server_process.terminate()
                raise Exception("Exchange server did not start within timeout")
            time.sleep(0.5)
    
    # Store server info
    context.server_pid = context.server_process.pid
    context.failed_scenarios = []
    context.passed_scenarios = []
    
    # Check if server actually started
    if context.server_process.poll() is not None:
        output, _ = context.server_process.communicate()
        print(f"Server failed to start. Output: {output.decode() if output else 'None'}")
        raise Exception("Exchange server failed to start")


def after_all(context):
    """
    Clean up test environment after all scenarios.
    Stop the exchange server.
    """
    print("\n" + "="*60)
    print("Stopping FIX Exchange Server...")
    print("="*60 + "\n")
    
    # Terminate server process
    if hasattr(context, 'server_process'):
        try:
            context.server_process.terminate()
            context.server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            context.server_process.kill()
            context.server_process.wait()
        
        print("✓ Exchange server stopped\n")
    
    # Print test summary
    print("="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    print(f"Passed: {len(context.passed_scenarios)}")
    print(f"Failed: {len(context.failed_scenarios)}")
    
    if context.failed_scenarios:
        print("\nFailed Scenarios:")
        for scenario in context.failed_scenarios:
            print(f"  ✗ {scenario}")
    
    print("="*60 + "\n")


def before_scenario(context, scenario):
    """
    Set up before each scenario.
    """
    print(f"\n▶ Running: {scenario.name}")
    context.scenario_name = scenario.name


def after_scenario(context, scenario):
    """
    Clean up after each scenario.
    Close any open connections.
    """
    # Close client socket if open
    if hasattr(context, 'client_socket'):
        try:
            context.client_socket.close()
        except Exception:
            pass
        delattr(context, 'client_socket')
    
    # Track scenario results
    if scenario.status == "failed":
        context.failed_scenarios.append(scenario.name)
        print(f"  ✗ FAILED: {scenario.name}")
    else:
        context.passed_scenarios.append(scenario.name)
        print(f"  ✓ PASSED: {scenario.name}")


def before_step(context, step):
    """Execute before each step."""
    pass


def after_step(context, step):
    """Execute after each step."""
    if step.status == "failed":
        print(f"    ✗ Step failed: {step.name}")
        if step.error_message:
            print(f"      Error: {step.error_message}")
