from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.db.mongodb import get_mongo_collection

DocumentType = TypeVar("DocumentType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class MongoRepository(Generic[DocumentType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class for MongoDB documents."""

    def __init__(self, collection_name: str, document_class: type[DocumentType]):
        self.collection_name = collection_name
        self.document_class = document_class

    def _get_collection(self) -> AsyncIOMotorCollection:
        """Get MongoDB collection."""
        return get_mongo_collection(self.collection_name)

    def _convert_id(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Convert ObjectId to string in document."""
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return doc

    async def get(self, id: str) -> DocumentType | None:
        """Get a single document by ID."""
        collection = self._get_collection()
        doc = await collection.find_one({"_id": ObjectId(id)})
        if doc:
            doc = self._convert_id(doc)
            return self.document_class(**doc)
        return None

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[DocumentType]:
        """Get multiple documents with pagination."""
        collection = self._get_collection()
        filter_dict = filter_dict or {}

        cursor = collection.find(filter_dict).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        result = []
        for doc in docs:
            doc = self._convert_id(doc)
            result.append(self.document_class(**doc))

        return result

    async def create(self, *, obj_in: CreateSchemaType) -> DocumentType:
        """Create a new document."""
        collection = self._get_collection()
        obj_data = (
            obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
        )

        result = await collection.insert_one(obj_data)
        doc = await collection.find_one({"_id": result.inserted_id})
        doc = self._convert_id(doc)

        return self.document_class(**doc)

    async def update(self, *, id: str, obj_in: UpdateSchemaType) -> DocumentType | None:
        """Update an existing document."""
        collection = self._get_collection()

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else obj_in.dict(exclude_unset=True)
            )

        await collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        doc = await collection.find_one({"_id": ObjectId(id)})
        if doc:
            doc = self._convert_id(doc)
            return self.document_class(**doc)
        return None

    async def remove(self, *, id: str) -> bool:
        """Delete a document by ID."""
        collection = self._get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def get_by_field(self, *, field_name: str, value: Any) -> DocumentType | None:
        """Get a document by a specific field."""
        collection = self._get_collection()
        doc = await collection.find_one({field_name: value})
        if doc:
            doc = self._convert_id(doc)
            return self.document_class(**doc)
        return None

    async def exists(self, *, id: str) -> bool:
        """Check if a document exists by ID."""
        collection = self._get_collection()
        doc = await collection.find_one({"_id": ObjectId(id)})
        return doc is not None

    async def count(self, *, filter_dict: dict[str, Any] | None = None) -> int:
        """Count documents matching filter."""
        collection = self._get_collection()
        filter_dict = filter_dict or {}
        return await collection.count_documents(filter_dict)
