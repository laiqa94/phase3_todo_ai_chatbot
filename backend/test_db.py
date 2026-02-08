#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from sqlmodel import Session, create_engine, select
from app.core.config import settings
from app.models.task import Task

print('Database URL:', settings.DATABASE_URL, file=sys.stderr)
engine = create_engine(settings.DATABASE_URL)
print('Engine created', file=sys.stderr)
try:
    with Session(engine) as session:
        print('Session created', file=sys.stderr)
        statement = select(Task).limit(5)
        results = session.exec(statement).all()
        print('Results:', results, file=sys.stderr)
except Exception as e:
    print('Error:', e, file=sys.stderr)
    import traceback
    traceback.print_exc()
