FROM ******-********.region.vtb.ru:5000/library/astra/ub117-python37:1.7.6

ARG COMMIT_SHA
LABEL commit_sha=${COMMIT_SHA}

ARG API_USER_ARG
ARG API_PASSWORD_ARG
ARG MAIL_PASSWORD_ARG

ENV API_USER=$API_USER_ARG
ENV API_PASSWORD=$API_PASSWORD_ARG
ENV MAIL_PASSWORD=$MAIL_PASSWORD_ARG

RUN rm /etc/apt/sources.list && \
    echo "deb http://**.***.***.**/stages_astra/1.7.6/repository-base 1.7_x86-64 main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://**.***.***.**/stages_astra/1.7.6/repository-extended 1.7_x86-64 main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && apt-get install python3-yaml python3-requests -y

WORKDIR /app
COPY . .
CMD ["python3", "main.py"]
