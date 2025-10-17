# check_logs.py

"""
Check Cloud Run logs for import errors
"""

import subprocess
import sys

def check_logs():
    """Check Cloud Run logs"""
    
    print("Checking Cloud Run logs for import errors...")
    print("=" * 60)
    
    cmd = [
        "gcloud", "run", "services", "logs", "read",
        "validatus-backend",
        "--region=us-central1",
        "--project=validatus-platform",
        "--limit=50",
        "--format=value(textPayload,jsonPayload.message)"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logs = result.stdout
            
            # Look for import errors
            if "Data-Driven Results API" in logs:
                print("\n[FOUND] Data-Driven Results API logs:")
                for line in logs.split('\n'):
                    if "Data-Driven" in line or "import" in line.lower():
                        print(f"  {line}")
            
            # Look for errors
            if "error" in logs.lower() or "failed" in logs.lower():
                print("\n[FOUND] Error logs:")
                for line in logs.split('\n'):
                    if "error" in line.lower() or "failed" in line.lower():
                        print(f"  {line}")
            
            # Look for router registration
            if "registered" in logs.lower():
                print("\n[FOUND] Router registration logs:")
                for line in logs.split('\n'):
                    if "registered" in line.lower():
                        print(f"  {line}")
            
            print("\n[INFO] Full logs available via:")
            print("  gcloud run services logs read validatus-backend --region=us-central1 --project=validatus-platform")
            
        else:
            print(f"[ERROR] Failed to fetch logs: {result.stderr}")
            
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    check_logs()
