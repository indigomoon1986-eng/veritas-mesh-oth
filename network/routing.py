"""Hop table. A message relays through known nodes. No default route to the internet."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HopTable:
    node_id: str
    neighbors: dict[str, list[str]] = field(default_factory=dict)

    def learn(self, peer: str, via: str | None = None) -> None:
        self.neighbors.setdefault(peer, [])
        hop = via or peer
        if hop not in self.neighbors[peer]:
            self.neighbors[peer].append(hop)

    def route(self, dest: str) -> list[str]:
        if dest == self.node_id:
            return [self.node_id]
        if dest not in self.neighbors or not self.neighbors[dest]:
            raise KeyError(f"no sovereign route to {dest}")
        path = self.neighbors[dest]
        if path[-1] == dest:
            return [self.node_id, *path]
        return [self.node_id, *path, dest]
