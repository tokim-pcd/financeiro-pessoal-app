from __future__ import annotations

from typing import Any, Dict, List


def cent_to_currency(value_cents: int) -> float:
    return value_cents / 100


def month_summary(year: int, month: int, incomes: List[Dict[str, Any]], expenses: List[Dict[str, Any]], reserve: float = 0.0) -> Dict[str, Any]:
    expected_income = sum(int(item["value_cents"]) for item in incomes if str(item.get("status", "")).lower() == "prevista")
    received_income = sum(int(item["value_cents"]) for item in incomes if str(item.get("status", "")).lower() == "recebida")

    total_expenses = sum(int(item["value_cents"]) for item in expenses)
    paid_expenses = sum(int(item["value_cents"]) for item in expenses if str(item.get("status", "")).lower() == "pago")
    pending_expenses = sum(int(item["value_cents"]) for item in expenses if str(item.get("status", "")).lower() in {"pendente", "vencido"})
    cancelled_expenses = sum(int(item["value_cents"]) for item in expenses if str(item.get("status", "")).lower() == "cancelado")

    reserve_cents = int(round(reserve * 100))
    current_balance = received_income - paid_expenses - reserve_cents
    projected_balance = expected_income - total_expenses - reserve_cents

    return {
        "year": year,
        "month": month,
        "renda_prevista": cent_to_currency(expected_income),
        "renda_recebida": cent_to_currency(received_income),
        "total_despesas": cent_to_currency(total_expenses),
        "despesas_pagas": cent_to_currency(paid_expenses),
        "despesas_pendentes": cent_to_currency(pending_expenses),
        "despesas_canceladas": cent_to_currency(cancelled_expenses),
        "saldo_atual_estimado": cent_to_currency(current_balance),
        "saldo_previsto": cent_to_currency(projected_balance),
        "reserva": reserve,
    }


def category_totals(expenses: List[Dict[str, Any]]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for expense in expenses:
        category = str(expense.get("category") or "Outros")
        totals[category] = totals.get(category, 0.0) + cent_to_currency(int(expense.get("value_cents", 0)))
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def format_money(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
