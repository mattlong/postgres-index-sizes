import random
import uuid
import copy
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import create_engine
from sqlalchemy import types
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID


CONNECTION_STRING = open('psql_conn.txt').read().strip()
metadata = MetaData()
BaseModel = declarative_base()
engine = create_engine(CONNECTION_STRING, echo=False)
Session = sessionmaker(bind=engine)


class Model(BaseModel):
    __tablename__ = 'model'

    id = Column(types.Integer, autoincrement=True, primary_key=True)

    unique_string = Column(types.String(36), nullable=False, unique=True)
    unique_uuid = Column(UUID, nullable=False, unique=True)

    nonunique_string_100 = Column(types.String(36), nullable=False)
    nonunique_uuid_100 = Column(UUID, nullable=False)

    nonunique_string_10 = Column(types.String(36), nullable=False)
    nonunique_uuid_10 = Column(UUID, nullable=False)


    __table_args__ = (
        Index('model_nonunique_string_100_key',     nonunique_string_100, unique=False),
        Index('model_nonunique_uuid_100_key',       nonunique_uuid_100, unique=False),

        Index('model_nonunique_string_10_key',      nonunique_string_10, unique=False),
        Index('model_nonunique_uuid_10_key',        nonunique_uuid_10, unique=False),

        Index('model_nonunique_string_100_unique_string_key',        nonunique_string_100, unique_string, unique=True),
        Index('model_nonunique_uuid_100_unique_uuid_key',        nonunique_uuid_100, unique_uuid, unique=True),
    )


def create_tables():
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)


def bulk_insert_rows(count):
    row_template = {
        'id': None,
        'uid_string': None,
        'uid_uuid': None,
    }

    nonunique_10 = [str(uuid.uuid4()) for _ in range(10)]
    nonunique_100 = [str(uuid.uuid4()) for _ in range(100)]

    session = Session()

    n1 = count
    CHUNK_SIZE = 1000
    while n1 > 0:
        rows = []
        for i in xrange(min(CHUNK_SIZE, n1)):
            row = copy.deepcopy(row_template)
            row['unique_string'] = \
            row['unique_uuid'] = str(uuid.uuid4())

            row['nonunique_string_10'] = \
            row['nonunique_uuid_10'] = random.choice(nonunique_10)

            row['nonunique_string_100'] = \
            row['nonunique_uuid_100'] = random.choice(nonunique_100)

            rows.append(row)

        session.bulk_insert_mappings(
            Model,
            rows
        )
        n1 -= CHUNK_SIZE

    session.commit()


def main():
    count = 1000000

    print('Creating and purging table...')
    create_tables()
    print('Inserting %d rows. This could take a while...' % count)
    bulk_insert_rows(count)
    print('Done')


if __name__ == '__main__':
    main()
