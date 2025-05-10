"""
Author  : Coke
Date    : 2025-05-10
"""

from src.models.base import Document


class Counter(Document):
    """
    MongoDB model for implementing per-collection and conditional counters.

    Examples:
        next_order_id = await get_next_sequence(
            collection_name="orders",
            conditions={"shop_id": "shop_456"}
        )
    """

    seq: int = 0
    collection_name: str
    conditions: dict[str, str] | None = None

    class Settings:
        name = "counter"
        indexes = [[("collection_name", 1)]]


async def get_next_sequence(collection_name: str, conditions: dict) -> int:
    """
    Get the next value in an auto-incrementing sequence for specified conditions (atomic operation)

    Args:
        collection_name (str): Target collection name (e.g., 'datasets', 'jobs')
        conditions (dict): Condition dictionary (e.g., {'space_id': '123'})

    Returns:
        int: The next sequence value after incrementing
    """

    counter = await Counter.get_motor_collection().find_one_and_update(
        filter={"collection_name": collection_name, "conditions": conditions},
        update={"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )

    return counter["seq"]


async def delete_sequence(collection_name: str, conditions: dict) -> None:
    """
    Delete a sequence counter matching specified conditions

    Args:
        collection_name (str): Target collection name
        conditions (dict): Condition dictionary
    """

    counter = await Counter.find_one(Counter.collection_name == collection_name, Counter.conditions == conditions)
    if counter:
        await counter.delete()  # type: ignore
