# The stand-in demo in one command, no Python or Exasol needed on the host:
#   docker build -t receipts . && docker run --rm -p 8000:8000 receipts
# then open http://127.0.0.1:8000. It runs in lab mode on synthetic data, on the DuckDB stand-in.
# For Exasol, run Receipts on the host next to Exasol Personal instead (see docs/RUN_GUIDE.md).
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY receipts ./receipts
COPY web ./web
COPY samples ./samples
# editable, so the package finds web/ and samples/ next to it, as in a clone
RUN pip install --no-cache-dir -e .

ENV RECEIPTS_BACKEND=duckdb RECEIPTS_NO_BROWSER=1 PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["receipts", "demo", "--lab", "--host", "0.0.0.0", "--port", "8000"]
