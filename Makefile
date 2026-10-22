# Receipts. Run `make help`.
PY ?= python3
PORT ?= 8000
# optional incoming day, YYYY-MM-DD; empty means yesterday in India
DAY ?=
DAYARG = $(if $(DAY),--day $(DAY))

.PHONY: help install init demo serve eval eval-quick judge-check test doctor sample export-sql exasol-init clean

help:
	@echo "make install       install Receipts and its dependencies"
	@echo "make init          generate synthetic data and build the database (Exasol if EXA_DSN is set)"
	@echo "make demo          build if needed, start and open the command center on http://127.0.0.1:$(PORT) (DAY=YYYY-MM-DD pins the day)"
	@echo "make judge-check   reproduce the headline claims. No Exasol, no API key needed"
	@echo "make eval          full scored evaluation, writes samples/eval_report.md"
	@echo "make test          run the test suite, including the Exasol SQL path"
	@echo "make doctor        check the setup, and on Exasol check reserved words and the UDF"
	@echo "make exasol-init   build everything inside a local Exasol Personal"

install:
	$(PY) -m pip install -e ".[dev]"

init:
	receipts init $(DAYARG)

demo:
	receipts demo --port $(PORT) $(DAYARG)

serve:
	receipts serve --port $(PORT) $(DAYARG)

eval:
	receipts eval

eval-quick:
	receipts eval --quick

judge-check:
	receipts judge-check

test:
	$(PY) -m pytest -q

doctor:
	receipts doctor

sample:
	receipts sample

export-sql:
	receipts export-sql

# Exasol Personal: `exasol install local`, `exasol slc install python3`, then:
exasol-init:
	RECEIPTS_BACKEND=exasol EXA_DSN=$${EXA_DSN:-localhost:8563} receipts init $(DAYARG)
	RECEIPTS_BACKEND=exasol EXA_DSN=$${EXA_DSN:-localhost:8563} receipts doctor

clean:
	rm -rf data/*.csv data/*.duckdb data/manifest.json .pytest_cache
