# FastAPI Currency Exchange

---

## Стек

---


* **FastAPI** - основной web-фреймворк
* **PostgreSQL** - основная база данных
* **Pydantic** - валидация данных
* **Pydantic-settings** управление конфигураций через переменные окружения
* **SQLAlchemy** - ORM для взаимосвязи с БД
* **Alembic** - миграции схем БД

---

## Описание

---

### Авторизация

Для доступа к API используется авторизация через JWT токен. Логин осуществляется через эндпоинт ```/token```.


### Основные функции

* ```/currency/exchange```

**Метод**: ```POST```

**Описание**: Конвертация валюты из одной в другую. Параметры передаются в теле запроса.

**Пример запроса**:

```
{
  "from_currency": "USD",
  "to_currency": ["EUR", "GBP"]
}
```
 
**Пример Ответа**

```
{
  "User": "john_doe",
  "Email": "john@example.com",
  "currency_data": {
    "currency_from": "EUR",
    "currency_to": {
      "RUB": 92.641045
    }
  }
}
```

* ```/currency/list```

**Метод**: ```GET```

**Описание**: Получение списка всех доступных валют.

**Пример ответа**:

```
{
  "USD": 1.132945,
  "EUR": 1,
  "GBP": 0.849692,
  "RUB": 92.641045
}
```

---

## Развертывание

---

1. **Установить Python 3.11+**

    Убедитесь, что у вас установлен Python 3.11 или более новая версия. Если нет, скачайте и установите его с официального сайта: [Python.org](https://www.python.org/).

2. **Создать виртуальное окружение**

Для создания виртуального окружения выполните команду:

```bash
python -m venv <название виртуального окружения>
```

Замените ```<название виртуального окружения>``` на желаемое имя для вашего виртуального окружения. 

3. **Активировать виртуальное окружение**

Windows

```
<название виртуального окружения>\Scripts\Activate
```

Linux/macOS

```
source <название виртуального окружения>/bin/activate
```

4. **Установить зависимости**

```
pip install -r requirements.txt
```

5. **PosgreSQL DB**

Запустите SQL Shell (psql) и создайте свою базу данных, затем введите данные бд в ```.env```, если у вас уже есть база данных, просто добавьте данные в переменные окружения

6. **Настроить переменные окружения**

    Создайте файл ```.env```

7. **Применить миграции**

```
alembic upgrade head
```

8. **Запустить сервер**

```
uvicorn main:app --reload
```