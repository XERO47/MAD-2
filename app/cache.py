from functools import wraps
from flask_caching import Cache
from flask import current_app

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes default timeout
})

def get_cache_key(*args, **kwargs):
    """Generate a cache key based on the function arguments"""
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()
    return f"user_{user_id}_{args}_{kwargs}"

def get_admin_cache_key(*args, **kwargs):
    """Generate a cache key for admin routes"""
    return f"admin_{args}_{kwargs}"

def cache_response(timeout=300):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = get_cache_key(*args, **kwargs)
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def admin_cache_response(timeout=300):
    """Decorator to cache admin API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = get_admin_cache_key(*args, **kwargs)
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def clear_cache_for_user(user_id):
    """Clear all cache entries for a specific user"""
    # Since we can't easily clear by prefix with Redis, we'll need to implement
    # a more sophisticated cache invalidation strategy in a production environment
    cache.clear()

def clear_admin_cache():
    """Clear all admin cache entries"""
    cache.clear()

def clear_quiz_cache(quiz_id):
    """Clear cache for a specific quiz"""
    cache.delete(f"quiz_{quiz_id}")
    cache.delete(f"quiz_attempts_{quiz_id}")

def clear_subject_cache(subject_id):
    """Clear cache for a specific subject"""
    cache.delete(f"subject_{subject_id}")
    cache.delete(f"subject_chapters_{subject_id}") 