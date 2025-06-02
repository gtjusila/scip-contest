import subprocess
import json
import sys
import os
from datetime import datetime
import uuid
from pyscipopt import Model, SCIP_PARAMSETTING, SCIP_RESULT


def run_script(script_name, timeout_sec, timeout_status, runtime_status):
    full_path = os.path.join("/mnt/user-code", script_name)
    if not os.path.isfile(full_path):
        print(f"[EVALUATE] {script_name} not found, skipping.")
        return {"status": "ScriptNotFound"}

    try:
        result = subprocess.run(
            ["bash", full_path],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        if result.returncode == 0:
            print(f"[EVALUATE] {script_name} finished successfully.")
            return {"status": "Success"}
        else:
            print(f"[EVALUATE] {script_name} failed with exit code {result.returncode}")
            print(result.stderr)
            return {
                "status": runtime_status,
                "exit_code": result.returncode,
                "stderr": result.stderr
            }
    except subprocess.TimeoutExpired:
        print(f"[EVALUATE] {script_name} timed out after {timeout_sec} seconds.")
        return {"status": timeout_status}

def evaluate_model(testcase_path):
    """
    Evaluate a testcase using PySCIPOpt.

    Arguments:
    - testcase_path: full path to the testcase file in /data/testcases

    Returns:
    - A dictionary with SCIP results
    """

    # Load SCIP model
    model = Model()
    model.readProblem(testcase_path)
    print(f"[EVALUATE] Loaded testcase: {testcase_path}")

    # Check for parameter.set
    param_file = os.path.join("/mnt/user-code", "parameter.set")
    if not os.path.isfile(param_file):
        raise FileNotFoundError("parameter.set not found in /mnt/user-code")

    # Load user parameters
    model.readParams(param_file)
    print(f"[EVALUATE] Loaded user parameters from: {param_file}")

    # Set time limit to 2 hours (7200 seconds)
    model.setRealParam("limits/time", 7200)

    # Solve the model
    model.optimize()

    # Extract results
    status = model.getStatus()
    gap = model.getGap() * 100  # Convert to percentage
    solve_time = model.getSolvingTime()

    print(f"[EVALUATE] SCIP Status: {status}")
    print(f"[EVALUATE] Final Gap Closed: {gap:.2f}%")
    print(f"[EVALUATE] Solve Time: {solve_time:.2f} seconds")

    return {
        "termination_status": str(status),
        "gap_closed": gap,
        "solve_time": solve_time
    }

def write_result(result):
    unique_id = uuid.uuid4().hex
    output_file = f"evaluation_result_{unique_id}.json"
    output_path = os.path.join("/mnt/result", output_file)

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[EVALUATE] Result written to {output_path}")
    
def main():
    try:
        # Validate input
        if len(sys.argv) != 2:
            raise ValueError("Usage: evaluate <testcase_filename>")

        testcase = sys.argv[1]
        testcase_path = os.path.join("/data/testcases", testcase)

        if not os.path.isfile(testcase_path):
            raise ValueError(f"Testcase not found: {testcase_path}")

        # Run initialize.sh (if exists)
        init_result = run_script(
            "initialize.sh",
            timeout_sec=3600,
            timeout_status="FailToInitialize",
            runtime_status="RuntimeError"
        )
        if init_result["status"] not in ["Success", "ScriptNotFound"]:
            write_result(init_result)
            return

        # Run train.sh
        train_result = run_script(
            "train.sh",
            timeout_sec=21600,
            timeout_status="TrainTimeLimitExceeded",
            runtime_status="RuntimeError"
        )
        if train_result["status"] != "Success":
            write_result(train_result)
            return

        # Final evaluation
        metrics = evaluate_model(testcase_path)
        result = {
            "status": "Success",
            "testcase": testcase,
            **metrics
        }
        write_result(result)

    except ValueError as ve:
        # Print usage errors, do NOT write result file
        print(f"[EVALUATE] {ve}")

    except Exception as e:
        # Other unexpected errors: write result
        result = {
            "status": "EvaluationError",
            "error_message": str(e)
        }
        write_result(result)
if __name__ == "__main__":
    main()
