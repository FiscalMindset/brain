"""Integration adapter catalogue (contract preview, no live OAuth yet)."""

from fastapi import APIRouter

from app.integrations.adapters import ADAPTERS, describe_contract

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("")
def list_integrations():
    """List adapters with status and the shared ingestion contract."""
    return {
        "integrations": [
            {"name": a.name, "status": a.status, "requires_oauth": a.requires_oauth} for a in ADAPTERS
        ],
        "contract": describe_contract(),
        "count": len(ADAPTERS),
    }
