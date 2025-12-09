from database import Base, SessionLocal, engine

from models import Address, User


def create_tables():
    Base.metadata.create_all(bind=engine)


def seed_data():
    db = SessionLocal()
    if db.query(User).count() == 0:
        users = [
            User(name="spongebob", fullname="Spongebob Squarepants"),
            User(name="sandy", fullname="Sandy Cheeks"),
            User(name="patrick", fullname="Patrick Star"),
        ]
        addresses = [
            Address(email_address="spongebob@sqlalchemy.org"),
            Address(email_address="sandy@sqlalchemy.org"),
            Address(email_address="patrick@sqlalchemy.org"),
        ]
        users[0].addresses.append(addresses[0])
        users[1].addresses.append(addresses[1])
        users[2].addresses.append(addresses[2])

        db.add_all(users)
        db.commit()
    db.close()


def init_db():
    create_tables()
    seed_data()
