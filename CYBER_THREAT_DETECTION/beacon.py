import socket
import time
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def log_time():
    return datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p IST")

print(f"[{log_time()}] [INFO] Beacon Service Started - TCP / UDP Mode")
count = 0

while True:
    count += 1
    try:
        if count % 2 == 1:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 9999))
            s.sendall(b"TCP BEACON PACKET")
            s.close()
            print(f"[{log_time()}] [SENT] TCP Beacon Packet Transmitted")
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b"UDP BEACON PACKET", ("127.0.0.1", 9998))
            s.close()
            print(f"[{log_time()}] [SENT] UDP Beacon Packet Transmitted")
    except:
        print(f"[{log_time()}] [ERROR] Server Not Reachable - Retrying...")
    time.sleep(2)