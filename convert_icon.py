from PIL import Image
import os

def create_ico(png_path, ico_path):
    # Открываем PNG файл
    img = Image.open(png_path)
    
    # Создаем список изображений разных размеров
    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    images = []
    
    for size in sizes:
        # Создаем копию изображения нужного размера
        resized_img = img.resize(size, Image.Resampling.LANCZOS)
        images.append(resized_img)
    
    # Сохраняем как ICO
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(img.size[0], img.size[1]) for img in images],
        append_images=images[1:]
    )

if __name__ == '__main__':
    png_path = os.path.join('ui', 'icons', 'icon.png')
    ico_path = os.path.join('ui', 'icons', 'icon.ico')
    create_ico(png_path, ico_path) 