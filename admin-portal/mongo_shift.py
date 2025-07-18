from pymongo import MongoClient
import sys

def clone_mongo_data(source_uri, target_uri, source_db_name, target_db_name):
    """
    Clones data from one MongoDB URI to another.

    Args:
        source_uri (str): MongoDB URI of the source database.
        target_uri (str): MongoDB URI of the target database.
        source_db_name (str): Name of the source database.
        target_db_name (str): Name of the target database.
    """
    try:
        # Connect to the source and target MongoDB instances
        source_client = MongoClient(source_uri)
        target_client = MongoClient(target_uri)

        # Access the source and target databases
        source_db = source_client[source_db_name]
        target_db = target_client[target_db_name]

        # Iterate through all collections in the source database
        for collection_name in source_db.list_collection_names():
            print(f"Cloning collection: {collection_name}")

            # Access the source and target collections
            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]

            # Fetch all documents from the source collection
            documents = list(source_collection.find())

            if documents:
                for doc in documents:
                    # Remove the '_id' field to avoid duplicate key errors on ObjectId
                    doc.pop("_id", None)

                    # Check for duplicates in the target collection
                    unique_field = "email"  # Change this to the unique field for the collection
                    if unique_field in doc:
                        existing_doc = target_collection.find_one({unique_field: doc[unique_field]})
                        if existing_doc:
                            print(f"Skipping duplicate document with {unique_field}: {doc[unique_field]}")
                            continue

                    # Insert the document into the target collection
                    target_collection.insert_one(doc)

                print(f"Cloned {len(documents)} documents from {collection_name}")
            else:
                print(f"No documents found in {collection_name}")

        print("Data cloning completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connections
        source_client.close()
        target_client.close()


if __name__ == "__main__":
    # Example usage
    source_uri = "mongodb+srv://jsrihariseshbe24:OkxQQv04JIEoarF6@obscura.uhjj2ie.mongodb.net/OBSCURA?retryWrites=true&w=majority"
    target_uri = "mongodb+srv://jsrihariseshbe24:xclkVC1buP9wpdGw@skillmate.v34gjcg.mongodb.net/skillmate?retryWrites=true&w=majority"
    source_db_name = "obscura"
    target_db_name = "obscura"

    clone_mongo_data(source_uri, target_uri, source_db_name, target_db_name)