FROM python:3.13
WORKDIR /dennis-concordance-web-app-project
COPY requierments.txt requierments.txt
RUN pip install -r requierments.txt
COPY . .

WORKDIR /dennis-concordance-web-app-project/backend
CMD ["python",  "app.py"]
