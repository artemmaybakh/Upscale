# Используем официальный Python-образ
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы проекта
WORKDIR /app
COPY . /app

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска
CMD ["python", "main.py"]
