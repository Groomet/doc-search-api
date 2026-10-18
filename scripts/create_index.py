from app.search.client import es

INDEX_NAME = "documents"

mapping = {
    "properties": {
        "id": {"type": "integer"},
        "text": {
            "type": "text",
            "analyzer": "russian",
            "fields": {
                "standard": {
                    "type": "text",
                    "analyzer": "standard"
                }
            }
        },
        "created_date": {"type": "date"}
    }
}

if es.indices.exists(index=INDEX_NAME):
    es.indices.put_mapping(
        index=INDEX_NAME,
        properties=mapping["properties"]
    )
    print("Mapping обновлён")
else:
    es.indices.create(
        index=INDEX_NAME,
        mappings=mapping
    )
    print("Индекс создан")