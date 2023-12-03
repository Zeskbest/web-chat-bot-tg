import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = 'sqlite:///./sqlite3.db'

Base = declarative_base()
engine = sa.create_engine(DATABASE_URL)
sess = sessionmaker(autocommit=False, autoflush=True, bind=engine)()


class Person(Base):
    __tablename__ = 'person'
    id = sa.Column(sa.Integer, primary_key=True)
    tg_user_id = sa.Column(sa.BigInteger)
    tg_chat_id = sa.Column(sa.BigInteger)


Base.metadata.create_all(bind=engine)


def get_person(tg_user_id: int, tg_chat_id: int) -> Person:
    person = sess.query(Person).filter_by(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id).one_or_none()
    if person is None:
        person = Person(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id)
        sess.add(person)
        sess.commit()
    return person
