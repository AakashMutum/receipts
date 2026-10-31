# Data manifest

Public data used by the real-data backtests. None of it is committed: the files live outside the repository (on the
author's machine in `D:\Hackathon\data`), and the scripts download them or say where to put them. Dates are the
download dates in IST.

## UCI Online Retail II with ECB reference rates

Used by [`scripts/backtest_retail.py`](../scripts/backtest_retail.py), report
[`samples/exasol/real_backtest_retail.md`](../samples/exasol/real_backtest_retail.md).

| File | Bytes | SHA-256 | Source | Downloaded |
|---|---|---|---|---|
| online_retail_ii.zip | 45,622,418 | `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb` | https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip | 2026-10-30 |
| eurofxref-hist.zip | 642,255 | `73db21584dd46cebf5cd6df75ebb6de7afcdeebff52f54d5046ca8e459c0fbb3` | https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip | 2026-10-30 |

* UCI: "This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license."
  Chen, D. (2012), Online Retail II, UCI Machine Learning Repository, https://doi.org/10.24432/C5CG6D.
* ECB: "The reference rates are published for information purposes only." Source: European Central Bank.
