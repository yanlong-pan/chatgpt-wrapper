from flask import current_app
from flask_caching import Cache

from chatgpt_wrapper.backends.openai.orm import Character

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=24*60*60, key_prefix='predefined_characters')
def get_cached_characters():
    return Character.get_characters()
