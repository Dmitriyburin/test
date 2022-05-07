import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship

association_table = sqlalchemy.Table('association_table', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('jobs', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('jobs.id')),
                                     sqlalchemy.Column('category', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('category.id'))
                                     )


class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    hazard = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    jobs = relationship("Jobs",
                        secondary="association_table",
                        back_populates="categories")

    def __repr__(self):
        return str(self.hazard)
