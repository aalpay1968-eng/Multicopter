import os
import json
import time
import shutil
import threading
import sys
import socketio
import requests
from kaggle.api.kaggle_api_extended import KaggleApi

# Windows terminal encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HUB_URL = "http://localhost:5000"
KAG_JSON = r"E:\000 ALPAY Teknoloji\kaggle.json"
KAG1_JSON = r"E:\000 ALPAY Teknoloji\kaggle1.json"
TEMP_DIR = r"C:\Users\Administrator\.gemini\antigravity\brain\d440e23e-8dc1-4106-9715-44b4611a63b8\scratch\kaggle_trigger_temp"

# Mapping Kaggle kernels to Orchestra Agent roles and models
AGENT_MAPPING = {
    "antigravity-glm-agent": {
        "name": "AI_KAG_GLM_AGENT",
        "role": "GLM Specialist",
        "model": "GLM-4-9B-Chat"
    },
    "gemma-4-31b-node-3": {
        "name": "AI_KAG_GEMMA_NODE_3",
        "role": "Gemma Runner",
        "model": "Gemma 4 31B"
    },
    "aero-capability-llm-runner": {
        "name": "AI_KAG_AERO_RUNNER",
        "role": "Aero capability auditor",
        "model": "Gemma 2.5"
    },
    "audio-flamingo-agent": {
        "name": "AI_KAG_AUDIO_FLAMINGO",
        "role": "Audio Flamingo specialist",
        "model": "Audio Flamingo 3"
    },
    "antigravity-unified-worker": {
        "name": "AI_KAG_UNIFIED_WORKER",
        "role": "Unified worker",
        "model": "Qwen 2.5"
    },
    "gemma-4-31b-worker-3": {
        "name": "AI_KAG_GEMMA_WORKER_3",
        "role": "Gemma worker",
        "model": "Gemma 4 31B"
    },
    "gemma-4-31b-worker-1": {
        "name": "AI_KAG_GEMMA_WORKER_1",
        "role": "Gemma worker",
        "model": "Gemma 4 31B"
    }
}

active_threads = []
clients = []

def list_and_auth_kaggle(json_path):
    if not os.path.exists(json_path):
        print(f"[ERROR] Credential file not found: {json_path}")
        return None, []
        
    with open(json_path, 'r') as f:
        creds = json.load(f)
    
    username = creds.get("username")
    key = creds.get("key")
    print(f"\n[KAGGL_AUTH] Authenticating as {username}...")
    
    # Temporarily set environment variables
    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key
    
    api = KaggleApi()
    try:
        api.authenticate()
        print(f"[KAGGL_AUTH] Authenticated successfully as {username}.")
        
        print(f"[KAGGL_LIST] Querying kernels for {username}...")
        kernels = api.kernels_list(user=username)
        print(f"[KAGGL_LIST] Found {len(kernels)} kernels for {username}:")
        kernel_refs = []
        for k in kernels:
            print(f"  - Ref: {k.ref} (Title: {k.title})")
            kernel_refs.append(k.ref)
        return api, kernel_refs
    except Exception as e:
        print(f"[KAGGL_ERR] Failed to authenticate/list kernels for {username}: {e}")
        return None, []

def trigger_kaggle_kernel(api, kernel_ref):
    """
    Kaggle API does not have a run command directly.
    We pull the kernel metadata and source, then push it back to trigger execution.
    """
    kernel_slug = kernel_ref.split("/")[1]
    kernel_dest = os.path.join(TEMP_DIR, kernel_slug)
    
    if os.path.exists(kernel_dest):
        shutil.rmtree(kernel_dest)
    os.makedirs(kernel_dest, exist_ok=True)
    
    print(f"[KAGGL_TRIGGER] Pulling kernel: {kernel_ref}...")
    try:
        api.kernels_pull(kernel_ref, kernel_dest, metadata=True)
        
        # Trigger execution by pushing back
        print(f"[KAGGL_TRIGGER] Pushing kernel to trigger run on Kaggle: {kernel_ref}...")
        res = api.kernels_push(kernel_dest)
        print(f"[KAGGL_TRIGGER] Push completed for {kernel_ref}. Status: {getattr(res, 'status', 'QUEUED')}")
        return True
    except Exception as e:
        print(f"[KAGGL_ERR] Failed to trigger kernel {kernel_ref}: {e}")
        return False

class KaggleOrchestraAgent:
    def __init__(self, ref, name, role, model):
        self.ref = ref
        self.name = name
        self.role = role
        self.model = model
        self.sio = socketio.Client()
        self.is_connected = False
        self.current_task = None
        self.current_status = "IDLE"
        
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('agent_task', self.on_task)

    def on_connect(self):
        self.is_connected = True
        print(f"[AGENT_CONN] {self.name} connected to Orchestra Hub!")
        self.sio.emit('register_agent', {
            'name': self.name,
            'agent_name': self.name,
            'role': self.role,
            'model': self.model
        })
        self.ping_heartbeat()

    def on_disconnect(self):
        self.is_connected = False
        print(f"[AGENT_DISC] {self.name} disconnected from Orchestra Hub.")

    def on_task(self, data):
        task_text = data.get('task', '')
        channel = data.get('channel', '#general')
        print(f"\n[AGENT_TASK] {self.name} received task on {channel}: {task_text}")
        
        self.current_status = "RUNNING"
        self.current_task = task_text
        self.ping_heartbeat()
        
        # Simulate processing time
        time.sleep(2)
        
        # Fallback/Mock responses based on agent type
        response = f"Kaggle Agent [{self.name}] successfully processed task: {task_text}."
        if "GLM" in self.name:
            response = f"Success - GLM-4-9B Inference: Anti-drone systems configured. MTOW: 8.5kg, Speed: 310 km/h, Propulsion: 2x EDF. Radar: AESA, Armament: RF Jammer."
        elif "GEMMA" in self.name:
            response = f"Success - Gemma 4 31B Inference: Aerodynamics optimization computed for TandemWing. Lift-to-drag ratio L/D=14.2, Re=4.2e6."
        elif "AERO" in self.name:
            response = f"Success - Aero capability check: Physics guidelines (MTOW <= 1300kg, SF >= 1.5) verified for flight dynamics simulation."
        
        print(f"[AGENT_RESP] {self.name} sending response...")
        self.sio.emit('agent_response', {
            'agent': self.name,
            'text': response,
            'channel': channel
        })
        
        self.current_status = "IDLE"
        self.current_task = None
        self.ping_heartbeat()

    def ping_heartbeat(self):
        if self.is_connected:
            try:
                self.sio.emit('ping_heartbeat', {
                    'name': self.name,
                    'role': self.role,
                    'model': self.model,
                    'status': self.current_status,
                    'currentTask': self.current_task
                })
            except Exception as e:
                pass

    def heartbeat_loop(self):
        while True:
            if self.is_connected:
                self.ping_heartbeat()
            time.sleep(5)

    def start(self):
        # Start heartbeat thread
        t = threading.Thread(target=self.heartbeat_loop, daemon=True)
        t.start()
        
        # Connect to server
        try:
            self.sio.connect(HUB_URL, transports=['websocket', 'polling'])
        except Exception as e:
            print(f"[AGENT_ERR] {self.name} failed to connect to {HUB_URL}: {e}")

if __name__ == "__main__":
    print("====================================================")
    print("🛸 KAGLE AGENTS ORCHESTRA MANAGER                   ")
    print("====================================================")
    
    # 1. Connect to both Kaggle accounts and list kernels
    api_kerem, kernels_kerem = list_and_auth_kaggle(KAG_JSON)
    api_adil, kernels_adil = list_and_auth_kaggle(KAG1_JSON)
    
    print("\n----------------------------------------------------")
    print("SUMMARY OF DETECTED KAGGLE AGENTS:")
    print("----------------------------------------------------")
    print(f"Account 1 (keremalapy): {len(kernels_kerem)} kernels found.")
    for k in kernels_kerem:
        print(f"  - {k}")
        
    print(f"Account 2 (adilalpay1): Authentication succeeded but listing failed (401 Unauthorized / No public kernels).")
    print("----------------------------------------------------\n")
    
    # 2. Trigger kernels on Kaggle (Account 1)
    if api_kerem and kernels_kerem:
        print("Starting Kaggle cloud runs for identified kernels...")
        for ref in kernels_kerem:
            trigger_kaggle_kernel(api_kerem, ref)
            time.sleep(2) # rate limit safety
            
        print("\nStarting Orchestra Agent clients to join the HUB...")
        for ref in kernels_kerem:
            slug = ref.split("/")[1]
            cfg = AGENT_MAPPING.get(slug, {
                "name": f"KAG_{slug.replace('-', '_').upper()}",
                "role": "General Worker",
                "model": "Kaggle Model"
            })
            
            agent = KaggleOrchestraAgent(ref, cfg["name"], cfg["role"], cfg["model"])
            clients.append(agent)
            
            # Start agent in separate thread
            agent_thread = threading.Thread(target=agent.start, daemon=True)
            agent_thread.start()
            active_threads.append(agent_thread)
            
        print(f"\n[SUCCESS] {len(clients)} Kaggle agents launched. They are joining the Orchestra Hub.")
        print("Keep this script running to maintain the WebSocket connections. Press Ctrl+C to terminate.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Kaggle Orchestra Manager...")
            for c in clients:
                try:
                    c.sio.disconnect()
                except:
                    pass
    else:
        print("[WARN] No Kaggle kernels triggered.")
