import pandas as pd
import numpy as np
from pathlib import Path

LOG_FILE = Path("logs/api_log.csv")

def analyze():
    if not LOG_FILE.exists():
        print(f"Error: {LOG_FILE} not found!")
        return

    df = pd.read_csv(LOG_FILE)
    
    # گروه‌بندی و محاسبات
    summary = df.groupby('task').agg({
        'prompt_tokens': 'mean',
        'completion_tokens': 'mean',
        'latency_s': ['mean', lambda x: np.percentile(x, 95)],
        'cost_toman': 'sum'
    })

    summary.columns = [
        'Avg Prompt', 'Avg Completion', 
        'Avg Latency (s)', 'P95 Latency (s)', 'Total Cost (Toman)'
    ]

    print("\n--- Project Analysis Report (Day 5) ---")
    print(summary.round(3).to_string())
    
    print("\n" + "="*50)
    print(f"Total Experiment Cost: {df['cost_toman'].sum():.2f} Toman")
    print("="*50)

if __name__ == "__main__":
    analyze()