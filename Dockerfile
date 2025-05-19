# Используем официальный лёгкий образ Python 3.11
FROM python:3.11-slim

# Не буферизовать вывод — чтобы логи сразу шли в Railway
ENV PYTHONUNBUFFERED=1

# Рабочая папка
WORKDIR /app

# Сначала копируем только зависимости, чтобы кэшировать слой
COPY requirements.txt .

# Устанавливаем зависимости без кэша
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Точка входа — запускаем бота
CMD ["python", "bot.py"]
