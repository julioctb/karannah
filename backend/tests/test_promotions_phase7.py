# ruff: noqa: F811 -- pytest fixture imports are injected by parameter name below.
from __future__ import annotations

from datetime import date, timedelta

import pytest
from test_domain_api import (
    BRANCH_IDS,
    _checkout_payload,
    _open_t01,
    as_encargado,
    as_vendedor,
    client,  # noqa: F401 -- imported pytest fixture
    session_factory,  # noqa: F401 -- dependency of the client fixture
)

from app.api.deps import get_current_claims
from app.main import app
from app.services.pos import current_business_date

pytestmark = pytest.mark.asyncio


def _promotion_payload(
    name: str = "Venta de aniversario",
    *,
    percent: str = "10.00",
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> dict:
    return {
        "name": name,
        "discount_percent": percent,
        "starts_on": starts_on.isoformat() if starts_on else None,
        "ends_on": ends_on.isoformat() if ends_on else None,
    }


async def _create_promotion(client, **overrides) -> dict:
    payload = _promotion_payload(**overrides)
    response = await client.post("/api/v1/promotions", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _quote_payload(promotion_id: int | None = None, **overrides) -> dict:
    payload = {
        "branch_id": str(BRANCH_IDS["T01"]),
        "sale_type": "menudeo",
        "items": [{"variant_id": 1, "quantity": 1}],
        "discount_percent": "0.00",
    }
    if promotion_id is not None:
        payload["promotion_id"] = promotion_id
    payload.update(overrides)
    return payload


async def test_admin_manages_global_promotions_and_operational_roles_list_available(client):
    today = current_business_date()
    promotion = await _create_promotion(
        client,
        starts_on=today,
        ends_on=today,
    )
    assert promotion["active"] is True
    assert promotion["discount_percent"] == "10.00"
    updated = await client.patch(
        f"/api/v1/promotions/{promotion['id']}",
        json={"name": "Aniversario actualizado", "discount_percent": "12.50"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Aniversario actualizado"
    assert updated.json()["discount_percent"] == "12.50"

    app.dependency_overrides[get_current_claims] = as_vendedor
    listed = await client.get("/api/v1/promotions")
    assert listed.status_code == 200
    assert [row["id"] for row in listed.json()] == [promotion["id"]]
    denied_create = await client.post(
        "/api/v1/promotions", json=_promotion_payload("No autorizada")
    )
    assert denied_create.status_code == 403
    denied_patch = await client.patch(
        f"/api/v1/promotions/{promotion['id']}", json={"name": "No autorizada"}
    )
    assert denied_patch.status_code == 403

    app.dependency_overrides[get_current_claims] = as_encargado
    assert (await client.get("/api/v1/promotions")).status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        _promotion_payload(percent="0.00"),
        _promotion_payload(
            starts_on=date(2026, 2, 2),
            ends_on=date(2026, 2, 1),
        ),
    ],
)
async def test_promotion_constraints_reject_invalid_configuration(client, payload):
    response = await client.post("/api/v1/promotions", json=payload)
    assert response.status_code == 422


async def test_vendedor_quote_applies_promotion_without_discount_approval(client):
    promotion = await _create_promotion(client)
    app.dependency_overrides[get_current_claims] = as_vendedor

    response = await client.post(
        "/api/v1/sales/quote", json=_quote_payload(promotion["id"])
    )

    assert response.status_code == 200, response.text
    quote = response.json()
    assert quote["promotion_id"] == promotion["id"]
    assert quote["promotion_name"] == "Venta de aniversario"
    assert quote["discount_percent"] == "10.00"
    assert quote["discount"] == "180.00"
    assert quote["total"] == "1620.00"
    assert quote["approval_required"] is False


async def test_checkout_revalidates_and_persists_promotion_attribution(client):
    promotion = await _create_promotion(client)
    app.dependency_overrides[get_current_claims] = as_vendedor
    cash_session = await _open_t01(client)
    payload = _checkout_payload(cash_session["id"], amount="1620.00")
    payload["promotion_id"] = promotion["id"]

    response = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "promotion-checkout"},
        json=payload,
    )

    assert response.status_code == 201, response.text
    sale = response.json()
    assert sale["promotion_id"] == promotion["id"]
    assert sale["promotion_name"] == "Venta de aniversario"
    assert sale["discount_percent"] == "10.00"
    assert sale["discount"] == "180.00"
    assert sale["discount_approved_by"] is None
    detail = await client.get(f"/api/v1/sales/{sale['id']}")
    assert detail.json()["promotion_name"] == "Venta de aniversario"


@pytest.mark.parametrize(
    ("quote_changes", "expected_status"),
    [
        ({"discount_percent": "1.00"}, 422),
        ({"sale_type": "mayoreo"}, 422),
        ({"promotion_id": 999999}, 404),
    ],
)
async def test_quote_rejects_nonstacking_mayoreo_and_unknown_promotions(
    client, quote_changes, expected_status
):
    promotion = await _create_promotion(client)
    payload = _quote_payload(promotion["id"])
    payload.update(quote_changes)

    response = await client.post("/api/v1/sales/quote", json=payload)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("name", "starts_delta", "ends_delta"),
    [
        ("Inactiva", None, None),
        ("Futura", 1, 2),
        ("Vencida", -2, -1),
    ],
)
async def test_quote_rejects_inactive_not_yet_started_and_expired_promotions(
    client, name, starts_delta, ends_delta
):
    today = current_business_date()
    promotion = await _create_promotion(
        client,
        name=name,
        starts_on=today + timedelta(days=starts_delta) if starts_delta is not None else None,
        ends_on=today + timedelta(days=ends_delta) if ends_delta is not None else None,
    )
    if name == "Inactiva":
        deactivated = await client.patch(
            f"/api/v1/promotions/{promotion['id']}", json={"active": False}
        )
        assert deactivated.status_code == 200

    response = await client.post(
        "/api/v1/sales/quote", json=_quote_payload(promotion["id"])
    )

    assert response.status_code == 409


async def test_checkout_rejects_promotion_deactivated_after_quote(client):
    promotion = await _create_promotion(client)
    quoted = await client.post(
        "/api/v1/sales/quote", json=_quote_payload(promotion["id"])
    )
    assert quoted.status_code == 200
    deactivated = await client.patch(
        f"/api/v1/promotions/{promotion['id']}", json={"active": False}
    )
    assert deactivated.status_code == 200

    app.dependency_overrides[get_current_claims] = as_vendedor
    cash_session = await _open_t01(client)
    payload = _checkout_payload(cash_session["id"], amount="1620.00")
    payload["promotion_id"] = promotion["id"]
    response = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "stale-promotion"},
        json=payload,
    )

    assert response.status_code == 409


async def test_manual_discount_approval_path_is_unchanged(client):
    app.dependency_overrides[get_current_claims] = as_vendedor
    quote = await client.post(
        "/api/v1/sales/quote", json=_quote_payload(discount_percent="5.00")
    )
    assert quote.status_code == 200
    assert quote.json()["approval_required"] is True

    cash_session = await _open_t01(client)
    denied = await client.post(
        "/api/v1/sales/checkout",
        headers={"Idempotency-Key": "manual-discount-regression"},
        json=_checkout_payload(cash_session["id"], discount="5.00", amount="1710.00"),
    )
    assert denied.status_code == 403
