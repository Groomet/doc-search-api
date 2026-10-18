from sqlalchemy import select
from elasticsearch.helpers import bulk

from app.db.session import SessionLocal
from app.search.client import es
from app.models.document import Document


with SessionLocal() as session:
    stmt = select(Document)
    result = session.scalars(stmt)
    documents = result.all()
    data=[]
    
    for document in documents:
        item={
            "id":document.id,
            "text":document.text,
            "created_date":document.created_date.isoformat()
        }
        data.append(item)
    
    actions=[]
    
    for item in data:
        action = {
            "_index": "documents",
            "_id": item["id"],
            "_source": item
        }
        actions.append(action)
    
    success, errors = bulk(es, actions)
    
    print("Успешно проиндексировано:", success)
    print("Ошибки:", errors)
    es.indices.refresh(index="documents")
    print("Документов в индексе:", es.count(index="documents")["count"])
    