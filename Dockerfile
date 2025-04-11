# Используем официальный Python
FROM python:3.11-slim-bullseye

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /backend

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем остальной код проекта
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
