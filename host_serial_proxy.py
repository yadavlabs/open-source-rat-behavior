import socket
import threading
from serial import Serial
from serial.tools import list_ports

PROXY_IP = "127.0.0.1"
API_PORT = 8888
SERIAL_BRIDGE_THREADS = {}

def handle_docker_api(client_socket):
    """Handles incoming setup requests from the containerized Flask app."""
    try:
        request = client_socket.recv(1024).decode('utf-8').strip()
        print(f"[Proxy] Received API request: '{request}'")
        
        # Action from 'findPorts' view route
        if request == "LIST_PORTS":
            ports = [p.device + " - " + p.description for p in list_ports.comports()]
            print(f"[Proxy] Found ports:")
            for port in ports:
                print(f"[Proxy] - {port}")
            # Send comma-separated Windows names back (e.g., "COM3,COM4")
            client_socket.sendall(f"{','.join(ports)}\n".encode('utf-8'))
            
        # Action from 'openCOMs' view route
        elif request.startswith("CONNECT:"):
            _, com_port, baudrate = request.split(":")
            success = start_serial_bridge(com_port, int(baudrate))
            response = "SUCCESS" if success else "FAILED"
            client_socket.sendall(f"{response}\n".encode('utf-8'))
    except Exception as e:
        print(f"[Proxy] API thread error: {e}")
    finally:
        client_socket.close()

def start_serial_bridge(com_port, baudrate):
    """Bridges the selected Windows COM port to an internal TCP Network Port."""
    if com_port in SERIAL_BRIDGE_THREADS:
        print(f"[Proxy] Port {com_port} is already bridged.")
        return True
    try:
        ser = Serial(com_port, baudrate, timeout=2)
        # Generate a distinct TCP network port dynamically (e.g., COM3 -> TCP 9003)
        digits = ''.join(filter(str.isdigit, com_port))
        tcp_port = 9000 + (int(digits) if digits else 0)
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((PROXY_IP, tcp_port))
        server.listen(1)
        
        def bridge_worker():
            print(f"[Proxy] Bridge active. Waiting for Docker to connect on TCP port {tcp_port}...")
            conn, _ = server.accept()
            print(f"[Proxy] Bi-directional hardware link established for {com_port}")
            
            # Subthread: Serial Data to Docker Network
            def serial_to_network():
                while True:
                    try:
                        if ser.is_open and ser.in_waiting > 0:
                            conn.sendall(ser.read(ser.in_waiting))
                    except: break
            
            # Subthread: Docker Network commands down to Serial
            def network_to_serial():
                while True:
                    try:
                        data = conn.recv(2048)
                        if not data: break
                        ser.write(data)
                    except: break

            t1 = threading.Thread(target=serial_to_network, daemon=True)
            t1.start()
            network_to_serial()
            
            # Clean up when connection cuts out
            ser.close()
            server.close()
            if com_port in SERIAL_BRIDGE_THREADS:
                del SERIAL_BRIDGE_THREADS[com_port]
            print(f"[Proxy] Disconnected and closed bridge for {com_port}")

        threading.Thread(target=bridge_worker, daemon=True).start()
        SERIAL_BRIDGE_THREADS[com_port] = tcp_port
        return True
    except Exception as e:
        print(f"[Proxy] Failed to initialize hardware bridge for {com_port}: {e}")
        return False

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((PROXY_IP, API_PORT))
    server.listen(5)
    server.settimeout(1.0)
    print(f"[Proxy] Listening for Docker hardware requests on port {API_PORT}")
    try:
        while True:
            try:
                client, _ = server.accept()
                threading.Thread(target=handle_docker_api, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\n[Proxy] Closing proxy server.")
    finally:
        server.close()
        print("[Proxy] Offline.")

if __name__ == "__main__":
    main()
