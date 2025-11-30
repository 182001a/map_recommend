# 1. ベースイメージ（Python 3.12）
FROM python:3.12-slim

# 2. Python の基本設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. コンテナ内の作業ディレクトリ
WORKDIR /code

# 4. OSレベルの必要パッケージ(PostgreSQL, build tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 5. Python依存パッケージをインストール
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# 6. アプリコードをコンテナにコピー
COPY . /code/

# 7. コンテナが公開するポート
EXPOSE 8000

# 8. コンテナ起動時に実行するコマンド（開発用）
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
