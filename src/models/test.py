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


if __name__ == "__main__":
    from sqlmodel import Session, SQLModel, create_engine  # type: ignore

    sqlite_file_name = "root:123456@127.0.0.1:33306/client"
    sqlite_url = f"mysql+mysqlconnector://{sqlite_file_name}"

    engine = create_engine(sqlite_url, echo=True)

    with Session(engine) as session:
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)

        def affiliation(session: Session) -> None:
            company_structure = dict(
                name="霸天集团",
                children=[
                    dict(
                        name="机械部队", children=[dict(name="机甲小队"), dict(name="机器人兵团"), dict(name="战车队")]
                    ),
                    dict(name="战略部", children=[dict(name="情报分析组"), dict(name="指挥决策组")]),
                    dict(name="科技部", children=[dict(name="高能武器组"), dict(name="人工智能组")]),
                    dict(name="资源部", children=[dict(name="矿产采集组"), dict(name="能源管理组")]),
                    dict(name="后勤部", children=[dict(name="物资供应组"), dict(name="人员调度组")]),
                ],
            )

            _corporation = Test(name=company_structure["name"])  # type: ignore
            session.add(_corporation)
            session.commit()

            def recursion(children: list) -> None:
                for item in children:
                    _item = Test(name=item.get("name"))
                    session.add(_item)
                    session.commit()

                    if item.get("children"):
                        recursion(item["children"])  # type: ignore

            recursion(company_structure["children"])  # type: ignore

        affiliation(session)
