import os
import sys
import json
import subprocess
import datetime

REPO_DIR = r"E:\000 ALPAY Teknoloji\Teknoloji\Skills\MultiCopter_Code\Multicopter"
GIT_EXE = r"C:\Users\Administrator\AppData\Local\GitHubDesktop\app-3.5.11\resources\app\git\cmd\git.exe"

def run_git(args, env=None):
    if env is None:
        env = os.environ.copy()
    env['GIT_SSH'] = r"C:\Windows\System32\OpenSSH\ssh.exe"
    r = subprocess.run([GIT_EXE] + args, cwd=REPO_DIR, env=env, capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip(), r.stderr.strip()

def main():
    print("=== Antigravity 30-Minute Status Report & Sync ===")
    
    # 1. Fetch and Pull
    print("Pulling latest main branch...")
    # Check current latest commit hash
    _, before_hash, _ = run_git(["rev-parse", "HEAD"])
    
    success, stdout, stderr = run_git(["pull", "origin", "main"])
    if not success:
        print(f"Failed to pull repository: {stderr}")
        sys.exit(1)
        
    _, after_hash, _ = run_git(["rev-parse", "HEAD"])
    
    new_commits_pulled = (before_hash != after_hash)
    if new_commits_pulled:
        print("New commits pulled from GitHub.")
    else:
        print("No new commits from remote.")

    # 2. Read current state
    state_path = os.path.join(REPO_DIR, "ORCHESTRA_STATE.json")
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {"system_status": "UNKNOWN", "next_agent": None}

    # 3. Compile Heartbeat Report
    log_path = os.path.join(REPO_DIR, "ORCHESTRA_LOG.md")
    if not os.path.exists(log_path):
        print("ORCHESTRA_LOG.md not found.")
        sys.exit(1)
        
    with open(log_path, "r", encoding="utf-8") as f:
        log_content = f.read()
        
    # Find the header section
    header_end = log_content.find("---")
    if header_end == -1:
        header = "# 📜 Orkestra İletişim Günlüğü (Orchestra Log)\n\n"
        body = log_content
    else:
        header = log_content[:header_end + 3]
        body = log_content[header_end + 3:]
        
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if new_commits_pulled:
        findings = "- Uzak depoda yeni değişiklikler algılandı ve yerel depoya çekildi.\n- Güncel Durum: " + state.get("system_status", "UNKNOWN") + " | Sıradaki Ajan: " + str(state.get("next_agent"))
    else:
        findings = "- Uzak depo kontrol edildi. İnternet Qwen ajanı tarafından yeni bir değişiklik veya görev tetiklenmedi.\n- Sistem durum raporları ile kararlı şekilde beklemede (IDLE)."

    heartbeat_entry = f"""

## [{timestamp_str}] - ANTIGRAVITY (Senkronizasyon & Durum Raporu)
**Durum:** BEKLEMEDE (IDLE)
**Açıklama:**
{findings}

**Sonraki Eylem:**
- İnternet üzerindeki Qwen Coder veya kullanıcıdan yeni görev/branch ataması bekleniyor.

---"""

    updated_log = header + heartbeat_entry + body
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(updated_log)
        
    # 4. Commit and Push
    print("Committing and pushing status report...")
    run_git(["add", "ORCHESTRA_LOG.md"])
    run_git(["commit", "-m", f"chore(sync): periodic status report and heartbeat {timestamp_str}"])
    
    success, stdout, stderr = run_git(["push"])
    if success:
        print("Status report successfully pushed to GitHub.")
    else:
        print(f"Failed to push status report: {stderr}")

if __name__ == "__main__":
    main()
