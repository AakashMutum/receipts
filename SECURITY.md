# Security

To report a security issue, open a GitHub issue that describes the problem without exploit details and asks for a private contact, or contact the maintainer, Aakash Singh Mutum, through the GitHub profile [@AakashMutum](https://github.com/AakashMutum). Please do not publish details until a fix is available.

All data in this repository is synthetic and generated from a seed. It contains no real customer, payment or personal data. The only credentials in the repository are the documented local defaults of Exasol Personal (`sys` / `exasol`), which are for a database bound to localhost. The read-only agent user that `receipts init` creates on Exasol (`AGENT_READER`) has a documented local default password in `mcp/mcp_client_config.example.json`; set `RECEIPTS_AGENT_PASSWORD` to something else for anything shared. Never point Receipts at a shared database with default credentials.

Everything that can write bad data is lab-only: planting scenarios, Break the pipeline and the red team need `--lab` (or `RECEIPTS_LAB=1`) and refuse to run unless the loaded data is the built-in synthetic data. `receipts redteam`, `receipts scale`, `receipts eval` and `receipts variants` on Exasol rebuild the schemas at `EXA_DSN`: run them only against a local Exasol Personal that holds nothing else, never against production tables.
