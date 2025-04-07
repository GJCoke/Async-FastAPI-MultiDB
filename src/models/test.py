from sqlmodel import Field

from src.crud.base import BaseSQLModelCRUD
from src.models.base import Document, SQLModel


class Test(SQLModel, table=True):
    __tablename__ = "test_affiliation"

    name: str = Field(..., unique=True)
    desc_test: str = ""


class TestDocument(Document):
    name: str = "test"
    desc_test: str = "test desc"

    class Settings:
        collection = "test_affiliation"


testCrud = BaseSQLModelCRUD[Test, Test, Test](Test)
