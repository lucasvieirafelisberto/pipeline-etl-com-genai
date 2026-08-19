"""
====================================================================
 Pipeline ETL com IA Generativa — DIO TOTVS 2026 | Fundamentos de Engenharia de Dados e Machine Learning
====================================================================
Autor  : Lucas Vieira Felisberto
Versão : 2.0.0
Python : 3.10+

Fluxo:
    [CSV] ──► EXTRACT ──► TRANSFORM (IA Generativa) ──► LOAD [JSON/CSV]

Dependências:
    pip install anthropic pandas python-dotenv
====================================================================
"""

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import anthropic
import pandas as pd
from dotenv import load_dotenv

# ─── Configuração de logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

load_dotenv()

# ─── Constantes ─────────────────────────────────────────────────────────────
INPUT_PATH  = Path("data/usuarios.csv")
OUTPUT_JSON = Path("output/usuarios_enriquecidos.json")
OUTPUT_CSV  = Path("output/usuarios_enriquecidos.csv")
MODEL       = "claude-sonnet-4-20250514"
MAX_TOKENS  = 300
RATE_LIMIT_SLEEP = 1  # segundos entre chamadas à API


# ──────────────────────────────────────────────────────────────────────────────
# MODELOS DE DADOS
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class Usuario:
    """Representa um cliente bancário após a extração."""
    id: int
    nome: str
    conta: str
    cartao: str
    saldo: float
    limite_credito: float
    mensagem_ia: Optional[str] = None
    perfil_financeiro: Optional[str] = None
    status_processamento: str = "pendente"


# ──────────────────────────────────────────────────────────────────────────────
# ETAPA 1 — EXTRACT
# ──────────────────────────────────────────────────────────────────────────────
def extract(caminho: Path) -> list[Usuario]:
    """
    Lê o arquivo CSV e converte cada linha em um objeto Usuario.

    Args:
        caminho: Caminho para o arquivo CSV de entrada.

    Returns:
        Lista de objetos Usuario populados com os dados brutos.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        ValueError: Se colunas obrigatórias estiverem ausentes.
    """
    log.info("─── EXTRACT ───────────────────────────────────────────────────")
    log.info("Lendo arquivo: %s", caminho)

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho)

    colunas_obrigatorias = {"id", "nome", "conta", "cartao", "saldo", "limite_credito"}
    faltando = colunas_obrigatorias - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes no CSV: {faltando}")

    usuarios = [
        Usuario(
            id=int(row["id"]),
            nome=str(row["nome"]),
            conta=str(row["conta"]),
            cartao=str(row["cartao"]),
            saldo=float(row["saldo"]),
            limite_credito=float(row["limite_credito"]),
        )
        for _, row in df.iterrows()
    ]

    log.info("✓ %d usuários extraídos com sucesso.", len(usuarios))
    return usuarios


# ──────────────────────────────────────────────────────────────────────────────
# ETAPA 2 — TRANSFORM
# ──────────────────────────────────────────────────────────────────────────────
def _classificar_perfil(saldo: float, limite: float) -> str:
    """Classificação de perfil financeiro baseada em regras de negócio."""
    utilizacao = (limite - saldo) / limite if limite > 0 else 0
    if saldo > 4000 and utilizacao < 0.3:
        return "Premium"
    elif saldo > 1000:
        return "Intermediário"
    else:
        return "Iniciante"


def _gerar_mensagem_ia(cliente: anthropic.Anthropic, usuario: Usuario) -> str:
    """
    Chama a API da IA Generativa para criar uma mensagem personalizada.

    A mensagem leva em conta o perfil financeiro do usuário e deve ser
    motivadora, respeitosa e orientada a boas práticas financeiras.

    Args:
        cliente: Instância do cliente Anthropic.
        usuario: Dados do usuário para contextualizar a mensagem.

    Returns:
        Mensagem personalizada gerada pela IA.
    """
    prompt = f"""Você é um assistente financeiro especialista em engenharia de dados.
Gere uma mensagem curta (máx. 2 frases), personalizada e motivadora para o seguinte cliente:

- Nome: {usuario.nome}
- Perfil financeiro: {usuario.perfil_financeiro}
- Saldo atual: R$ {usuario.saldo:,.2f}
- Limite de crédito: R$ {usuario.limite_credito:,.2f}

A mensagem deve ser direta, amigável e incluir uma dica ou incentivo financeiro relevante ao perfil.
Responda APENAS com a mensagem, sem saudação formal nem assinatura."""

    resposta = cliente.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return resposta.content[0].text.strip()


def transform(usuarios: list[Usuario]) -> list[Usuario]:
    """
    Enriquece cada usuário com:
      1. Classificação de perfil financeiro (regra de negócio local)
      2. Mensagem personalizada gerada por IA Generativa

    Args:
        usuarios: Lista de usuários extraídos.

    Returns:
        Lista de usuários com campos enriquecidos preenchidos.
    """
    log.info("─── TRANSFORM ─────────────────────────────────────────────────")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variável de ambiente ANTHROPIC_API_KEY não definida. "
            "Crie um arquivo .env com: ANTHROPIC_API_KEY=sk-ant-..."
        )

    cliente = anthropic.Anthropic(api_key=api_key)
    total = len(usuarios)

    for i, usuario in enumerate(usuarios, 1):
        log.info("[%d/%d] Processando: %s", i, total, usuario.nome)
        try:
            # Passo 1 — Classificação por regra local (rápido, sem I/O)
            usuario.perfil_financeiro = _classificar_perfil(
                usuario.saldo, usuario.limite_credito
            )
            log.info("  ↳ Perfil: %s", usuario.perfil_financeiro)

            # Passo 2 — Chamada à IA Generativa
            usuario.mensagem_ia = _gerar_mensagem_ia(cliente, usuario)
            log.info("  ↳ Mensagem: %s", usuario.mensagem_ia)

            usuario.status_processamento = "sucesso"

        except anthropic.RateLimitError:
            log.warning("  ↳ Rate limit atingido. Aguardando 10 segundos...")
            time.sleep(10)
            usuario.mensagem_ia = "[geração pausada — rate limit]"
            usuario.status_processamento = "rate_limit"

        except Exception as exc:  # noqa: BLE001
            log.error("  ↳ Erro ao processar %s: %s", usuario.nome, exc)
            usuario.mensagem_ia = "[erro na geração]"
            usuario.status_processamento = f"erro: {exc}"

        finally:
            time.sleep(RATE_LIMIT_SLEEP)

    sucessos = sum(1 for u in usuarios if u.status_processamento == "sucesso")
    log.info("✓ Transform concluído: %d/%d com sucesso.", sucessos, total)
    return usuarios


# ──────────────────────────────────────────────────────────────────────────────
# ETAPA 3 — LOAD
# ──────────────────────────────────────────────────────────────────────────────
def load(usuarios: list[Usuario]) -> None:
    """
    Persiste os dados enriquecidos em dois formatos:
      - JSON  →  leitura humana / integração com APIs
      - CSV   →  ingestão em bancos relacionais / BI

    Args:
        usuarios: Lista de usuários transformados.
    """
    log.info("─── LOAD ───────────────────────────────────────────────────────")
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    # ── JSON ──────────────────────────────────────────────────────────────────
    registros = [asdict(u) for u in usuarios]
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    log.info("✓ JSON salvo em: %s", OUTPUT_JSON)

    # ── CSV ───────────────────────────────────────────────────────────────────
    df = pd.DataFrame(registros)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    log.info("✓ CSV  salvo em: %s", OUTPUT_CSV)


# ──────────────────────────────────────────────────────────────────────────────
# ORQUESTRADOR
# ──────────────────────────────────────────────────────────────────────────────
def run_pipeline() -> None:
    """
    Ponto de entrada principal. Orquestra as três etapas do pipeline ETL:
    Extract → Transform → Load.
    """
    log.info("=" * 65)
    log.info("  PIPELINE ETL — IA Generativa  |  DIO TOTVS 2026 | Engenharia de Dados e ML")
    log.info("=" * 65)

    start = time.perf_counter()

    # 1️⃣  Extract
    usuarios = extract(INPUT_PATH)

    # 2️⃣  Transform
    usuarios = transform(usuarios)

    # 3️⃣  Load
    load(usuarios)

    elapsed = time.perf_counter() - start
    log.info("=" * 65)
    log.info("  Pipeline finalizado em %.2fs  ✅", elapsed)
    log.info("=" * 65)


if __name__ == "__main__":
    run_pipeline()
