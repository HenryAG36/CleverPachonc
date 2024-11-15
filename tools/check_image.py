from PIL import Image
import os

def check_image():
    png_path = os.path.join("..", "src", "assets", "icons", "app_icon.png")
    
    if os.path.exists(png_path):
        # Open image and get info
        img = Image.open(png_path)
        
        print("📸 Image Analysis")
        print("================")
        print(f"📏 Size: {img.size[0]}x{img.size[1]} pixels")
        print(f"🎨 Mode: {img.mode}")
        print(f"📦 Format: {img.format}")
        print(f"💾 File size: {os.path.getsize(png_path) / 1024:.2f} KB")
        
        # Check if size is optimal
        if img.size[0] < 512 or img.size[1] < 512:
            print("\n⚠️ Warning: Image size is smaller than recommended (512x512)")
        
        # Check if mode is optimal
        if img.mode != "RGBA":
            print("\n⚠️ Warning: Image mode is not RGBA (recommended for transparency)")
            
    else:
        print("❌ Image file not found!")

if __name__ == "__main__":
    check_image() 