from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    code: str
    name: str
    tier: str = "normal"
