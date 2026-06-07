import os
import json
import requests

BASE_URL = "http://localhost:20128/v1"
API_KEY = "sk-1ee05867913c0a66-ezh2p2-dc5b44f0"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def parse_stream_response(response_text):
    content = ""
    lines = response_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('data: '):
            data_str = line[6:].strip()
            if data_str == '[DONE]':
                break
            try:
                data = json.loads(data_str)
                choices = data.get('choices', [])
                if choices:
                    delta = choices[0].get('delta', {})
                    if 'content' in delta:
                        content += delta['content']
                    elif 'message' in delta:
                        content += delta['message'].get('content', '')
            except Exception:
                pass
    return content

def analyze():
    # 1. Load config and geometry files
    with open("config.json", "r") as f:
        config_data = json.load(f)
    with open("geometry.json", "r") as f:
        geom_data = json.load(f)

    # Prepare a highly concise summary of inputs to minimize token usage
    summary_data = {
        "n_rotors": config_data.get("n_rotors"),
        "layout": config_data.get("layout"),
        "drive_type": config_data.get("drive_type"),
        "mtow_kg": config_data.get("debug", {}).get("mtow_kg"),
        "payload_kg": config_data.get("debug", {}).get("payload_kg"),
        "wheelbase_m": geom_data.get("wheelbase_m"),
        "D_rotor_m": geom_data.get("D_rotor_m"),
        "DL_actual_Nm2": geom_data.get("DL_actual_Nm2"),
        "FM_actual": geom_data.get("FM_actual"),
    }

    prompt = f"""You are a senior aerospace engineer. Analyze the following multicopter configuration and provide a brief, professional engineering critique (3-4 bullet points maximum, extremely concise in Turkish):
Configuration: {json.dumps(summary_data, indent=2)}
"""

    payload = {
        "model": "orchestra-coder",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 400
    }

    print("Sending prompt to orchestra-coder via 9Router...")
    try:
        r = requests.post(f"{BASE_URL}/chat/completions", headers=HEADERS, json=payload, timeout=60)
        print(f"Response Status Code: {r.status_code}")
        
        # Check if the response is JSON or event-stream
        content_type = r.headers.get("Content-Type", "")
        if "text/event-stream" in content_type or r.text.strip().startswith("data:"):
            analysis = parse_stream_response(r.text)
        else:
            try:
                resp = r.json()
                analysis = resp["choices"][0]["message"]["content"]
            except Exception:
                analysis = r.text
        
        print("\n=== Engineering Analysis from orchestra-coder ===")
        print(analysis)
        
        # Save the analysis to reports/analysis_summary.txt
        os.makedirs("reports", exist_ok=True)
        with open("reports/analysis_summary.txt", "w", encoding="utf-8") as out:
            out.write(analysis)
        print("\nAnalysis saved to reports/analysis_summary.txt")
        
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    analyze()
