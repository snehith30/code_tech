import socket
import concurrent.futures

def scan_port(ip, port, timeout=1.0):
    """Attempts to connect to a specific port on the target IP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            # Returns 0 if connection succeeds
            if s.connect_ex((ip, port)) == 0:
                try:
                    # Attempt basic banner grabbing
                    banner = s.recv(1024).decode().strip()
                except:
                    banner = ""
                return port, True, banner
    except:
        pass
    return port, False, ""

def run_scanner(target_ip, start_port=1, end_port=1024, threads=100):
    """Manages the thread pool for scanning a range of ports."""
    print(f"\n[*] Starting scan on target: {target_ip}")
    print(f"[*] Scanning ports {start_port} to {end_port}...\n")
    
    open_ports = []
    
    # Use ThreadPoolExecutor for concurrent scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        # Submit all tasks to the executor
        futures = {executor.submit(scan_port, target_ip, port): port for port in range(start_port, end_port + 1)}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            port, is_open, banner = future.result()
            if is_open:
                open_ports.append(port)
                if banner:
                    print(f"[+] Port {port} is OPEN - Banner: {banner[:50]}")
                else:
                    print(f"[+] Port {port} is OPEN")
                    
    print(f"\n[*] Scan complete. Found {len(open_ports)} open ports.")
    return open_ports