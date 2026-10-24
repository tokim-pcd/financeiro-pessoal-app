# Financeiro Pessoal

Aplicativo local para controle financeiro pessoal em Python, com interface em CustomTkinter e persistência em SQLite.

## Estrutura do projeto

- `financeiro_pessoal/` — código principal do aplicativo
- `main.py` — entrada da aplicação
- `tests/` — testes automatizados

## Requisitos

- Python 3.10+
- pip

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Funcionalidades implementadas nesta base

- Banco SQLite com persistência local
- Dashboard inicial com indicadores financeiros
- Cadastro de receitas
- Cadastro de despesas
- Cálculo de síntese mensal
- Configurações básicas do usuário
- Arquitetura modular para expansão

## Próximos ciclos

- Contas recorrentes
- Cartões e parcelamentos
- Metas de economia
- Relatórios em PNG/PDF/Excel/CSV
- Backup e restauração
