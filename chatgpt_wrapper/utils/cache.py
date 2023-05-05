from flask import current_app
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=24*60*60, key_prefix='predefined_characters')
def get_cached_character_names():
    return current_app.user_manager.orm.get_character_names()
