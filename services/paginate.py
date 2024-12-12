from utils.transform import objectid_to_str


class PaginationService:
    @staticmethod
    async def get_paginated_data(collection, limit: int = 100, page: int = 1):
        skip = (page - 1) * limit
        total_count = await collection.count_documents({})
        total_pages = (total_count + limit - 1) // limit

        documents = objectid_to_str(await collection.find().skip(skip).limit(limit).to_list(length=limit))

        return {
            "data": documents,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
        }

