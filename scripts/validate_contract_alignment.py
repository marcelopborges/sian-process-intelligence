#!/usr/bin/env python3
"""
Validador de aderência ao contrato de Process Intelligence — Contas a Pagar.

Analisa modelos dbt em dbt/models/ contra o contrato em
docs/contracts/contas_a_pagar_process_intelligence.md.

Uso:
    python scripts/validate_contract_alignment.py

Exit code: 0 se apenas warnings; 1 se houver pelo menos um ERRO.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Configuração de caminhos (relativo à raiz do repositório)
# -----------------------------------------------------------------------------

# Raiz do repo: script em scripts/validate_contract_alignment.py
REPO_ROOT = Path(__file__).resolve().parent.parent
DBT_MODELS_DIR = REPO_ROOT / "dbt" / "models"

# Nomes dos arquivos obrigatórios (procurados recursivamente em dbt/models/)
REQUIRED_MART_FILES = [
    "mart_cp_case_base.sql",
    "mart_cp_event_log.sql",
]

# Eventos obrigatórios no event log (presença esperada no arquivo)
REQUIRED_EVENTS = [
    "TITULO_CRIADO",
    "TITULO_LIBERADO",
    "EVENTO_FINANCEIRO_GERADO",
    "LANCAMENTO_CONTABIL",
    "PAGAMENTO_REALIZADO",
    "BAIXA_SEM_SE5",
    "TITULO_CANCELADO",
]

# Campos obrigatórios no event log
REQUIRED_EVENT_LOG_FIELDS = [
    "case_id",
    "activity",
    "event_timestamp_adjusted",
    "event_order",
    "timestamp_confiabilidade",
]

# Valores esperados de timestamp_confiabilidade
REQUIRED_CONFIABILIDADE_VALUES = ["NEGOCIO", "TECNICO"]

# Componentes da chave do caso (E2_*) — devem aparecer no case_base (ou via ref ao int que os expõe)
CASE_ID_KEY_FIELDS = [
    "E2_FILIAL",
    "E2_PREFIXO",
    "E2_NUM",
    "E2_PARCELA",
    "E2_TIPO",
    "E2_FORNECE",
    "E2_LOJA",
]

# Padrão COALESCE suspeito: COALESCE( algo SE5 , algo SE2 ) — pode mascarar ausência de SE5
COALESCE_SUSPICIOUS_PATTERN = re.compile(
    r"COALESCE\s*\([^)]*SE5[^)]*,[^)]*SE2[^)]*\)",
    re.IGNORECASE | re.DOTALL,
)


def find_sql_files(base_dir: Path) -> list[Path]:
    """Retorna todos os arquivos .sql sob base_dir (recursivo)."""
    if not base_dir.is_dir():
        return []
    return list(base_dir.rglob("*.sql"))


def find_mart_file(name: str) -> Path | None:
    """Retorna o primeiro path que termina com name sob dbt/models/, ou None."""
    for path in find_sql_files(DBT_MODELS_DIR):
        if path.name == name:
            return path
    return None


def read_file_content(path: Path | None) -> str:
    """Retorna o conteúdo do arquivo ou string vazia se path for None ou arquivo inexistente."""
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


# -----------------------------------------------------------------------------
# Validações (cada função retorna lista de (tipo, mensagem) — tipo: "ok" | "erro" | "warning")
# -----------------------------------------------------------------------------


def check_required_files(report: list[tuple[str, str]]) -> None:
    """A. Arquivos obrigatórios: mart_cp_case_base.sql e mart_cp_event_log.sql."""
    for name in REQUIRED_MART_FILES:
        path = find_mart_file(name)
        if path is None:
            report.append(("erro", f"{name} não encontrado"))
        else:
            report.append(("ok", f"{name} encontrado"))


def check_no_current_date_in_case_base(report: list[tuple[str, str]]) -> None:
    """B. mart_cp_case_base.sql NÃO pode conter CURRENT_DATE()."""
    path = find_mart_file("mart_cp_case_base.sql")
    if path is None:
        return  # já falhou em check_required_files
    content = read_file_content(path)
    if "CURRENT_DATE()" in content or "current_date()" in content:
        report.append(("erro", "CURRENT_DATE() encontrado no case_base"))
    else:
        report.append(("ok", "case_base sem CURRENT_DATE()"))


def check_no_baixa_manual_in_any_sql(report: list[tuple[str, str]]) -> None:
    """C. Nenhum SQL pode usar BAIXA_MANUAL como nome de evento de saída; permitido só como valor de origem mapeado para BAIXA_SEM_SE5."""
    found_in: list[str] = []
    for path in find_sql_files(DBT_MODELS_DIR):
        content = read_file_content(path)
        if "BAIXA_MANUAL" not in content:
            continue
        # Permitir quando for mapeamento origem -> BAIXA_SEM_SE5 (ex.: when x in ('BAIXA_MANUAL','BAIXA') then 'BAIXA_SEM_SE5')
        lines = content.split("\n")
        allowed = False
        for i, line in enumerate(lines):
            if "BAIXA_MANUAL" in line and "BAIXA_SEM_SE5" in line:
                allowed = True
                break
            if "BAIXA_MANUAL" in line and i + 1 < len(lines) and "BAIXA_SEM_SE5" in lines[i + 1]:
                allowed = True
                break
        if not allowed:
            found_in.append(path.name)
    if found_in:
        report.append(
            ("erro", f"BAIXA_MANUAL encontrado em: {', '.join(found_in)}. Use BAIXA_SEM_SE5.")
        )
    else:
        report.append(("ok", "Nenhum uso de BAIXA_MANUAL como evento de saída (esperado: BAIXA_SEM_SE5)"))


def check_required_events_in_event_log(report: list[tuple[str, str]]) -> None:
    """D. mart_cp_event_log.sql deve referenciar os eventos obrigatórios (WARNING se faltar)."""
    path = find_mart_file("mart_cp_event_log.sql")
    if path is None:
        return
    content = read_file_content(path)
    missing = [ev for ev in REQUIRED_EVENTS if ev not in content]
    if missing:
        report.append(
            ("warning", f"Eventos não encontrados no event_log: {', '.join(missing)}")
        )
    else:
        report.append(("ok", "Todos os eventos obrigatórios presentes no event_log"))


def check_required_fields_in_event_log(report: list[tuple[str, str]]) -> None:
    """E. mart_cp_event_log.sql deve conter os campos obrigatórios do event log."""
    path = find_mart_file("mart_cp_event_log.sql")
    if path is None:
        return
    content = read_file_content(path)
    missing = [f for f in REQUIRED_EVENT_LOG_FIELDS if f not in content]
    if missing:
        report.append(
            ("erro", f"Campos obrigatórios ausentes no event_log: {', '.join(missing)}")
        )
    else:
        report.append(("ok", "Campos obrigatórios presentes no event_log"))


def check_timestamp_confiabilidade_values(report: list[tuple[str, str]]) -> None:
    """F. Verificar se aparecem os valores NEGOCIO e TECNICO (WARNING se não)."""
    path = find_mart_file("mart_cp_event_log.sql")
    if path is None:
        return
    content = read_file_content(path)
    missing = [v for v in REQUIRED_CONFIABILIDADE_VALUES if v not in content]
    if missing:
        report.append(
            ("warning", f"Valores de timestamp_confiabilidade não encontrados: {', '.join(missing)}")
        )
    else:
        report.append(("ok", "Valores NEGOCIO e TECNICO presentes"))


def check_coalesce_suspicious(report: list[tuple[str, str]]) -> None:
    """G. COALESCE(.*SE5.*,.*SE2.*) — possível mascaramento de ausência de SE5. Ignora se documentado como valor observado vs inferido (contrato)."""
    found_in: list[str] = []
    for path in find_sql_files(DBT_MODELS_DIR):
        content = read_file_content(path)
        if not COALESCE_SUSPICIOUS_PATTERN.search(content):
            continue
        # Contrato: valor observado (SE5) vs inferido (SE2) é explícito no case_base
        if "observado" in content.lower() and "inferido" in content.lower():
            continue
        found_in.append(path.name)
    if found_in:
        report.append(
            (
                "warning",
                f"Possível mascaramento de ausência de SE5 (COALESCE SE5/SE2) em: {', '.join(found_in)}",
            )
        )
    else:
        report.append(("ok", "Nenhum COALESCE suspeito (SE5, SE2) encontrado"))


def check_case_id_structure_in_case_base(report: list[tuple[str, str]]) -> None:
    """H. case_base (mart ou int_cp_se2_base) deve referenciar os 7 campos da chave (E2_* ou e2_*)."""
    # O case_id é construído no int_cp_se2_base; o mart pode só usar ref(). Verificamos a camada.
    content_mart = read_file_content(find_mart_file("mart_cp_case_base.sql"))
    path_int = find_mart_file("int_cp_se2_base.sql")
    content_int = read_file_content(path_int)
    content = content_mart + "\n" + content_int
    content_lower = content.lower()
    missing = []
    for field in CASE_ID_KEY_FIELDS:
        alias_lower = field.lower()  # e2_filial, e2_prefixo, ...
        if field not in content and alias_lower not in content_lower:
            missing.append(field)
    if missing:
        report.append(
            ("erro", f"Componentes da chave do caso ausentes no case_base: {', '.join(missing)}")
        )
    else:
        report.append(("ok", "Estrutura do case_id (7 campos E2_*) presente no case_base"))


# -----------------------------------------------------------------------------
# Orquestração e saída
# -----------------------------------------------------------------------------


def run_all_checks() -> list[tuple[str, str]]:
    """Executa todas as validações e retorna lista de (tipo, mensagem)."""
    report: list[tuple[str, str]] = []
    check_required_files(report)
    check_no_current_date_in_case_base(report)
    check_no_baixa_manual_in_any_sql(report)
    check_required_events_in_event_log(report)
    check_required_fields_in_event_log(report)
    check_timestamp_confiabilidade_values(report)
    check_coalesce_suspicious(report)
    check_case_id_structure_in_case_base(report)
    return report


def main() -> int:
    """Ponto de entrada CLI. Imprime relatório e retorna exit code."""
    if not DBT_MODELS_DIR.is_dir():
        print(f"[ERRO] Diretório não encontrado: {DBT_MODELS_DIR}")
        return 1

    report = run_all_checks()
    errors = 0
    warnings = 0

    for kind, msg in report:
        if kind == "ok":
            print(f"[OK] {msg}")
        elif kind == "erro":
            print(f"[ERRO] {msg}")
            errors += 1
        else:
            print(f"[WARNING] {msg}")
            warnings += 1

    print()
    print("Resumo final:")
    print(f"  ERROS: {errors}")
    print(f"  WARNINGS: {warnings}")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
