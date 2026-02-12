FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask pandas joblib scikit-learn
EXPOSE 5000
CMD ["python", "app.py"]
