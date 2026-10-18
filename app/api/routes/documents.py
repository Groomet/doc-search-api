from typing import Annotated

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.search.client import es_async


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/search", response_model=list[DocumentResponse])
async def search_documents(
    q: Annotated[str, Query(min_length=1, max_length=500)],
    session: AsyncSession = Depends(get_async_db),
):
    q = q.strip()

    if not q:
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be empty",
        )

    response = await es_async.search(
        index="documents",
        query={
            "multi_match": {
                "query": q,
                "fields": ["text", "text.standard"],
            }
        },
        sort=[{"created_date": {"order": "desc"}}],
        size=20,
    )

    hits = response["hits"]["hits"]
    ids = [int(hit["_id"]) for hit in hits]

    if not ids:
        return []

    stmt = select(Document).where(Document.id.in_(ids))
    result = await session.scalars(stmt)
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
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_async_db),
):
    stmt = select(Document).where(Document.id == document_id)
    document = await session.scalar(stmt)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    document_data = {
        "id": document.id,
        "text": document.text,
        "created_date": document.created_date.isoformat(),
    }

    deleted_from_elastic = False

    try:
        await es_async.delete(
            index="documents",
            id=document_id,
        )
        deleted_from_elastic = True
    except NotFoundError:
        pass

    try:
        await session.delete(document)
        await session.commit()
    except Exception:
        await session.rollback()

        if deleted_from_elastic:
            await es_async.index(
                index="documents",
                id=document_id,
                document=document_data,
            )

        raise

    return {"message": f"Document {document_id} deleted"}