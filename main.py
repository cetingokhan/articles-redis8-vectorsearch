import openai
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_openai import OpenAIEmbeddings
from redis import Redis
from pymongo import MongoClient
from langchain_core.documents import Document


OPENAI_API_KEY = "OPENAI_API_KEY"


REDIS_HOST = "localhost"
REDIS_PORT = "6379"
VECTOR_DIM = 1536 
INDEX_NAME = "faqs_vector_index2"
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "my_database"
COLLECTION_NAME = "hardware_faq"



embeddings = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small"
)

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) #, password="redis-stack"

config = RedisConfig(
    index_name=INDEX_NAME,
    redis_client=redis_client,
    key_prefix="vector:faq:",
    storage_type="json",
        metadata_schema=[
        {"name": "category", "type": "tag"},
        {"name": "fid", "type": "numeric"},
    ],
    )   
vector_store = RedisVectorStore(embeddings, config=config)


def fetch_documents_from_mongo():
    client = MongoClient(MONGO_URI)
    collection = client[DATABASE_NAME][COLLECTION_NAME]
    documents = list(collection.find())
    client.close()
    print("Dökümanlar mongodb den getirildi!")
    return documents


def add_documents_to_vector_store(vector_store, documents):
    
    print(vector_store)
    
    docs = []
    for doc in documents:
        docs.append(Document(
            page_content=f"{doc['question']}\n{doc['answer']}",
            metadata={
                "id":str(doc["faq_id"]),
                "category":doc["category"],
                "fid":doc["faq_id"],
            }
        ))
    vector_store.add_documents(docs)
    print("Belgeler VectorStore'a eklendi.")


def semantic_search(vector_store, query, top_k=3):
    results = vector_store.similarity_search_with_score(query, k=top_k)
    print("Arama sonuçları:")
    for i, (doc, score) in enumerate(results):
        print(f"{i + 1}. {doc.page_content}\n{doc.metadata['category']}\n(Score: {(1-score)*100})")



if __name__ == "__main__":
    
    indexed_record_check = redis_client.execute_command("FT.SEARCH",INDEX_NAME,"*","LIMIT",0,1)
    if indexed_record_check[0]==0:
        documents = fetch_documents_from_mongo()
        add_documents_to_vector_store(vector_store, documents)


    print("Komut girin (çıkmak için 'quit' yazın):")
    while True:
        user_input = input("> ")
        if user_input.lower() == "quit":
            print("Çıkılıyor...")
            break
        else:
            semantic_search(vector_store, user_input)
