from elasticsearch import Elasticsearch, AsyncElasticsearch

from app.core.config import settings

es = Elasticsearch(settings.elastic_url)
es_async = AsyncElasticsearch(settings.elastic_url)
