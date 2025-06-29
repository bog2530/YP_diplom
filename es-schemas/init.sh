#!/bin/bash
while ! curl -s "elasticsearch:9200" > /dev/null; do
    echo "Ожидание доступности elastic..."
    sleep 5
done

if curl -s -f "http://elasticsearch:9200/movies" > /dev/null; then
    echo "Индекс movies уже существует"
else
    echo "Создаем индекс movies"
    curl -XPUT "http://elasticsearch:9200/movies" -H "Content-Type: application/json" -d @/data/movies.json
fi

if curl -s -f "http://elasticsearch:9200/genres" > /dev/null; then
    echo "Индекс genres уже существует"
else
    echo "Создаем индекс genres"
    curl -XPUT "http://elasticsearch:9200/genres" -H "Content-Type: application/json" -d @/data/genres.json
fi

if curl -s -f "http://elasticsearch:9200/persons" > /dev/null; then
    echo "Индекс persons уже существует"
else
    echo "Создаем индекс persons"
    curl -XPUT "http://elasticsearch:9200/persons" -H "Content-Type: application/json" -d @/data/persons.json
fi