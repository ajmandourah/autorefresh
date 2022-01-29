
FROM python:3.9.9-slim-bullseye
COPY . /data/.
WORKDIR /data
VOLUME /data/autorefresh
RUN pip3 install -r requirements.txt
EXPOSE 6969
CMD ["python","main.py"]
