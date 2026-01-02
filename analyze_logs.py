import json
import sys

def analyze_logs(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            # Try parsing as a list of objects
            logs = json.loads(content)
        except json.JSONDecodeError:
            # Maybe it's one JSON object per line, but we know it's 1 line. 
            # Or maybe it is a list but truncated in my view.
            # Let's assume it is a valid JSON array or object.
            print("Error parsing JSON. Content might be malformed.")
            return

        if isinstance(logs, list):
            for entry in logs:
                process_entry(entry)
        elif isinstance(logs, dict):
            process_entry(logs)
            
    except Exception as e:
        print(f"Error reading file: {e}")

def process_entry(entry):
    # Adjust based on actual log structure seen in previous turn
    # {"message":"...", "attributes":{"level":"info"}, ...}
    msg = entry.get('message', '')
    level = entry.get('attributes', {}).get('level', '')
    
    if isinstance(msg, str):
        msg_lower = msg.lower()
        if 'error' in msg_lower or 'fail' in msg_lower or 'exception' in msg_lower or 'traceback' in msg_lower or level.lower() == 'error':
            print(f"[{level.upper()}] {msg}")

if __name__ == "__main__":
    analyze_logs('deploy_logs.1765545637684.json')
