import os
import logging
from io import BytesIO
from PIL import Image
from django.conf import settings

logger = logging.getLogger(__name__)

# Allow users to override the max size in their settings.py, fallback to 10MB
MAX_IMAGE_SIZE = getattr(settings, 'IMAGE_SANITIZER_MAX_SIZE', 10 * 1024 * 1024)


def sanitize_and_convert_image(image_file):
    """
    Processes RASTER images and converts them to WebP globally.
    Verifies pixel integrity and strips all metadata/EXIF data.
    """
    try:
        if image_file.size > MAX_IMAGE_SIZE:
            logger.warning(f"Global Sanitizer: {image_file.name} blocked (exceeds {MAX_IMAGE_SIZE/(1024*1024)}MB).")
            return None

        image_file.seek(0)
        
        try:
            img = Image.open(image_file)
            img.load() 
        except Exception as e:
            logger.error(f"Global Sanitizer: {image_file.name} failed verification. Error: {e}")
            return None

        if img.mode in ("RGBA", "LA", "P") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        clean_img = Image.new(img.mode, img.size)
        clean_img.paste(img)

        buffer = BytesIO()
        
        try:
            clean_img.save(buffer, format="WEBP", quality=85, optimize=True)
        except ValueError:
            logger.warning("Global Sanitizer: WEBP not supported. Falling back to PNG.")
            buffer = BytesIO()
            clean_img.save(buffer, format="PNG", optimize=True)

        size = buffer.tell()
        if size == 0:
            return None
            
        buffer.seek(0)
        name = os.path.splitext(image_file.name)[0]
        
        is_webp = buffer.getvalue()[:4] == b'RIFF'
        extension = "webp" if is_webp else "png"
        
        return f"{name}.{extension}", buffer, size

    except Exception as e:
        logger.error(f"Global Sanitizer: General failure for {image_file.name}: {e}")
        return None