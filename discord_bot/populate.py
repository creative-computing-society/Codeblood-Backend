import database
import asyncio
import json


async def main():
    # 1) Initialize your DB and collections
    await database.init_db()
    await database.init_teams()

    # 2) Grab the collection
    teams = database.teams
    assert teams is not None, "Collection not initialized"

    # 3) Load your JSON data
    with open("populate.json") as f:
        data = json.load(f)  # should be a list of dicts

    # 4) Bulk insert
    result = await teams.insert_many(data)
    print(f"Inserted {len(result.inserted_ids)} documents.")


if __name__ == "__main__":
    asyncio.run(main())
