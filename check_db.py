import chromadb

def inspect_database():
    print("🔍 Inspecting ChromaDB...")
    
    client = chromadb.PersistentClient(path="./chroma_data")
    
    # 👇 Updated to match your exact collection name
    collection_name = "devmind_codebase" 
    
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        print(f"\n✅ Collection '{collection_name}' found!")
        print(f"📊 Total code chunks ingested: {count}\n")
        
        if count > 0:
            results = collection.peek(limit=5)
            print("📁 Sample of ingested files:")
            for meta in (results.get("metadatas") or []):
                print(f"  - {meta.get('file_path', 'Unknown File')}")
        else:
            print("⚠️ The database is completely empty!")
            
    except Exception as e:
        print(f"\n❌ Error accessing database: {str(e)}")

if __name__ == "__main__":
    inspect_database()