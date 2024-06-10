from PIL import Image, ImageDraw

def convert_percentage_to_pixel(coordinate_ratios, img_width, img_height):
    # Unpack the coordinates
    x1, y1, x2, y2 = coordinate_ratios
    
    # Convert the coordinates from ratios to pixels
    x1_pixel = int(x1 * img_width/100)
    y1_pixel = int(y1 * img_height/100)
    x2_pixel = int(x2 * img_width/100)
    y2_pixel = int(y2 * img_height/100)
    
    return (x1_pixel, y1_pixel, x2_pixel, y2_pixel)

# Load the image
image_path = 'RPA/screenshot.png'
with Image.open(image_path) as img:
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    # Define bounding box coordinates (ratio approximations)
    library_button = convert_percentage_to_pixel((0.98, 5.32, 2.93, 8.87), img_width, img_height)
    new_track_button = convert_percentage_to_pixel((6.84, 4.88, 11.72, 8.43), img_width, img_height)
    record_button = convert_percentage_to_pixel((45.90, 3.55, 47.85, 7.10), img_width, img_height)

    # Define the color and width of the rectangles
    color = 'red'
    width = 3

    # Draw rectangles around the estimated button locations
    draw.rectangle(library_button, outline=color, width=width)
    draw.rectangle(new_track_button, outline=color, width=width)
    draw.rectangle(record_button, outline=color, width=width)
    
    # Save the modified image
    highlighted_image_path = 'Screenshot_with_Bounding_Boxes.png'
    img.save(highlighted_image_path)
