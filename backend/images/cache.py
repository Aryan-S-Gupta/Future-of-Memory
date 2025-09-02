from cachetools import TTLCache

world_image_text_cache = TTLCache(maxsize=1, ttl=600) # stores 1 entry (current world description), expires 10 mins
world_prompt_cache = TTLCache(maxsize=10, ttl=600) # mapping world_id to prompt_id

def cache_world_image_text(world_id: str, image_text: str) -> None:
    world_image_text_cache[world_id] = image_text

def get_cached_image_text(world_id: str) -> str:
    return world_image_text_cache[world_id]

def map_world_to_prompt(world_id: str, prompt_id: str) -> None:
    world_prompt_cache[str(world_id)] = prompt_id

def get_prompt_id_for_world(world_id: str) -> str:
    wid = str(world_id)
    if wid not in world_prompt_cache:
        raise KeyError(f'unknown world_id: {wid}')
    return world_prompt_cache[wid]