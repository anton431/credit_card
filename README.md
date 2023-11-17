# Кредитная карта

## Описание проекта
Проект разбит на три микросервиса: сервис авторизации, основной сервис со всей логикой, сервис верификации, для проверки соответствия фото и документа.

## Stack

>Language: __Python 3__<br>
Web framework: __FastAPI__<br>
Database: __PostgreSQL__<br>

Другое: Docker, SQLAlchemy, pytest, Kubernetes, Grafana, Kafka

## API Views

><p>/api/verify — преверяет селфи и фото документа, если лица совпали, то лимит на карте увеличивается до 100 000;<br></p>
><p>/api/balance/ — показывает баланс;<br></p>
><p>/api/balance/history — история операций;<br></p>
><p>/api/withdrawal — списать средства;<br></p>
><p>/api/deposit — положить средства;<br></p>

## Информация о доступе к документации OpenAPI (Swagger)
> - <p>/docs/ — Документация;<br>
