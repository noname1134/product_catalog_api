import json

from redis_client import get_redis_client

from schemas.products_schema import ProductResponse

PRODUCT_CATALOG_CACHE_TTL_SECONDS = 60


def get_cached_products() -> list[dict] | None:
    client = get_redis_client()
    cached_value = client.get("products:all")

    if cached_value is None:
        return None

    return json.loads(cached_value)


def cache_products(products: list[dict]) -> None:
    client = get_redis_client()
    catalog = []
    for product in products:
        catalog.append(ProductResponse.model_validate(product).model_dump(mode="json"))
    json_string = json.dumps(catalog)
    client.set("products:all", json_string, ex=PRODUCT_CATALOG_CACHE_TTL_SECONDS)


def invalidate_products_cache() -> None:
    client = get_redis_client()
    client.delete("products:all")