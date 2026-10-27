# A public demo of lab mode

How to put "Break the pipeline" on the internet for people to try, on the DuckDB stand-in with synthetic data
only. Nothing here is deployed; this page and the files it names are the package.

## What a visitor can do

The command center in lab mode: Break the pipeline (pick a fault, a share and a gateway, watch the gate step by
step), Reset, approve a proven correction, the Red team tab with "Run one attack", and the trust badge at
`/badge.svg`. Explanations use the deterministic template; no API key is passed to the container.

## What protects it

| Guard | How |
|---|---|
| Synthetic data only | Breaking, resetting and attacking are refused (409) unless the database matches `data/manifest.json` of the synthetic generator. The container builds that data itself and has no other data source. |
| Normal mode stays read-only | Without `--lab` the lab endpoints answer 403 and the panels are not on the page, also with the public demo switch on. |
| Rate limits | With `RECEIPTS_PUBLIC_DEMO=1`, every action that writes (Break, Reset, Run one attack, run a scenario, approve) is limited per client (`RECEIPTS_DEMO_PER_MIN`, default 6 a minute) and for the whole server (`RECEIPTS_DEMO_GLOBAL_PER_MIN`, default 30). Over the limit: 429 with `Retry-After`. Reading the page, a case or the badge is not limited. |
| One run at a time | A second Break while the gate is running gets 409. |
| Automatic reset | After `RECEIPTS_DEMO_RESET_MIN` idle minutes (default 10) tonight's batch and its published row are removed, so the next visitor starts from a clean night. |
| Fresh day | `receipts demo` rebuilds the synthetic data when it is not for yesterday, also while running. |
| No root, no key | The `public` image runs as an unprivileged user and sets `ANTHROPIC_API_KEY` to empty. |

The client for the per-client limit is the first `X-Forwarded-For` address when the platform's proxy sets it,
else the socket address. A visitor who forges that header gets their own bucket, but the server-wide limit still
holds.

## Run it locally first

```bash
docker build --target public -t receipts-public .
```

```bash
docker run --rm -p 8080:8080 receipts-public
```

Without Docker, the same guards: `RECEIPTS_PUBLIC_DEMO=1 receipts demo --lab --port 8080`.

## Deploy

`fly.toml` builds the `public` target and listens on 8080: `fly launch --no-deploy --copy-config` with your own
app name, then `fly deploy`. Any platform that runs a Dockerfile works the same way: build with `--target public`,
expose port 8080, one instance (the stand-in database lives inside the container and is rebuilt on start).

## What was checked

* The guards are covered by `tests/test_hosted.py` (rate limits, automatic reset, 403 without lab mode, the
  Dockerfile's public target) and by a local run of `receipts demo --lab` with `RECEIPTS_PUBLIC_DEMO=1`: two
  resets answered 200, the third and a Break answered 429, the badge 200.
* The Docker image was not built on the development laptop: Docker keeps its images on the system drive, which
  had no room. The image and `fly.toml` are listed under "Verified and not covered" in the README.
