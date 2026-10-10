"""X.4.2 typed payment rail for Monarch X.

M is quantity, asset, and price. Two amounts settle only when the asset matches.
Pipeline: Intent, Identity, Consent, Validation, Execution, Receipt, Audit.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Amount:
    quantity: str
    asset: str
    price: str

    def same_asset(self, other: "Amount") -> bool:
        return self.asset == other.asset


@dataclass
class Intent:
    sender: str
    receiver: str
    amount: Amount
    purpose: str


@dataclass
class Identity:
    node_id: str
    key_slot: str


@dataclass
class Consent:
    granted: bool
    by: str


@dataclass
class Receipt:
    ok: bool
    stage: str
    amount: Amount | None = None
    note: str = ""
    audit: list[str] = field(default_factory=list)


class Rail:
    def __init__(self, identity: Identity):
        self.identity = identity
        self.audit: list[str] = []

    def run(self, intent: Intent, consent: Consent) -> Receipt:
        self.audit.append("intent")
        if intent.sender != self.identity.node_id:
            return self._fail("identity", "sender is not this node")
        self.audit.append("identity")
        if not consent.granted or consent.by != intent.sender:
            return self._fail("consent", "consent missing")
        self.audit.append("consent")
        if not intent.amount.quantity or not intent.amount.asset or not intent.amount.price:
            return self._fail("validation", "amount is not fully typed")
        self.audit.append("validation")
        self.audit.append("execution")
        self.audit.append("receipt")
        receipt = Receipt(True, "receipt", intent.amount, "typed transfer accepted on mesh", list(self.audit))
        self.audit.append("audit")
        receipt.audit = list(self.audit)
        return receipt

    def settle(self, left: Amount, right: Amount) -> Receipt:
        if not left.same_asset(right):
            return self._fail("validation", f"cannot settle {left.asset} against {right.asset}")
        return Receipt(True, "validation", left, "assets match")

    def _fail(self, stage: str, note: str) -> Receipt:
        self.audit.append(stage)
        return Receipt(False, stage, None, note, list(self.audit))
