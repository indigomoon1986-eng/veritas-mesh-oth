"""python -m app.cli send --text 'node check' --mode nvis"""

from __future__ import annotations

import argparse
import json

from app.service import OthApp
from app.types import Outbound


def main() -> None:
    parser = argparse.ArgumentParser(prog="veritas-oth")
    sub = parser.add_subparsers(dest="cmd", required=True)
    send = sub.add_parser("send")
    send.add_argument("--text", required=True)
    send.add_argument("--mode", choices=["nvis", "skywave"], default="nvis")
    send.add_argument("--azimuth", type=float, default=0.0)
    send.add_argument("--range-km", type=float, default=300.0)
    send.add_argument("--freq-hz", type=float, default=None)
    plan = sub.add_parser("plan")
    plan.add_argument("--mode", choices=["nvis", "skywave"], default="skywave")
    plan.add_argument("--azimuth", type=float, default=0.0)
    plan.add_argument("--range-km", type=float, default=800.0)
    args = parser.parse_args()
    app = OthApp()
    if args.cmd == "send":
        out = app.send(Outbound(args.text, args.mode, args.azimuth, args.range_km, args.freq_hz))
    else:
        out = app.plan(args.mode, args.azimuth, args.range_km).to_dict()
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
