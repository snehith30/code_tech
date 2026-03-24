import sys
import os
# Add the current directory to the path so it can find the modules folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules import port_scanner

def display_menu():
    print("\n" + "="*40)
    print("      PYTHON RECONNAISSANCE TOOLKIT      ")
    print("="*40)
    print("  [1] TCP Port Scanner")
    print("  [2] Future Module (e.g., Subdomain Enum)")
    print("  [0] Exit")
    print("="*40)

def main():
    while True:
        display_menu()
        choice = input("\nSelect a module: ").strip()
        
        if choice == '1':
            target = input("Enter target IP address: ").strip()
            try:
                start = int(input("Enter start port (default 1): ") or 1)
                end = int(input("Enter end port (default 1024): ") or 1024)
                threads = int(input("Enter number of threads (default 100): ") or 100)
                port_scanner.run_scanner(target, start, end, threads)
            except ValueError:
                print("[-] Invalid input. Please enter numerical values for ports and threads.")
                
        elif choice == '2':
            print("\n[*] Module not yet implemented. Build it and plug it in!")
            
        elif choice == '0':
            print("\n[*] Exiting toolkit. Goodbye!")
            sys.exit(0)
            
        else:
            print("\n[-] Invalid selection. Try again.")

if __name__ == "__main__":
    main()