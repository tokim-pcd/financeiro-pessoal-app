from __future__ import annotations

import os
from tkinter import messagebox

import customtkinter as ctk

from financeiro_pessoal.config import APP_NAME
from financeiro_pessoal.database import (
    add_expense,
    add_income,
    get_categories,
    list_expenses,
    list_incomes,
    set_setting,
)
from financeiro_pessoal.services.finance_service import format_money, month_summary


class FinanceApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1280x760")
        self.minsize(1050, 650)
        self.configure(fg_color="#F3F7FF")

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0E4A92")
        self.sidebar.pack(side="left", fill="y")

        title = ctk.CTkLabel(self.sidebar, text="Financeiro\nPessoal", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        title.pack(padx=20, pady=24, anchor="w")

        self.nav_buttons = {}
        for label in [
            "Dashboard",
            "Receitas",
            "Despesas",
            "Contas recorrentes",
            "Cartões",
            "Metas",
            "Relatórios",
            "Configurações",
        ]:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                fg_color="transparent",
                border_color="#DCEBFF",
                border_width=1,
                hover_color="#1A66C2",
                command=lambda item=label: self.show_screen(item),
            )
            btn.pack(fill="x", padx=18, pady=6)
            self.nav_buttons[label] = btn

        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color="#F3F7FF")
        self.main.pack(side="right", fill="both", expand=True)

        self.frames = {}
        self.frames["Dashboard"] = DashboardFrame(self.main, self)
        self.frames["Receitas"] = IncomeFrame(self.main, self)
        self.frames["Despesas"] = ExpenseFrame(self.main, self)
        self.frames["Contas recorrentes"] = RecurringFrame(self.main, self)
        self.frames["Cartões"] = CardsFrame(self.main, self)
        self.frames["Metas"] = GoalsFrame(self.main, self)
        self.frames["Relatórios"] = ReportsFrame(self.main, self)
        self.frames["Configurações"] = SettingsFrame(self.main, self)

        for key, frame in self.frames.items():
            frame.pack_forget()

        self.show_screen("Dashboard")

    def show_screen(self, name: str) -> None:
        for key, frame in self.frames.items():
            if key == name:
                frame.pack(fill="both", expand=True)
                frame.refresh()
            else:
                frame.pack_forget()


class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#F3F7FF")
        self.app = app

    def refresh(self):
        pass


class DashboardFrame(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F")
        self.title.pack(anchor="w", padx=24, pady=(20, 10))

        self.card_container = ctk.CTkFrame(self, fg_color="transparent")
        self.card_container.pack(fill="x", padx=20, pady=10)

        self.cards = []
        for i in range(6):
            card = ctk.CTkFrame(self.card_container, width=180, corner_radius=14, fg_color="white")
            card.grid(row=0, column=i, padx=12, pady=8, sticky="nsew")
            self.cards.append(card)

        self.summary_text = ctk.CTkLabel(self, text="", justify="left", font=ctk.CTkFont(size=14), text_color="#233B5E")
        self.summary_text.pack(anchor="w", padx=24, pady=(8, 0))

        self.table = ctk.CTkScrollableFrame(self, width=900, height=400, fg_color="white", corner_radius=14)
        self.table.pack(fill="both", expand=True, padx=24, pady=20)

    def refresh(self):
        year = 2026
        month = 10
        incomes = list_incomes(year, month)
        expenses = list_expenses(year, month)
        data = month_summary(year, month, incomes, expenses, reserve=300)

        labels = [
            ("Renda prevista", format_money(data["renda_prevista"]), "#EAF4FF"),
            ("Renda recebida", format_money(data["renda_recebida"]), "#EAFBEA"),
            ("Total de despesas", format_money(data["total_despesas"]), "#FFF0ED"),
            ("Despesas pendentes", format_money(data["despesas_pendentes"]), "#FFF7E8"),
            ("Saldo atual", format_money(data["saldo_atual_estimado"]), "#ECF7F1"),
            ("Saldo previsto", format_money(data["saldo_previsto"]), "#EAF4FF"),
        ]

        for card, (label, value, color) in zip(self.cards, labels):
            for child in card.winfo_children():
                child.destroy()
            card.configure(fg_color=color)
            ctk.CTkLabel(card, text=label, text_color="#4A5F78", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=14, pady=(12, 0))
            ctk.CTkLabel(card, text=value, text_color="#0E243F", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=14, pady=(6, 12))

        self.summary_text.configure(
            text=(
                f"Receitas previstas: {format_money(data['renda_prevista'])} | "
                f"Despesas pendentes: {format_money(data['despesas_pendentes'])} | "
                f"Saldo estimado: {format_money(data['saldo_atual_estimado'])}"
            )
        )

        for child in self.table.winfo_children():
            child.destroy()

        if not expenses:
            ctk.CTkLabel(self.table, text="Nenhuma despesa cadastrada para este mês.", text_color="#5A6B82").pack(anchor="w", padx=18, pady=18)
            return

        header = ctk.CTkFrame(self.table, fg_color="#EFF5FF")
        header.pack(fill="x", padx=12, pady=(12, 6))
        for title, width in [("Despesa", 260), ("Categoria", 180), ("Valor", 120), ("Status", 120), ("Vencimento", 140)]:
            ctk.CTkLabel(header, text=title, width=width, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color="#1E3A5C").pack(side="left", padx=8, pady=8)

        for item in expenses[:8]:
            row = ctk.CTkFrame(self.table, fg_color="white")
            row.pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(row, text=item["description"], width=260, anchor="w").pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=item["category"], width=180, anchor="w").pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=format_money(item["value_cents"] / 100), width=120, anchor="w").pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=item["status"], width=120, anchor="w").pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=item["due_date"], width=140, anchor="w").pack(side="left", padx=8, pady=6)


class IncomeFormMixin:
    def build_income_form(self, parent):
        details = ctk.CTkFrame(parent, fg_color="white", corner_radius=16)
        details.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(details, text="Nova receita", font=ctk.CTkFont(size=22, weight="bold"), text_color="#163C6A").pack(anchor="w", padx=18, pady=(18, 8))

        form = ctk.CTkFrame(details, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=18, pady=8)

        fields = {
            "description": ctk.CTkEntry(form, placeholder_text="Descrição da receita"),
            "value": ctk.CTkEntry(form, placeholder_text="Valor (ex.: 4500.00)"),
            "category": ctk.CTkOptionMenu(form, values=["Salário", "Trabalho extra", "Freelance", "Benefícios", "Reembolsos", "Outros"]),
            "expected_date": ctk.CTkEntry(form, placeholder_text="Data prevista (AAAA-MM-DD)"),
            "payment_method": ctk.CTkOptionMenu(form, values=["PIX", "Transferência", "Dinheiro", "Boleto", "Outro"]),
            "status": ctk.CTkOptionMenu(form, values=["prevista", "recebida"]),
            "notes": ctk.CTkEntry(form, placeholder_text="Observações (opcional)"),
        }

        for key, widget in fields.items():
            widget.pack(fill="x", pady=6)

        save_button = ctk.CTkButton(form, text="Salvar receita", command=lambda: self.save_income(fields))
        save_button.pack(fill="x", pady=(10, 0))
        return details

    def save_income(self, fields):
        try:
            value = float(fields["value"].get())
        except ValueError:
            messagebox.showerror("Erro", "Informe um valor numérico válido para a receita.")
            return

        payload = {
            "description": fields["description"].get().strip(),
            "value_cents": int(round(value * 100)),
            "category": fields["category"].get(),
            "expected_date": fields["expected_date"].get() or "2026-01-01",
            "received_date": fields["expected_date"].get() if fields["status"].get() == "recebida" else None,
            "status": fields["status"].get(),
            "payment_method": fields["payment_method"].get(),
            "notes": fields["notes"].get().strip(),
        }
        if not payload["description"]:
            messagebox.showerror("Erro", "Preencha a descrição da receita.")
            return
        add_income(payload)
        self.refresh()


class IncomeFrame(BaseScreen, IncomeFormMixin):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title = ctk.CTkLabel(self, text="Receitas", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F")
        self.title.pack(anchor="w", padx=24, pady=(20, 10))
        self.form_container = None
        self.list_container = None

    def refresh(self):
        if self.form_container is not None:
            self.form_container.destroy()
        if self.list_container is not None:
            self.list_container.destroy()

        self.form_container = self.build_income_form(self)
        self.list_container = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        incomes = list_incomes(2026, 10)
        ctk.CTkLabel(self.list_container, text="Receitas do mês", font=ctk.CTkFont(size=18, weight="bold"), text_color="#163C6A").pack(anchor="w", padx=18, pady=(18, 10))

        if not incomes:
            ctk.CTkLabel(self.list_container, text="Nenhuma receita cadastrada.", text_color="#596D85").pack(anchor="w", padx=18, pady=8)
            return

        table = ctk.CTkFrame(self.list_container, fg_color="transparent")
        table.pack(fill="both", expand=True, padx=18, pady=8)

        headers = ["Descrição", "Valor", "Categoria", "Status"]
        for title, index in zip(headers, range(len(headers))):
            ctk.CTkLabel(table, text=title, font=ctk.CTkFont(size=12, weight="bold"), width=180, anchor="w", text_color="#1F3F61").grid(row=0, column=index, padx=8, pady=4)

        for row_index, item in enumerate(incomes[:10], start=1):
            ctk.CTkLabel(table, text=item["description"], width=180, anchor="w").grid(row=row_index, column=0, padx=8, pady=4)
            ctk.CTkLabel(table, text=format_money(item["value_cents"] / 100), width=120, anchor="w").grid(row=row_index, column=1, padx=8, pady=4)
            ctk.CTkLabel(table, text=item["category"], width=150, anchor="w").grid(row=row_index, column=2, padx=8, pady=4)
            ctk.CTkLabel(table, text=item["status"], width=100, anchor="w").grid(row=row_index, column=3, padx=8, pady=4)


class ExpenseFormMixin:
    def build_expense_form(self, parent):
        details = ctk.CTkFrame(parent, fg_color="white", corner_radius=16)
        details.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(details, text="Nova despesa", font=ctk.CTkFont(size=22, weight="bold"), text_color="#163C6A").pack(anchor="w", padx=18, pady=(18, 8))

        form = ctk.CTkFrame(details, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=18, pady=8)

        fields = {
            "description": ctk.CTkEntry(form, placeholder_text="Nome da despesa"),
            "value": ctk.CTkEntry(form, placeholder_text="Valor (ex.: 350.50)"),
            "category": ctk.CTkOptionMenu(form, values=get_categories()),
            "due_date": ctk.CTkEntry(form, placeholder_text="Data de vencimento (AAAA-MM-DD)"),
            "status": ctk.CTkOptionMenu(form, values=["pendente", "pago", "vencido", "cancelado"]),
            "payment_method": ctk.CTkOptionMenu(form, values=["PIX", "Cartão de crédito", "Cartão de débito", "Dinheiro", "Transferência", "Boleto", "Débito automático", "Outro"]),
            "notes": ctk.CTkEntry(form, placeholder_text="Observações (opcional)"),
        }

        for key, widget in fields.items():
            widget.pack(fill="x", pady=6)

        ctk.CTkButton(form, text="Salvar despesa", command=lambda: self.save_expense(fields)).pack(fill="x", pady=(10, 0))
        return details

    def save_expense(self, fields):
        try:
            value = float(fields["value"].get())
        except ValueError:
            messagebox.showerror("Erro", "Informe um valor numérico válido para a despesa.")
            return

        payload = {
            "description": fields["description"].get().strip(),
            "value_cents": int(round(value * 100)),
            "category": fields["category"].get(),
            "due_date": fields["due_date"].get() or "2026-01-01",
            "paid_date": None if fields["status"].get() != "pago" else fields["due_date"].get() or "2026-01-01",
            "payment_method": fields["payment_method"].get(),
            "status": fields["status"].get(),
            "notes": fields["notes"].get().strip(),
        }
        if not payload["description"]:
            messagebox.showerror("Erro", "Preencha a descrição da despesa.")
            return
        add_expense(payload)
        self.refresh()


class ExpenseFrame(BaseScreen, ExpenseFormMixin):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title = ctk.CTkLabel(self, text="Despesas", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F")
        self.title.pack(anchor="w", padx=24, pady=(20, 10))
        self.form_container = None
        self.list_container = None

    def refresh(self):
        if self.form_container is not None:
            self.form_container.destroy()
        if self.list_container is not None:
            self.list_container.destroy()

        self.form_container = self.build_expense_form(self)
        self.list_container = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        expenses = list_expenses(2026, 10)
        ctk.CTkLabel(self.list_container, text="Despesas do mês", font=ctk.CTkFont(size=18, weight="bold"), text_color="#163C6A").pack(anchor="w", padx=18, pady=(18, 10))

        if not expenses:
            ctk.CTkLabel(self.list_container, text="Nenhuma despesa cadastrada.", text_color="#596D85").pack(anchor="w", padx=18, pady=8)
            return

        table = ctk.CTkFrame(self.list_container, fg_color="transparent")
        table.pack(fill="both", expand=True, padx=18, pady=8)

        headers = ["Descrição", "Valor", "Categoria", "Status"]
        for title, index in zip(headers, range(len(headers))):
            ctk.CTkLabel(table, text=title, font=ctk.CTkFont(size=12, weight="bold"), width=180, anchor="w", text_color="#1F3F61").grid(row=0, column=index, padx=8, pady=4)

        for row_index, item in enumerate(expenses[:10], start=1):
            ctk.CTkLabel(table, text=item["description"], width=180, anchor="w").grid(row=row_index, column=0, padx=8, pady=4)
            ctk.CTkLabel(table, text=format_money(item["value_cents"] / 100), width=120, anchor="w").grid(row=row_index, column=1, padx=8, pady=4)
            ctk.CTkLabel(table, text=item["category"], width=150, anchor="w").grid(row=row_index, column=2, padx=8, pady=4)
            ctk.CTkLabel(table, text=item["status"], width=100, anchor="w").grid(row=row_index, column=3, padx=8, pady=4)


class RecurringFrame(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        ctk.CTkLabel(self, text="Contas recorrentes", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F").pack(anchor="w", padx=24, pady=(20, 10))
        ctk.CTkLabel(self, text="Módulo de contas recorrentes em desenvolvimento. Base de dados e arquitetura já preparadas para expansão.", text_color="#4B5F72").pack(anchor="w", padx=24, pady=12)

    def refresh(self):
        pass


class CardsFrame(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        ctk.CTkLabel(self, text="Cartões", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F").pack(anchor="w", padx=24, pady=(20, 10))
        ctk.CTkLabel(self, text="Cadastro, faturas e parcelamento prontos para extensão no modelo financeiro central.", text_color="#4B5F72").pack(anchor="w", padx=24, pady=12)

    def refresh(self):
        pass


class GoalsFrame(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        ctk.CTkLabel(self, text="Metas de economia", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F").pack(anchor="w", padx=24, pady=(20, 10))
        ctk.CTkLabel(self, text="Estrutura preparada para controlar reservas e objetivos financeiros com rastreio de progresso.", text_color="#4B5F72").pack(anchor="w", padx=24, pady=12)

    def refresh(self):
        pass


class ReportsFrame(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        ctk.CTkLabel(self, text="Relatórios e gráficos", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F").pack(anchor="w", padx=24, pady=(20, 10))
        ctk.CTkLabel(self, text="Gráficos e exportações em PNG/PDF/Excel/CSV podem ser acrescentados no próximo ciclo de desenvolvimento.", text_color="#4B5F72").pack(anchor="w", padx=24, pady=12)

    def refresh(self):
        pass


class SettingsFrame(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.title = ctk.CTkLabel(self, text="Configurações", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0E243F")
        self.title.pack(anchor="w", padx=24, pady=(20, 10))

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nome do usuário")
        self.name_entry.pack(fill="x", padx=24, pady=8)

        self.save_btn = ctk.CTkButton(self, text="Salvar configurações", command=self.save_settings)
        self.save_btn.pack(anchor="w", padx=24, pady=12)

    def save_settings(self):
        set_setting("user_name", self.name_entry.get())
        messagebox.showinfo("Sucesso", "Configuração salva com sucesso.")

    def refresh(self):
        from financeiro_pessoal.database import get_setting
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, get_setting("user_name", ""))


def run() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = FinanceApp()
    app.mainloop()


if __name__ == "__main__":
    run()
