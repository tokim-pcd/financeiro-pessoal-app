from __future__ import annotations

try:
    import customtkinter as ctk
except ModuleNotFoundError:  # pragma: no cover - depende da instalação do pacote
    ctk = None

from financeiro_pessoal.config import APP_NAME


class FinanceApp:
    def __init__(self) -> None:
        if ctk is None:
            raise RuntimeError(
                "customtkinter não está instalado. Execute: pip install -r requirements.txt"
            )

        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        self.root.geometry("1200x760")
        self.root.minsize(900, 600)
        self.root.configure(fg_color="#F4F8FF")

        title = ctk.CTkLabel(
            self.root,
            text="Financeiro Pessoal",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#123A66",
        )
        title.pack(padx=24, pady=(18, 8), anchor="w")

        subtitle = ctk.CTkLabel(
            self.root,
            text="Base funcional do sistema financeiro local com banco SQLite.",
            font=ctk.CTkFont(size=14),
            text_color="#445B76",
        )
        subtitle.pack(padx=24, pady=(0, 18), anchor="w")

        card = ctk.CTkFrame(self.root, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=22, pady=(0, 22))

        ctk.CTkLabel(
            card,
            text="Status da estrutura",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0F2E52",
        ).pack(anchor="w", padx=18, pady=(18, 8))

        ctk.CTkLabel(
            card,
            text="- Banco SQLite local\n- Persistência em arquivo no diretório do usuário\n- Estrutura modular para receitas, despesas e serviços\n- Pronto para expansão para cartões, recorrências, relatórios e backups",
            justify="left",
            text_color="#2A3E56",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def run(self) -> None:
        self.root.mainloop()


def run() -> None:
    app = FinanceApp()
    app.run()


if __name__ == "__main__":
    run()
