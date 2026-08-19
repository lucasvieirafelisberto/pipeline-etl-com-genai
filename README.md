# 🚀 Pipeline ETL com IA Generativa

**DIO TOTVS 2026 | Fundamentos de Engenharia de Dados e Machine Learning**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Anthropic](https://img.shields.io/badge/Claude-Sonnet_4-orange)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 Sobre o Projeto

Pipeline **ETL (Extract → Transform → Load)** que usa **IA Generativa (Claude)** para enriquecer dados de clientes bancários com mensagens personalizadas com base no perfil financeiro de cada usuário.

```
┌─────────────┐     ┌──────────────────────────────┐     ┌─────────────────────┐
│  EXTRACT    │────►│         TRANSFORM            │────►│       LOAD          │
│             │     │                              │     │                     │
│  CSV com    │     │  1. Classifica perfil        │     │  JSON enriquecido   │
│  usuários   │     │     (Premium / Intermediário │     │  CSV para BI/DW     │
│  bancários  │     │      / Iniciante)            │     │                     │
│             │     │  2. IA gera mensagem pessoal │     │                     │
└─────────────┘     └──────────────────────────────┘     └─────────────────────┘
```

---

## 🗂️ Estrutura do Projeto

```
etl_dio/
├── data/
│   └── usuarios.csv               # Dados de entrada
├── output/                        # Criado automaticamente pelo pipeline
│   ├── usuarios_enriquecidos.json
│   └── usuarios_enriquecidos.csv
├── notebooks/
│   └── ETL_DIO_TOTVS_2026.ipynb  # Notebook interativo
├── etl_pipeline.py                # Script principal (produção)
├── .env.example                   # Template de variáveis de ambiente
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/<seu-usuario>/etl-dio-totvs-2026
cd etl-dio-totvs-2026

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as credenciais
cp .env.example .env
# Edite .env e adicione sua ANTHROPIC_API_KEY
```

### Obtendo a API Key

1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Crie uma conta ou faça login
3. Vá em **API Keys** → **Create Key**
4. Copie a chave e cole no arquivo `.env`

---

## 🚀 Execução

### Via script Python (produção)
```bash
python etl_pipeline.py
```

### Via Jupyter Notebook (exploratório)
```bash
jupyter notebook notebooks/ETL_DIO_TOTVS_2026.ipynb
```

### Saída esperada
```
2026-01-15 10:30:00 [INFO] ═══════════════════════════════════════════════════
2026-01-15 10:30:00 [INFO]   PIPELINE ETL — IA Generativa  |  DIO TOTVS 2026 | Engenharia de Dados e ML
2026-01-15 10:30:00 [INFO] ═══════════════════════════════════════════════════
2026-01-15 10:30:00 [INFO] ─── EXTRACT ────────────────────────────────────────
2026-01-15 10:30:00 [INFO] ✓ 5 usuários extraídos com sucesso.
2026-01-15 10:30:00 [INFO] ─── TRANSFORM ──────────────────────────────────────
2026-01-15 10:30:00 [INFO] [1/5] Processando: Ana Clara Mendes
2026-01-15 10:30:00 [INFO]   ↳ Perfil: Intermediário
2026-01-15 10:30:01 [INFO]   ↳ Mensagem: Ana, seu saldo demonstra uma boa base financeira!...
...
2026-01-15 10:30:10 [INFO] ─── LOAD ────────────────────────────────────────────
2026-01-15 10:30:10 [INFO] ✓ JSON salvo em: output/usuarios_enriquecidos.json
2026-01-15 10:30:10 [INFO] ✓ CSV  salvo em: output/usuarios_enriquecidos.csv
2026-01-15 10:30:10 [INFO] Pipeline finalizado em 12.34s  ✅
```

---

## 🧪 Formato dos Dados

### Entrada (`data/usuarios.csv`)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | Identificador único |
| `nome` | str | Nome completo do cliente |
| `conta` | str | Número da conta |
| `cartao` | str | Bandeira e final do cartão |
| `saldo` | float | Saldo em conta (R$) |
| `limite_credito` | float | Limite do cartão (R$) |

### Saída (`output/usuarios_enriquecidos.json`)
Todos os campos de entrada **mais**:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `perfil_financeiro` | str | `Premium` / `Intermediário` / `Iniciante` |
| `mensagem_ia` | str | Mensagem personalizada gerada pela IA |
| `status_processamento` | str | `sucesso` / `erro: ...` / `rate_limit` |

---

## 🏗️ Arquitetura de Decisão: Classificação de Perfil

```python
def _classificar_perfil(saldo: float, limite: float) -> str:
    utilizacao = (limite - saldo) / limite   # % de limite disponível
    if saldo > 4000 and utilizacao < 0.3:
        return "Premium"          # Alto saldo + baixa utilização
    elif saldo > 1000:
        return "Intermediário"    # Saldo razoável
    return "Iniciante"            # Saldo baixo
```

---

## 🧠 Conceitos ETL Aplicados

| Etapa | Técnica | Motivo |
|-------|---------|--------|
| **Extract** | Validação de schema antes da ingestão | *Fail fast*: detectar erros cedo |
| **Transform** | Enriquecimento com IA Generativa | Agregar valor aos dados brutos |
| **Transform** | Tratamento de erro por registro | Pipeline resiliente |
| **Load** | JSON + CSV simultâneos | Suporte a diferentes consumidores |

---

## 📦 requirements.txt

```
anthropic>=0.34.0
pandas>=2.0.0
python-dotenv>=1.0.0
jupyter>=1.0.0
```

---

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças maiores, abra uma *issue* primeiro.

---

## 👤 Autor

Desenvolvido por Lucas Vieira como parte do desafio **DIO × TOTVS — Fundamentos de Engenharia de Dados e Machine Learning**.

---

## 📄 Licença

Este projeto está sob a licença MIT.