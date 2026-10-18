from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from elasticsearch import NotFoundError

from app.db.session import get_db
from app.search.client import es
from app.models.document import Document
from app.schemas.document import DocumentResponse


router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/search", response_model=list[DocumentResponse])
def search_documents(
    q: Annotated[str, Query(min_length=1, max_length=500)],
    session: Session = Depends(get_db)
):
    q = q.strip()

    if not q:
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be empty"
        )
        
    response = es.search(
        index="documents",
        query={
            "multi_match": {
                "query": q,
                "fields": ["text", "text.standard"]
            }
        },
        sort=[
            {"created_date": {"order": "desc"}}
            ],
        size=20
    )
    hits = response["hits"]["hits"]
    
    ids = []
    for hit in hits:
        ids.append(int(hit["_id"]))
    if not ids:
        return []
    
    stmt = select(Document).where(Document.id.in_(ids))
    result = session.scalars(stmt)
    documents = result.all()
        
    documents_by_id = {
        document.id: document
        for document in documents
    }
    ordered_documents = [
        documents_by_id[document_id]
        for document_id in ids
        if document_id in documents_by_id
    ]
    
    return ordered_documents

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    session: Session = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id)
    document = session.scalar(stmt)
    
    if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
            
    document_data = {
        "id": document.id,
        "text": document.text,
        "created_date": document.created_date.isoformat(),
    }
    
    deleted_from_elastic = False
    
    try:
        es.delete(index="documents",id=document_id)  
        deleted_from_elastic = True
    except NotFoundError:
        pass
    
    try:  
        session.delete(document)
        session.commit()
    except Exception:
        session.rollback()
        if deleted_from_elastic:
            es.index(
                index="documents",
                id=document_id,
                document=document_data
            ) 
        raise
    
    return {"message":f"Document {document_id} deleted"}
