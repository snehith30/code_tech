import tkinter as tk
from tkinter import filedialog, messagebox
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import os

class SecureFileApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AES-256 File Encryptor")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        self.filepath = None

        # UI Elements
        tk.Label(root, text="Target File:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        
        self.file_label = tk.Label(root, text="No file selected", fg="gray")
        self.file_label.pack(pady=5)
        
        tk.Button(root, text="Browse File", command=self.select_file, width=15).pack()

        tk.Label(root, text="Password:", font=("Arial", 10, "bold")).pack(pady=(15, 0))
        self.password_entry = tk.Entry(root, show="*", width=30)
        self.password_entry.pack(pady=5)

        # Buttons Frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Encrypt", command=self.encrypt_file, bg="#ff9999", width=12).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Decrypt", command=self.decrypt_file, bg="#99ff99", width=12).grid(row=0, column=1, padx=10)

    def select_file(self):
        self.filepath = filedialog.askopenfilename()
        if self.filepath:
            self.file_label.config(text=os.path.basename(self.filepath), fg="black")

    def get_key(self, password, salt):
        """Derives a 32-byte (256-bit) key from the password using PBKDF2."""
        return PBKDF2(password, salt, dkLen=32, count=1000000)

    def encrypt_file(self):
        if not self.filepath:
            messagebox.showwarning("Error", "Please select a file first.")
            return
        
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Error", "Please enter a password.")
            return

        try:
            with open(self.filepath, 'rb') as f:
                plaintext = f.read()

            # Generate a random salt and initialization vector (IV)
            salt = get_random_bytes(16)
            iv = get_random_bytes(16)
            key = self.get_key(password, salt)

            # Initialize AES cipher in CBC mode
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

            # Save the encrypted file (Salt + IV + Ciphertext)
            out_file = self.filepath + ".enc"
            with open(out_file, 'wb') as f:
                f.write(salt + iv + ciphertext)

            messagebox.showinfo("Success", f"File encrypted successfully!\nSaved as: {os.path.basename(out_file)}")
            self.password_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))

    def decrypt_file(self):
        if not self.filepath:
            messagebox.showwarning("Error", "Please select a file first.")
            return
            
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Error", "Please enter a password.")
            return

        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()

            # Extract the salt, IV, and the actual encrypted data
            salt = data[:16]
            iv = data[16:32]
            ciphertext = data[32:]

            key = self.get_key(password, salt)

            # Initialize AES cipher for decryption
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

            # Remove .enc extension if present, or append .dec
            if self.filepath.endswith(".enc"):
                out_file = self.filepath[:-4]
            else:
                out_file = self.filepath + ".dec"

            with open(out_file, 'wb') as f:
                f.write(plaintext)

            messagebox.showinfo("Success", f"File decrypted successfully!\nSaved as: {os.path.basename(out_file)}")
            self.password_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Decryption Error", "Incorrect password or corrupted file.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureFileApp(root)
    root.mainloop()