"""
Wraps the openFDA Drug Label API (https://api.fda.gov/drug/label.json).
Fetches live FDA label text for each drug -- no caching, no stale data.
"""

from __future__ import annotations
import datetime
import time
from dataclasses import dataclass, field
import requests

FDA_LABEL_URL = "https://api.fda.gov/drug/label.json"
REQUEST_TIMEOUT = 20
RATE_LIMIT_SECONDS = 0.3


@dataclass
class DrugLabel:
    query: str
    found: bool
    brand_name: str | None = None
    generic_name: str | None = None
    rxcui: list[str] = field(default_factory=list)
    drug_interactions: str | None = None
    warnings: str | None = None
    contraindications: str | None = None
    boxed_warning: str | None = None
    error: str | None = None

    def to_context_block(self) -> str:
        if not self.found:
            return f"## {self.query}\nNo FDA label found. {self.error or ''}".strip()

        name = self.brand_name or self.generic_name or self.query
        parts = [f"## {name} (queried as '{self.query}')"]
        if self.boxed_warning:
            parts.append(f"BOXED WARNING: {self.boxed_warning[:1200]}")
        if self.drug_interactions:
            parts.append(f"Drug Interactions: {self.drug_interactions[:1200]}")
        if self.contraindications:
            parts.append(f"Contraindications: {self.contraindications[:800]}")
        if self.warnings:
            parts.append(f"Warnings: {self.warnings[:800]}")
        if len(parts) == 1:
            parts.append("(Label found but no structured safety sections present.)")
        return "\n\n".join(parts)


def _first(values, default=None):
    if isinstance(values, list) and values:
        return values[0]
    return default


def _join(values, default=None):
    if isinstance(values, list) and values:
        return " ".join(values)
    return default


def _query_once(field: str, drug_name: str, quoted: bool) -> dict | None:
    term = f'"{drug_name}"' if quoted else drug_name
    params = {"search": f"{field}:{term}", "limit": 1}
    resp = requests.get(FDA_LABEL_URL, params=params, timeout=REQUEST_TIMEOUT)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


def lookup_drug_label(drug_name: str) -> DrugLabel:
    drug_name = drug_name.strip()
    if not drug_name:
        return DrugLabel(query=drug_name, found=False, error="Empty drug name.")
    try:
        record = None
        for field_name in ("openfda.generic_name", "openfda.brand_name"):
            for quoted in (True, False):
                record = _query_once(field_name, drug_name, quoted)
                if record:
                    break
            if record:
                break
            time.sleep(RATE_LIMIT_SECONDS)

        if not record:
            return DrugLabel(query=drug_name, found=False, error="No matching FDA label found.")

        openfda = record.get("openfda", {})
        return DrugLabel(
            query=drug_name,
            found=True,
            brand_name=_first(openfda.get("brand_name")),
            generic_name=_first(openfda.get("generic_name")),
            rxcui=openfda.get("rxcui", []),
            drug_interactions=_join(record.get("drug_interactions")),
            warnings=_join(record.get("warnings")),
            contraindications=_join(record.get("contraindications")),
            boxed_warning=_join(record.get("boxed_warning")),
        )
    except requests.exceptions.RequestException as e:
        return DrugLabel(query=drug_name, found=False, error=f"openFDA request failed: {e}")


def lookup_multiple(drug_names: list[str]) -> list[DrugLabel]:
    out = []
    for name in drug_names:
        out.append(lookup_drug_label(name))
        time.sleep(RATE_LIMIT_SECONDS)
    return out


def get_drug_safety_info(drug_names: list[str]) -> dict:
    """
    Retrieve official FDA label safety information for a list of medications.

    Use this tool to check for drug interactions, contraindications, or
    boxed warnings. Pass generic or brand names (e.g. "metformin", "Lipitor").
    Returns FDA label text for each drug which you should reason over to
    identify conflicts across the full medication list.

    Args:
        drug_names: List of medication names e.g. ["warfarin", "ibuprofen"]

    Returns:
        dict with label text per drug, lookup failures, and fetch timestamp.
    """
    labels = lookup_multiple(drug_names)
    failures = [l.query for l in labels if not l.found]
    return {
        "labels": [l.to_context_block() for l in labels],
        "lookup_failures": failures,
        "source": "FDA openFDA Drug Label API (api.fda.gov)",
        "fetched_live_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "freshness_note": (
            "Labels fetched live from api.fda.gov at time of this run -- "
            "not cached. Reflects current published FDA label."
        ),
    }


if __name__ == "__main__":
    import json
    result = get_drug_safety_info(["warfarin", "ibuprofen"])
    print(json.dumps(result, indent=2)[:3000])