from flask import Flask, jsonify, request, render_template
import socket, threading
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

def indian_time():
    return datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p IST")

state = {
    "monitoring": False,
    "detected": False,
    "intrusion_detected": False,
    "intrusion_reason": "Monitoring Stopped - Click Start Monitoring",
    "total_heartbeats": 0,
    "total_packets": 0,
    "tcp_count": 0,
    "udp_count": 0,
    "last_seen": "Never",
    "last_packet_type": "No Packet Yet",
    "source_name": "Beacon",
    "source_id": "BEACON-001",
    "events": [],
    "traffic": []
}

def log(level, message):
    print(f"[{indian_time()}] [{level}] {message}")

def handle_packet(proto, addr, data):
    if not state["monitoring"]:
        return

    now = indian_time()
    state["detected"] = True
    state["intrusion_detected"] = True
    state["intrusion_reason"] = "INTRUSION DETECTED - Beacon Packet Received!"
    state["total_heartbeats"] += 1
    state["total_packets"] = state["total_heartbeats"]

    if proto == "TCP":
        state["tcp_count"] += 1
        packet_name = "TCP Beacon Packet"
    else:
        state["udp_count"] += 1
        packet_name = "UDP Beacon Packet"

    state["last_seen"] = now
    state["last_packet_type"] = proto

    state["events"].insert(0, {"time": now, "source_name": "Beacon", "source_id": "BEACON-001", "status": "INTRUSION DETECTED - " + proto + " PACKET"})
    state["events"] = state["events"][:10]

    state["traffic"].insert(0, {"time": now, "src": addr[0], "proto": proto, "packet_name": packet_name})
    state["traffic"] = state["traffic"][:10]

    log("DETECTED", f"{packet_name} | Source: {addr[0]} | Total Packets: {state['total_packets']}")

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 9999))
    s.listen(5)
    log("INFO", "TCP Server Started on Port 9999")
    while True:
        try:
            conn, addr = s.accept()
            data = conn.recv(1024).decode(errors="ignore")
            conn.close()
            handle_packet("TCP", addr, data)
        except:
            pass

def udp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 9998))
    log("INFO", "UDP Server Started on Port 9998")
    while True:
        try:
            data, addr = s.recvfrom(1024)
            handle_packet("UDP", addr, data.decode(errors="ignore"))
        except:
            pass

threading.Thread(target=tcp_server, daemon=True).start()
threading.Thread(target=udp_server, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def get_status():
    return jsonify({
        "monitoring": state["monitoring"],
        "detected": state["detected"],
        "intrusion_detected": state["intrusion_detected"],
        "intrusion_reason": state["intrusion_reason"],
        "total_heartbeats": state["total_heartbeats"],
        "total_packets": state["total_heartbeats"],
        "tcp_count": state["tcp_count"],
        "udp_count": state["udp_count"],
        "last_seen": state["last_seen"],
        "last_packet_type": state["last_packet_type"],
        "source_name": "Beacon",
        "source_id": "BEACON-001",
        "events": state["events"],
        "traffic": state["traffic"]
    })

@app.route("/api/start_monitoring", methods=["POST"])
def start_monitoring():
    state["monitoring"] = True
    state["detected"] = False
    state["intrusion_detected"] = False
    state["intrusion_reason"] = "Monitoring Started - Waiting for Beacon..."
    state["total_heartbeats"] = 0
    state["total_packets"] = 0
    state["tcp_count"] = 0
    state["udp_count"] = 0
    state["last_seen"] = "Never"
    state["last_packet_type"] = "No Packet Yet"
    state["events"] = []
    state["traffic"] = []
    log("INFO", "Monitoring Started by User")
    return jsonify({"ok": True, "message": "Monitoring Started"})

@app.route("/api/stop_monitoring", methods=["POST"])
def stop_monitoring():
    state["monitoring"] = False
    state["detected"] = False
    state["intrusion_detected"] = False
    state["intrusion_reason"] = "Stopped by user"
    state["total_heartbeats"] = 0
    state["total_packets"] = 0
    state["tcp_count"] = 0
    state["udp_count"] = 0
    state["last_seen"] = "Never"
    state["last_packet_type"] = "No Packet Yet"
    state["events"] = []
    state["traffic"] = []
    log("INFO", "Monitoring Stopped by User")
    return jsonify({"ok": True, "message": "Monitoring Stopped"})

@app.route("/api/simulate_attack", methods=["POST"])
def simulate_attack():
    state["intrusion_detected"] = True
    state["intrusion_reason"] = "INTRUSION DETECTED - Suspicious Packet!"
    log("WARNING", "Simulated Attack Triggered by User")
    return jsonify({"ok": True, "message": "Attack Simulated!"})

@app.route("/api/stop_attack", methods=["POST"])
def stop_attack():
    state["intrusion_detected"] = False
    state["intrusion_reason"] = "Threat Cleared - No Intrusion"
    log("INFO", "Threat Cleared by User")
    return jsonify({"ok": True, "message": "Threat Cleared!"})

if __name__ == "__main__":
    log("INFO", "Cyber Threat Detection System Starting...")
    log("INFO", "Web Server Running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)