name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: finsight
          POSTGRES_PASSWORD: finsight
          POSTGRES_DB: finsight_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10

    env:
      POSTGRES_USER: finsight
      POSTGRES_PASSWORD: finsight
      POSTGRES_HOST: localhost
      POSTGRES_PORT: 5432
      GOOGLE_API_KEY: not-used-in-tests

    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest -v
