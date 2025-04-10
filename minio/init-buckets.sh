#!/bin/sh

while ! nc -z minio 9000; do
    echo "MinIo is not available yet. Retrying in 1 seconds..."
    sleep 1
done

echo "MinIO is up. Initializing buckets..."

mc alias set myminio http://minio:9000 minioadmin minioadmin

for bucket in mylogs flink-data
do
    mc mb myminio/"$bucket" || true
    mc anonymous set download myminio/"$bucket"
done

exit 0
