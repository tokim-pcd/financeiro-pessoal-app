"""Pacote principal do aplicativo de controle financeiro pessoal."""

from financeiro_pessoal.database import initialize_db

__all__ = ["initialize_db"]

initialize_db()
