# The stand-in demo in one command, no Python or Exasol needed on the host:
#   docker build -t receipts . && docker run --rm -p 8000:8000 receipts
# then open http://127.0.0.1:8000. It runs in lab mode on synthetic data, on the DuckDB stand-in.
# For Exasol, run Receipts on the host next to Exasol Personal instead (see docs/RUN_GUIDE.md).
#
# A public demo (rate limits and automatic reset, see docs/DEPLOY_DEMO.md):
#   docker build --target public -t receipts-public . && docker run --rm -p 8080:8080 receipts-public
FROM python:3.12-slim AS local

WORKDIR /app
COPY pyproject.toml README.md LICENSE receipts.yaml ./
COPY receipts ./receipts
COPY web ./web
COPY samples ./samples
# editable, so the package finds web/ and samples/ next to it, as in a clone
RUN pip install --no-cache-dir -e .

ENV RECEIPTS_BACKEND=duckdb RECEIPTS_NO_BROWSER=1 PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["receipts", "demo", "--lab", "--host", "0.0.0.0", "--port", "8000"]

FROM local AS public
# No API key may reach a public demo: explanations stay on the deterministic template.
ENV RECEIPTS_PUBLIC_DEMO=1 RECEIPTS_DEMO_PER_MIN=6 RECEIPTS_DEMO_GLOBAL_PER_MIN=30 RECEIPTS_DEMO_RESET_MIN=10 \
    ANTHROPIC_API_KEY=
RUN useradd --create-home demo && chown -R demo /app
USER demo
EXPOSE 8080
CMD ["receipts", "demo", "--lab", "--host", "0.0.0.0", "--port", "8080"]

# The default target (a plain `docker build`) is the local demo above.
FROM local
