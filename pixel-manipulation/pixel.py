from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import random
import math

class GeometryEncryptor:
    def __init__(self, root):
        self.root = root
        self.root.title("Geometry Encryptor")
        self.original = None
        self.processed = None
        self.tk_image = None
        self.grid_size = 4  # 4x4 grid for block manipulation
        
        self.create_widgets()
    
    def create_widgets(self):
        self.label = tk.Label(self.root)
        self.label.pack(padx=10, pady=10)
        
        controls = tk.Frame(self.root)
        controls.pack(pady=10)
        
        tk.Button(controls, text="Open", command=self.open_image).grid(row=0, column=0, padx=5)
        tk.Button(controls, text="Encrypt", command=lambda: self.process_image("encrypt")).grid(row=0, column=1, padx=5)
        tk.Button(controls, text="Decrypt", command=lambda: self.process_image("decrypt")).grid(row=0, column=2, padx=5)
        tk.Button(controls, text="Save", command=self.save_image).grid(row=0, column=3, padx=5)
        
        self.key_var = tk.StringVar(value="12345")
        tk.Label(controls, text="Encryption Key:").grid(row=1, column=0, pady=5)
        tk.Entry(controls, textvariable=self.key_var).grid(row=1, column=1, columnspan=3)

    def open_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.original = Image.open(path).convert("RGB")
            self.processed = self.original.copy()
            self.display_image()

    def display_image(self):
        if self.processed:
            display_copy = self.processed.resize((400, 400))
            self.tk_image = ImageTk.PhotoImage(display_copy)
            self.label.config(image=self.tk_image)

    def process_image(self, mode):
        if not self.processed or not self.key_var.get():
            return

        key = int(self.key_var.get())
        random.seed(key)
        
        # Process both geometry and color
        if mode == "encrypt":
            self.processed = self.geometry_encrypt(self.processed, key)
            self.processed = self.color_encrypt(self.processed, key)
        else:
            self.processed = self.color_decrypt(self.processed, key)
            self.processed = self.geometry_decrypt(self.processed, key)
        
        self.display_image()

    def geometry_encrypt(self, img, key):
        """Split image into blocks and shuffle them with random rotations"""
        width, height = img.size
        
        # Calculate block size
        block_w = width // self.grid_size
        block_h = height // self.grid_size
        
        # Create blocks
        blocks = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                left = i * block_w
                upper = j * block_h
                right = left + block_w
                lower = upper + block_h
                block = img.crop((left, upper, right, lower))
                
                # Random rotation (0°, 90°, 180°, 270°)
                blocks.append(block.rotate(90 * random.randint(0, 3)))
        
        # Shuffle blocks
        random.shuffle(blocks)
        
        # Rebuild image
        encrypted = Image.new("RGB", (width, height))
        for idx, block in enumerate(blocks):
            col = idx % self.grid_size
            row = idx // self.grid_size
            x = col * block_w
            y = row * block_h
            encrypted.paste(block, (x, y))
        
        return encrypted

    def geometry_decrypt(self, img, key):
        """Reverse the block shuffling and rotations"""
        width, height = img.size
        block_w = width // self.grid_size
        block_h = height // self.grid_size
        
        # Generate original shuffle order
        random.seed(key)
        total_blocks = self.grid_size ** 2
        original_indices = list(range(total_blocks))
        random.shuffle(original_indices)
        
        # Create reverse mapping
        reverse_mapping = {original_indices[i]: i for i in range(total_blocks)}
        
        # Extract blocks
        blocks = []
        for idx in range(total_blocks):
            col = idx % self.grid_size
            row = idx // self.grid_size
            left = col * block_w
            upper = row * block_h
            right = left + block_w
            lower = upper + block_h
            block = img.crop((left, upper, right, lower))
            blocks.append(block)
        
        # Reorder blocks and reverse rotations
        original_blocks = [None] * total_blocks
        for new_idx, block in enumerate(blocks):
            original_idx = reverse_mapping[new_idx]
            
            # Reverse rotation (need to track original rotation)
            random.seed(key + new_idx)  # Unique seed per block
            rotation = 90 * random.randint(0, 3)
            original_blocks[original_idx] = block.rotate(-rotation)
        
        # Rebuild original image
        decrypted = Image.new("RGB", (width, height))
        for idx, block in enumerate(original_blocks):
            col = idx % self.grid_size
            row = idx // self.grid_size
            x = col * block_w
            y = row * block_h
            decrypted.paste(block, (x, y))
        
        return decrypted

    def color_encrypt(self, img, key):
        """XOR color encryption with channel mixing"""
        pixels = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                r, g, b = pixels[i, j]
                pixels[i, j] = (
                    (r ^ key) % 256,
                    (g ^ (key >> 8)) % 256,
                    (b ^ (key >> 16)) % 256
                )
        return img

    def color_decrypt(self, img, key):
        """Reverse color encryption (same as encrypt)"""
        return self.color_encrypt(img, key)  # XOR is self-inverse

    def save_image(self):
        if self.processed:
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("BMP", "*.bmp")]
            )
            if path:
                self.processed.save(path)

if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryEncryptor(root)
    root.mainloop()