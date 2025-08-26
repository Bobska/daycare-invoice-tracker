"""
Structured logging and error handling utilities for invoice management
"""
import logging
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
import traceback

class StructuredLogger:
    """Structured logging with correlation IDs"""
    
    @staticmethod
    def get_correlation_id(request):
        """Get or create correlation ID for request tracking"""
        if hasattr(request, 'correlation_id'):
            return request.correlation_id
        
        correlation_id = str(uuid.uuid4())[:8]
        request.correlation_id = correlation_id
        return correlation_id
    
    @staticmethod
    def log_error(logger, message, error=None, request=None, extra_data=None):
        """Structured error logging"""
        log_data = {
            'message': message,
            'correlation_id': StructuredLogger.get_correlation_id(request) if request else None,
            'user_id': request.user.id if request and request.user.is_authenticated else None,
        }
        
        if error:
            log_data.update({
                'error_type': error.__class__.__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            })
        
        if extra_data:
            log_data.update(extra_data)
        
        logger.error("Application Error", extra=log_data)
    
    @staticmethod
    def log_info(logger, message, request=None, extra_data=None):
        """Structured info logging"""
        log_data = {
            'message': message,
            'correlation_id': StructuredLogger.get_correlation_id(request) if request else None,
            'user_id': request.user.id if request and request.user.is_authenticated else None,
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        logger.info(message, extra=log_data)

# Create custom exception classes
class PDFProcessingError(Exception):
    """Specific exception for PDF processing issues"""
    pass

class InvoiceValidationError(Exception):
    """Specific exception for invoice validation issues"""
    pass

class FileUploadError(Exception):
    """Specific exception for file upload issues"""
    pass

# Rate limiting decorator
from django.core.cache import cache
from django.http import HttpResponse
import time

def rate_limit_uploads(max_uploads=5, window_minutes=10):
    """Rate limiting decorator for file uploads"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST' and request.FILES:
                user_id = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
                cache_key = f'upload_rate_limit_{user_id}'
                
                uploads = cache.get(cache_key, [])
                now = time.time()
                # Remove uploads older than window
                uploads = [upload_time for upload_time in uploads if now - upload_time < window_minutes * 60]
                
                if len(uploads) >= max_uploads:
                    response = HttpResponse("Too many uploads. Please wait before uploading again.", status=429)
                    response['Retry-After'] = str(window_minutes * 60)
                    return response
                
                uploads.append(now)
                cache.set(cache_key, uploads, window_minutes * 60)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
