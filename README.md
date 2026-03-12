# Django Image Sanitizer

A lightweight, global Django middleware that automatically intercepts file uploads to sanitize images, prevent XSS attacks, and optimize storage by converting raster images to WebP.

## 🚀 Features

* **Global Interception:** Works at the middleware level, meaning it automatically applies to all image uploads across your entire Django project without needing to modify individual forms or models.
* **XSS Prevention:** Strictly blocks `.svg` files and `image/svg+xml` content types to prevent malicious scripts from being uploaded.
* **Automatic WebP Conversion:** Converts standard raster images (JPG, PNG, BMP, etc.) to optimized WebP format to save server space and improve page load speeds.
* **Pixel Integrity Verification:** Uses Pillow to verify the actual file contents, ensuring that disguised malicious files are caught even if their extension is changed.
* **Configurable Size Limits:** Easily set a maximum file size for image uploads directly in your Django settings.
* **EXIF Data Stripping:** Automatically removes metadata from images during the conversion process for enhanced user privacy.

## 📦 Installation

Install the package via pip:

```bash
pip install django-image-sanitizer
```
## ⚙️ Configuration
```
1. Add to Middleware

Open your Django settings.py and add the sanitizer to your MIDDLEWARE list. It is recommended to place it after security and authentication middlewares, but before any routing middlewares.

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Add the image sanitizer middleware
    'django_image_sanitizer.middleware.ImageSanitizerMiddleware',
]

2. Configure Settings (Optional)

By default, the middleware blocks any image larger than 10MB. You can override this limit by adding IMAGE_SANITIZER_MAX_SIZE to your settings.py.

The value should be in bytes.

# settings.py

# Example: Set maximum upload size to 5MB
IMAGE_SANITIZER_MAX_SIZE = 5 * 1024 * 1024

```

## 🛠️ How It Works
Once installed and added to your middleware, django-image-sanitizer sits quietly in the background.

Whenever a user submits a POST request containing files (request.FILES), the middleware:

Checks if the file is an SVG and blocks it with an HttpResponseBadRequest if so.

Checks if the file is a raster image.

If it is a raster image, it verifies the file integrity, strips metadata, converts it to WebP (or PNG as a fallback), and updates the request.FILES object in memory.

Passes the sanitized, compressed image down to your views and forms as if the user uploaded the WebP file directly.

Non-image files (like PDFs or text documents) are ignored and pass through the middleware untouched.

## 📄 License
This project is licensed under the MIT License.