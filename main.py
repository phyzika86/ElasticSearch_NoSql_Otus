from opensearchpy import OpenSearch, exceptions
from datetime import datetime

# Подключение к OpenSearch
client = OpenSearch(
    hosts=["http://localhost:9200"],
    http_auth=None,  # Если security отключен
    use_ssl=False
)
print(client.info())

# Проверка подключения
if client.ping():
    print("Успешное подключение к Elasticsearch!")
else:
    print("Не удалось подключиться к Elasticsearch")

client.indices.delete(index='_all')

# Создание индекса
client.indices.create(index="test-index")

# Добавление документа
client.index(
    index="test-index",
    body={"title": "Документ в OpenSearch"}
)


# Создание индекса
index_body = {
  "mappings": {
    "properties": {
      "text": {"type": "text"},
      "created_at": {"type": "date"}
    }
  }
}
client.indices.create(index="text_index_2", body=index_body)

# Добавление документов
docs = [
  {"text": "Тест для домашки отуса курса NoSQL", "created_at": datetime.now()},
  {"text": "Создаю документы без шаблона", "created_at": datetime.now()},
  {"text": "Будет 4 документа", "created_at": datetime.now()},
  {"text_error": "Похоже на mongadb", "created_at": datetime.now()}
]

for doc in docs:
  client.index(index="text_index_2", body=doc)

# Проверка
print(client.search(index="text_index_2", body={"query": {"match_all": {}}}))


# Создание индекса с strict-маппингом
def create_index(index_name):
    mapping = {
        "settings": {
            "analysis": {
                "filter": {
                    "russian_stop": {
                        "type": "stop",
                        "stopwords": "_russian_"
                    },
                    "russian_stemmer": {
                        "type": "stemmer",
                        "language": "russian"
                    }
                },
                "analyzer": {
                    "russian": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "russian_stop",
                            "russian_stemmer"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "text": {
                    "type": "text",
                    "analyzer": "russian",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "created_at": {"type": "date"}
            }
        }
    }

    try:
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body=mapping)
            print(f"Индекс {index_name} создан с strict-маппингом")
        else:
            print(f"Индекс {index_name} уже существует")
    except exceptions.RequestError as e:
        print(f"Ошибка создания индекса: {e}")


create_index("otus_homework")

# Добавление документов
docs = [
  {"text": "моя мама мыла посуду а кот жевал сосиски", "created_at": datetime.now()},
  {"text": "рама была отмыта и вылизана котом", "created_at": datetime.now()},
  {"text": "мама мыла раму", "created_at": datetime.now()},
  {"text_error": "Похоже на mongadb", "created_at": datetime.now()}
]

for doc in docs:
    try:
        client.index(index="otus_homework", body=doc)
    except Exception as e:
        print('При создании документа произошла ошибка:', e)


client.indices.refresh(index="otus_homework")  # Если не сделать refresh, то документы появятся не сразу
# Проверка
res = client.search(index="otus_homework", body={"query": {"match_all": {}}})
print("Количество найденных документов:", res['hits']['total']['value'])
print(res)
