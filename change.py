import hashlib
import os
import json

def calculate_file_hash(filepath, algorithm='sha256'):
    """Calculates the hash of a file using the specified algorithm."""
    hash_func = getattr(hashlib, algorithm)()
    try:
        with open(filepath, 'rb') as f:
            # Read the file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def scan_directory(directory_path):
    """Scans a directory recursively and returns a dictionary of filepath: hash."""
    file_hashes = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            filepath = os.path.join(root, file)
            file_hash = calculate_file_hash(filepath)
            if file_hash:
                file_hashes[filepath] = file_hash
    return file_hashes

def monitor_files(directory_to_monitor, baseline_file='hash_baseline.json'):
    """Monitors a directory for changes by comparing current hashes to a saved baseline."""
    print(f"[*] Scanning directory: {directory_to_monitor}...")
    current_hashes = scan_directory(directory_to_monitor)

    # Check if a baseline exists
    if not os.path.exists(baseline_file):
        print("[*] No baseline found. Creating a new baseline...")
        with open(baseline_file, 'w') as f:
            json.dump(current_hashes, f, indent=4)
        print("[+] Baseline successfully created. Run the script again later to detect changes.")
        return

    print("[*] Comparing current files against existing baseline...")
    with open(baseline_file, 'r') as f:
        baseline_hashes = json.load(f)

    new_files = []
    modified_files = []
    deleted_files = []

    # Check for new and modified files
    for filepath, current_hash in current_hashes.items():
        if filepath not in baseline_hashes:
            new_files.append(filepath)
        elif current_hash != baseline_hashes[filepath]:
            modified_files.append(filepath)

    # Check for deleted files
    for filepath in baseline_hashes:
        if filepath not in current_hashes:
            deleted_files.append(filepath)

    # Output the results of the comparison
    if not new_files and not modified_files and not deleted_files:
        print("\n[+] No changes detected. File integrity is intact.")
    else:
        print("\n[!] ALERT: Changes Detected!\n" + "="*30)
        if new_files:
            print("\n[+] NEW FILES:")
            for f in new_files: print(f"  --> {f}")
        if modified_files:
            print("\n[!] MODIFIED FILES:")
            for f in modified_files: print(f"  --> {f}")
        if deleted_files:
            print("\n[-] DELETED FILES:")
            for f in deleted_files: print(f"  --> {f}")

        # Optional: Ask to update the baseline
        update = input("\nDo you want to update the baseline with these changes? (y/n): ").strip().lower()
        if update == 'y':
            with open(baseline_file, 'w') as f:
                json.dump(current_hashes, f, indent=4)
            print("[+] Baseline updated.")

if __name__ == "__main__":
    print("--- File Integrity Monitoring Tool ---")
    target_dir = input("Enter the absolute or relative path of the directory to monitor: ")
    
    if os.path.isdir(target_dir):
        monitor_files(target_dir)
    else:
        print("[-] Invalid directory path. Please check the path and try again.")