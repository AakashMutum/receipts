"""Reproducible synthetic data for a fictional Indian fintech marketplace.

Everything here is synthetic. The shapes are chosen to be realistic enough for
the faults to behave like they do in production: evening-heavy shopping in IST,
a small international (USD) slice converted with a daily FX feed, a few payment
gateways of very different size, and a low background rate of payment retries
(a failed attempt and a captured attempt sharing one PAYMENT_ID).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

from .model import DEFAULT_HISTORY_DAYS, INCOMING_DAY

CITIES = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]
CITY_W = [0.19, 0.18, 0.17, 0.11, 0.11, 0.09, 0.08, 0.07]
CATEGORIES = {  # code: (name, order share, mean ticket in INR)
    "ELEC": ("Electronics", 0.15, 3800.0),
    "FASH": ("Fashion", 0.21, 1800.0),
    "GROC": ("Grocery", 0.27, 750.0),
    "HOME": ("Home", 0.13, 2600.0),
    "BEAU": ("Beauty", 0.14, 900.0),
    "BOOK": ("Books", 0.10, 450.0),
}
CHANNELS = ["APP", "WEB", "POS"]
CHANNEL_W = [0.62, 0.30, 0.08]
DOMESTIC_GW = ["GW_A", "GW_B", "GW_C"]
DOMESTIC_GW_W = [0.55, 0.40, 0.05]
USD_SHARE = 0.09
TIERS = ["GOLD", "SILVER", "BRONZE"]
TIER_W = [0.15, 0.35, 0.50]
SIGMA = 0.6
BACKGROUND_RETRY = 0.006


@dataclass
class GenConfig:
    seed: int = 7
    orders_per_day: int = 20000
    history_days: int = DEFAULT_HISTORY_DAYS
    incoming_day: date = INCOMING_DAY
    n_merchants: int = 1500
    festival_uplift: float = 0.22


def _ts(arr_seconds: np.ndarray) -> list[str]:
    epoch = datetime(1970, 1, 1)
    return [(epoch + timedelta(seconds=int(s))).strftime("%Y-%m-%d %H:%M:%S") + ".000" for s in arr_seconds]


def _ist_tod_seconds(rng, n, evening_weight=0.50):
    """Seconds after IST midnight. Two peaks, lunch and evening, plus a flat floor."""
    lunch_w = 0.35 * (1 - evening_weight) / 0.5
    comp = rng.choice(3, size=n, p=[lunch_w, evening_weight, 1 - lunch_w - evening_weight])
    hours = np.where(comp == 0, rng.normal(13.0, 2.5, n),
                     np.where(comp == 1, rng.normal(20.5, 2.0, n), rng.uniform(0, 24, n)))
    hours = np.mod(hours, 24.0)
    return (hours * 3600).astype(np.int64)


class Generator:
    def __init__(self, cfg: GenConfig):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.next_order = 1_000_000
        self.next_payment = 50_000_000
        self.days = [cfg.incoming_day - timedelta(days=cfg.history_days - i) for i in range(cfg.history_days)]
        self.days.append(cfg.incoming_day)
        self.fx = {}
        rate = 83.9
        for d in self.days:
            rate += self.rng.normal(0, 0.08)
            self.fx[d] = round(rate, 4)

    # dimensions -------------------------------------------------------------
    def merchants(self):
        n = self.cfg.n_merchants
        tiers = self.rng.choice(TIERS, size=n, p=TIER_W)
        cities = self.rng.choice(CITIES, size=n, p=CITY_W)
        w = self.rng.pareto(1.6, n) + 1
        w = w / w.sum()
        self.merchant_ids = np.arange(10001, 10001 + n)
        self.merchant_w = w
        self.merchant_city = dict(zip(self.merchant_ids, cities))
        start = self.days[0] - timedelta(days=365)
        rows = [(int(m), f"Merchant {int(m)}", t, start.isoformat()) for m, t in zip(self.merchant_ids, tiers)]
        return rows

    def category_map(self):
        return [(code, v[0]) for code, v in CATEGORIES.items()]

    def fx_rates(self):
        return [(d.isoformat(), "USD", self.fx[d]) for d in self.days]

    # facts ------------------------------------------------------------------
    def _orders_and_payments(self, d: date, n: int, cat_boost=None, evening_weight=0.50, retry_rate=BACKGROUND_RETRY):
        rng = self.rng
        codes = list(CATEGORIES)
        cw = np.array([CATEGORIES[c][1] for c in codes])
        if cat_boost:
            cw = cw * np.array([cat_boost.get(c, 1.0) for c in codes])
        cw = cw / cw.sum()
        order_ids = np.arange(self.next_order, self.next_order + n)
        self.next_order += n
        merch = rng.choice(self.merchant_ids, size=n, p=self.merchant_w)
        cats = rng.choice(codes, size=n, p=cw)
        chans = rng.choice(CHANNELS, size=n, p=CHANNEL_W)
        orders = [(int(o), d.isoformat(), int(m), self.merchant_city[m], c, ch)
                  for o, m, c, ch in zip(order_ids, merch, cats, chans)]

        pay_ids = np.arange(self.next_payment, self.next_payment + n)
        self.next_payment += n
        is_usd = rng.random(n) < USD_SHARE
        gw = np.where(is_usd, "GW_INTL", rng.choice(DOMESTIC_GW, size=n, p=DOMESTIC_GW_W))
        means = np.array([CATEGORIES[c][2] for c in cats])
        inr = rng.lognormal(np.log(means) - SIGMA ** 2 / 2, SIGMA)
        amount = np.where(is_usd, inr / self.fx[d], inr)
        amount = np.round(amount, 2)
        tod = _ist_tod_seconds(rng, n, evening_weight)
        midnight_ist = (datetime(d.year, d.month, d.day) - datetime(1970, 1, 1)).total_seconds()
        utc = midnight_ist + tod - 330 * 60
        files = rng.integers(1, 9, n)
        payments = []
        for i in range(n):
            payments.append([int(pay_ids[i]), int(order_ids[i]), d.isoformat(), f"F{files[i]:02d}", str(gw[i]),
                             "USD" if is_usd[i] else "INR", float(amount[i]), "CAPTURED", utc[i]])
        retries = []
        k = rng.random(n) < retry_rate
        for i in np.nonzero(k)[0]:
            r = list(payments[i])
            r[7] = "FAILED"
            r[8] = r[8] - int(rng.integers(60, 180))
            retries.append(r)
        for r in payments + retries:
            r[8] = _ts(np.array([r[8]]))[0]
        return orders, payments + retries

    def daily(self, d: date):
        n = int(round(self.cfg.orders_per_day * np.exp(self.rng.normal(0, 0.015))))
        return self._orders_and_payments(d, n)

    def festival_extra(self, d: date, base_payments):
        """Real extra demand on the incoming day, plus a burst of payment retries."""
        n = int(round(self.cfg.orders_per_day * self.cfg.festival_uplift))
        orders, payments = self._orders_and_payments(d, n, cat_boost={"ELEC": 1.25, "FASH": 1.3},
                                                     evening_weight=0.62, retry_rate=0.0)
        extra_retries = []
        captured = [p for p in base_payments + payments if p[7] == "CAPTURED"]
        idx = self.rng.choice(len(captured), size=int(len(captured) * 0.03), replace=False)
        for i in idx:
            r = list(captured[i])
            r[7] = "FAILED"
            t = datetime.strptime(r[8][:19], "%Y-%m-%d %H:%M:%S") - timedelta(seconds=int(self.rng.integers(30, 240)))
            r[8] = t.strftime("%Y-%m-%d %H:%M:%S") + ".000"
            extra_retries.append(r)
        return orders, payments + extra_retries


def _write_csv(path: Path, header: list[str], rows) -> int:
    import csv

    with path.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        n = 0
        for r in rows:
            w.writerow(r)
            n += 1
    return n


def generate(out_dir: Path, cfg: GenConfig) -> dict:
    """Write LANDING CSVs for every table and return a manifest."""
    from .model import SOURCE_TABLES

    out_dir.mkdir(parents=True, exist_ok=True)
    g = Generator(cfg)
    hdr = {t: [c for c, _ in cols] for t, cols in SOURCE_TABLES.items()}
    counts = {}
    counts["MERCHANTS"] = _write_csv(out_dir / "MERCHANTS.csv", hdr["MERCHANTS"], g.merchants())
    counts["CATEGORY_MAP"] = _write_csv(out_dir / "CATEGORY_MAP.csv", hdr["CATEGORY_MAP"], g.category_map())
    counts["FX_RATES"] = _write_csv(out_dir / "FX_RATES.csv", hdr["FX_RATES"], g.fx_rates())

    import csv
    fo = (out_dir / "ORDERS.csv").open("w", newline="")
    fp = (out_dir / "PAYMENTS.csv").open("w", newline="")
    wo, wp = csv.writer(fo, lineterminator="\n"), csv.writer(fp, lineterminator="\n")
    wo.writerow(hdr["ORDERS"])
    wp.writerow(hdr["PAYMENTS"])
    n_o = n_p = 0
    incoming_payments = None
    for d in g.days:
        orders, payments = g.daily(d)
        wo.writerows(orders)
        wp.writerows(payments)
        n_o += len(orders)
        n_p += len(payments)
        if d == cfg.incoming_day:
            incoming_payments = payments
    fo.close()
    fp.close()
    counts["ORDERS"], counts["PAYMENTS"] = n_o, n_p

    fest_o, fest_p = g.festival_extra(cfg.incoming_day, incoming_payments)
    counts["FESTIVAL_ORDERS"] = _write_csv(out_dir / "FESTIVAL_ORDERS.csv", hdr["ORDERS"], fest_o)
    counts["FESTIVAL_PAYMENTS"] = _write_csv(out_dir / "FESTIVAL_PAYMENTS.csv", hdr["PAYMENTS"], fest_p)

    c = asdict(cfg)
    c["incoming_day"] = cfg.incoming_day.isoformat()
    manifest = {"config": c, "rows": counts, "first_day": g.days[0].isoformat(),
                "incoming_day": cfg.incoming_day.isoformat()}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
