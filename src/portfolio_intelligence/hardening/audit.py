from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from pydantic import Field

from portfolio_intelligence.domain.models import StrictModel


class AuditRecord(StrictModel):
    record_id: str
    event_type: str
    aggregate_id: str
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
    previous_hash: str = ""
    record_hash: str = ""

    def with_hash(self) -> "AuditRecord":
        body = self.model_dump(mode="json", exclude={"record_hash"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return self.model_copy(update={"record_hash": digest})


def deterministic_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
