from PIL import Image, ImageEnhance
import os

def create_ico():
    png_path = os.path.join("..", "src", "assets", "icons", "app_icon.png")
    ico_path = os.path.join("..", "src", "assets", "icons", "app_icon.ico")
    
    if os.path.exists(png_path):
        # Open and convert to RGBA
        img = Image.open(png_path)
        img = img.convert('RGBA')
        
        # Windows-optimized sizes
        icon_sizes = [
            (16,16),    # Taskbar small
            (20,20),    # Taskbar medium
            (24,24),    # Taskbar large
            (32,32),    # Default window icon
            (40,40),    # Alt+Tab small
            (48,48),    # Alt+Tab medium
            (64,64),    # Alt+Tab large
            (96,96),    # Start menu
            (128,128),  # File explorer
            (256,256),  # High-DPI displays
            (512,512)   # Maximum size
        ]
        
        img_list = []
        
        for size in icon_sizes:
            # Enhanced resize with multiple steps for better quality
            if size[0] < img.size[0]:
                # Calculate intermediate size for smoother downscaling
                intermediate_size = (
                    img.size[0] // 2,
                    img.size[1] // 2
                )
                temp_img = img.resize(intermediate_size, Image.Resampling.LANCZOS)
                resized_img = temp_img.resize(size, Image.Resampling.LANCZOS)
            else:
                resized_img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Enhance sharpness slightly
            enhancer = ImageEnhance.Sharpness(resized_img)
            resized_img = enhancer.enhance(1.1)  # Subtle sharpness
            
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(resized_img)
            resized_img = enhancer.enhance(1.05)  # Very subtle contrast
            
            img_list.append(resized_img)
        
        # Save as ICO with all sizes
        img_list[0].save(
            ico_path,
            format='ICO',
            sizes=icon_sizes,
            append_images=img_list[1:],
            quality=100  # Maximum quality
        )
        print("✨ Windows-optimized ICO file created successfully!")
        print("📏 Included sizes:", ", ".join(f"{s[0]}x{s[1]}" for s in icon_sizes))
    else:
        print("❌ Source PNG file not found!")

if __name__ == "__main__":
    create_ico() 