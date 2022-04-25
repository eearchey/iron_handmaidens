FROM python:3
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD python iron_handmaidens/manage.py runserver
WORKDIR /usr/src/app

# Internal port to expose
# EXPOSE 8000
