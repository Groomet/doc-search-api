import csv
import ast
from datetime import datetime
from sqlalchemy import select

from app.models.document import Document
from app.db.session import SessionLocal


def main():
    with SessionLocal.begin() as session:
        stmt = select(Document.id).limit(1)
        existing_id = session.scalar(stmt)
        
        if existing_id is not None:
            print("Таблица уже содержит документы")
            return
        
        with open("data/posts.csv", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                rubrics = ast.literal_eval(row["rubrics"])
                created_date = datetime.fromisoformat(row["created_date"])
                
                document = Document(
                    text=row["text"],
                    created_date=created_date,
                    rubrics=rubrics
                )
                
                session.add(document)
                count += 1
    print(f"Успешно загружено документов: {count}")
    
    
if __name__ == "__main__":
    main()