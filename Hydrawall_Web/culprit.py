import pandas as pd
import time

# Target the file Flask is watching
DATA_PATH = '/home/kali/Hydrawall_Web/system_data_cleaned.csv'

print("--- 🚨 HYDRAWALL-X ATTACK SIMULATOR ACTIVE ---")
print("Injecting malicious PIDs into the kernel stream...")

try:
    while True:
        # High PIDs that the Isolation Forest will flag as anomalies
        data = {'PID': [99999, 88888, 77777], 'PPID': [1, 1, 1]}
        df = pd.DataFrame(data)
        
        # Save to the CSV
        df.to_csv(DATA_PATH, index=False)
        print("Done: Injected PIDs 99999, 88888, 77777")
        
        # Wait for the AI to detect and the Flask app to 'kill' the data
        time.sleep(5)
except KeyboardInterrupt:
    print("\nSimulation Stopped.")
