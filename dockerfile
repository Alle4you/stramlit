#app/Dockerfile

FROM python:3.11.1

WORKDIR /stramlit

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

ARG GITHUB_TOKEN
RUN git clone https://alle4you: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@github.com/Alle4you/stramlit.git .


RUN git clone https://github.com/


RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--theme.base=dark"]