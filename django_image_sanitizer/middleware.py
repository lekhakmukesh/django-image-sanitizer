import os
import logging
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin

from .utils import sanitize_and_convert_image

logger = logging.getLogger(__name__)

class ImageSanitizerMiddleware(MiddlewareMixin):
    """
    Global Middleware to intercept all file uploads project-wide. 
    - Strictly blocks SVGs to prevent XSS.
    - Sanitizes and optimizes all raster images.
    """

    def process_request(self, request):
        if not request.FILES:
            return None

        for field_name in request.FILES.keys():
            files_list = request.FILES.getlist(field_name)
            new_files_list = []
            modified = False

            for uploaded_file in files_list:
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                content_type = uploaded_file.content_type or ""

                # 1. Block SVGs
                if file_ext == '.svg' or content_type == 'image/svg+xml':
                    logger.warning(f"Global Policy: Blocked SVG from {request.path}: {uploaded_file.name}")
                    return HttpResponseBadRequest(
                        "Security Policy: SVG files are not permitted. Please use JPG, PNG, or WebP."
                    )

                # 2. Process raster images
                elif content_type.startswith("image/") or file_ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'):
                    sanitized_data = sanitize_and_convert_image(uploaded_file)
                    
                    if sanitized_data:
                        new_filename, buffer, size = sanitized_data
                        out_content_type = "image/webp" if new_filename.endswith(".webp") else "image/png"
                        
                        new_file = InMemoryUploadedFile(
                            file=buffer,
                            field_name=field_name,
                            name=new_filename,
                            content_type=out_content_type,
                            size=size,
                            charset=None,
                        )
                        new_files_list.append(new_file)
                        modified = True
                    else:
                        return HttpResponseBadRequest(f"Security Alert: The file '{uploaded_file.name}' is invalid or corrupt.")
                
                else:
                    new_files_list.append(uploaded_file)

            if modified:
                request.FILES.setlist(field_name, new_files_list)

        return None