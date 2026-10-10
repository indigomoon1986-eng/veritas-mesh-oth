"""x402 V2 policy for the mesh.

A paid route answers 402 with PAYMENT-REQUIRED until the client sends
PAYMENT-SIGNATURE for the exact amount. This checks shape and amount. It does
not settle on a chain.
"""

from __future__ import annotations

import base64
import json
from dataclasses import asdict, dataclass, field


@dataclass
class Amount:
    atomic: str
    asset: str = "USDC"

    def matches(self, other: str) -> bool:
        return self.atomic == other


@dataclass
class PaymentRequired:
    x402Version: int
    error: str
    resource: dict
    accepts: list[dict]
    extensions: dict = field(default_factory=dict)

    def header(self) -> str:
        return base64.b64encode(json.dumps(asdict(self)).encode()).decode()


@dataclass
class PaymentState:
    required: Amount
    paid: Amount | None = None
    payer: str = ""
    settled: bool = False


def requirement(url: str, amount: Amount, pay_to: str, network: str = "eip155:84532") -> PaymentRequired:
    return PaymentRequired(
        x402Version=2,
        error="PAYMENT-SIGNATURE header is required",
        resource={"url": url, "description": "Veritas mesh send", "mimeType": "application/json"},
        accepts=[{"scheme": "exact", "network": network, "amount": amount.atomic, "asset": amount.asset, "payTo": pay_to, "maxTimeoutSeconds": 60, "extra": {"name": amount.asset, "version": "2"}}],
    )


def decode_signature(header: str) -> dict:
    return json.loads(base64.b64decode(header))


def verify(required: PaymentRequired, signature_header: str | None) -> PaymentState:
    amount = Amount(required.accepts[0]["amount"], required.accepts[0]["asset"])
    state = PaymentState(required=amount)
    if not signature_header:
        return state
    payload = decode_signature(signature_header)
    state.payer = str(payload.get("payer", ""))
    state.paid = Amount(str(payload.get("amount", "")), str(payload.get("asset", "")))
    state.settled = state.paid.matches(amount.atomic) and bool(state.payer)
    return state
