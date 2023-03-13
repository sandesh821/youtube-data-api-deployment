FROM python:3.6-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install google-api-python-client 
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]