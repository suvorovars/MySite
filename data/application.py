import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Application(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'application'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    viewed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    feedback = sqlalchemy.Column(sqlalchemy.String, nullable=False)