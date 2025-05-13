#!/usr/bin/env python3
"""
Simple script to generate a Gomoku game icon
"""

from PIL import Image, ImageDraw

def create_gomoku_icon(size=512, output_path=None):
    # Create a blank image with transparent background
    image = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Calculate padding and board dimensions
    padding = size * 0.1
    board_size = size - 2 * padding
    cell_size = board_size / 8
    
    # Draw board background (wooden texture)
    draw.rectangle(
        [(padding, padding), (size - padding, size - padding)],
        fill=(224, 184, 121, 255)  # #E0B879
    )
    
    # Draw grid lines
    for i in range(9):
        # Horizontal lines
        y = padding + i * cell_size
        draw.line([(padding, y), (size - padding, y)], fill=(0, 0, 0, 255), width=max(1, int(size/256)))
        
        # Vertical lines
        x = padding + i * cell_size
        draw.line([(x, padding), (x, size - padding)], fill=(0, 0, 0, 255), width=max(1, int(size/256)))
    
    # Draw stones
    stone_radius = cell_size * 0.4
    
    # Black stones
    draw.ellipse(
        [(padding + 2*cell_size - stone_radius, padding + 2*cell_size - stone_radius),
         (padding + 2*cell_size + stone_radius, padding + 2*cell_size + stone_radius)],
        fill=(0, 0, 0, 255)
    )
    
    draw.ellipse(
        [(padding + 6*cell_size - stone_radius, padding + 4*cell_size - stone_radius),
         (padding + 6*cell_size + stone_radius, padding + 4*cell_size + stone_radius)],
        fill=(0, 0, 0, 255)
    )
    
    draw.ellipse(
        [(padding + 4*cell_size - stone_radius, padding + 6*cell_size - stone_radius),
         (padding + 4*cell_size + stone_radius, padding + 6*cell_size + stone_radius)],
        fill=(0, 0, 0, 255)
    )
    
    # White stones with black outline
    draw.ellipse(
        [(padding + 4*cell_size - stone_radius, padding + 2*cell_size - stone_radius),
         (padding + 4*cell_size + stone_radius, padding + 2*cell_size + stone_radius)],
        fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=max(1, int(size/256))
    )
    
    draw.ellipse(
        [(padding + 2*cell_size - stone_radius, padding + 4*cell_size - stone_radius),
         (padding + 2*cell_size + stone_radius, padding + 4*cell_size + stone_radius)],
        fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=max(1, int(size/256))
    )
    
    draw.ellipse(
        [(padding + 6*cell_size - stone_radius, padding + 6*cell_size - stone_radius),
         (padding + 6*cell_size + stone_radius, padding + 6*cell_size + stone_radius)],
        fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=max(1, int(size/256))
    )
    
    # Save the image
    if output_path:
        image.save(output_path)
    
    return image

if __name__ == "__main__":
    import os
    
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')
    
    # Create resources directory if it doesn't exist
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    icon_path = os.path.join(resources_dir, 'gomoku_icon.png')
    create_gomoku_icon(512, icon_path)
    print(f"Icon created at: {icon_path}")
