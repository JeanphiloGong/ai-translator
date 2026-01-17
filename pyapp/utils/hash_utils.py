import json
from typing import Any, Dict, Tuple

from eth_hash.auto import keccak


def canonical_json_dumps(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def keccak_hex(value: str) -> str:
    return "0x" + keccak(value.encode("utf-8")).hex()


def hash_payload(payload: Dict[str, Any]) -> Tuple[str, str]:
    canonical = canonical_json_dumps(payload)
    return keccak_hex(canonical), canonical
