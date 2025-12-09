from sqlalchemy.orm import Session

import cruds


def get_users(db: Session):
    users = cruds.get_all_users(db)
    return [
        {
            "id": u.id,
            "name": u.name,
            "fullname": u.fullname,
            "addresses": [a.email_address for a in u.addresses],
        }
        for u in users
    ]


def get_user(db: Session, user_id: int):
    user = cruds.get_user_by_id(db, user_id)
    if not user:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "fullname": user.fullname,
        "addresses": [a.email_address for a in user.addresses],
    }


def get_addresses(db: Session):
    addresses = cruds.get_all_addresses(db)
    return [
        {
            "id": a.id,
            "email_address": a.email_address,
            "users": [u.name for u in a.users],
        }
        for a in addresses
    ]
