#!/bin/bash

echo "Waiting for MongoDB to start..."
sleep 5 # MongoDB'nin hazır olması için bekleme süresi


# MongoDB bilgileri
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_DB=my_database
MONGO_COLLECTION=hardware_faq
MONGO_INIT_FILE=/init-mongo/sample_data.json

echo "MongoDB: Mevcut koleksiyon kontrol ediliyor ve siliniyor..."

# Koleksiyonu sil (mevcutsa)
mongosh --host $MONGO_HOST --port $MONGO_PORT <<EOF
use $MONGO_DB
db.$MONGO_COLLECTION.drop()
EOF

echo "MongoDB: Koleksiyon silindi."

# Yeni verileri ekle
echo "MongoDB: Yeni veriler ekleniyor..."
mongoimport --host $MONGO_HOST --port $MONGO_PORT --db $MONGO_DB --collection $MONGO_COLLECTION --file $MONGO_INIT_FILE --jsonArray

echo "MongoDB: Veri ekleme tamamlandı."