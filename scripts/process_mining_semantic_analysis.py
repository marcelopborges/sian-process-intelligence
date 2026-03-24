#!/usr/bin/env python3
"""
Análise semântica de Process Mining — Contas a Pagar (Protheus).

Foco:
- Separar fluxos COM_SE5 (pagamento bancário real) vs SEM_SE5 (baixa operacional).
- DFG filtrado por frequência (reduzir ruído).
- Heuristics Net (dependências reais).
- Process Tree simplificado (variantes dominantes).
- Comparação lado a lado COM_SE5 vs SEM_SE5.
- Caminho dominante e classificação semântica (pagamento real / baixa manual / incompleto).

Uso:
  python scripts/process_mining_semantic_analysis.py [caminho_event_log.parquet]

Prefere cp_event_log_semantic.parquet quando disponível (trilhas já ancoradas em TITULO_CRIADO).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
# Para importar helpers do outro script de process mining
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUTPUT_DIR = REPO_ROOT / "output" / "process_mining"
ACTIVITIES = {
    "TITULO_CRIADO",
    "EVENTO_FINANCEIRO_GERADO",
    "TITULO_LIBERADO",
    "LANCAMENTO_CONTABIL",
    "PAGAMENTO_REALIZADO",
    "BAIXA_SEM_SE5",
}


def _ensure_pm4py_format(df):
    """Garante colunas PM4Py: case:concept:name, concept:name, time:timestamp."""
    import pandas as pd
    import pm4py

    rename = {}
    if "case_id" in df.columns and "case:concept:name" not in df.columns:
        rename["case_id"] = "case:concept:name"
    if "activity" in df.columns and "concept:name" not in df.columns:
        rename["activity"] = "concept:name"
    for ts_col in ("timestamp", "event_timestamp_original", "event_timestamp_semantic"):
        if ts_col in df.columns and "time:timestamp" not in df.columns:
            rename[ts_col] = "time:timestamp"
            break
    if rename:
        df = df.rename(columns=rename)
    if "time:timestamp" in df.columns:
        df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], errors="coerce")
        df = df.dropna(subset=["time:timestamp"])
    if "concept:name" not in df.columns or "case:concept:name" not in df.columns:
        raise ValueError("Log precisa de case_id, activity e timestamp.")
    df = df[df["concept:name"].astype(str).str.strip().isin(ACTIVITIES)]
    df = pm4py.format_dataframe(
        df,
        case_id="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    return df


def add_segment(log_df):
    """Adiciona coluna segment: COM_SE5 (tem PAGAMENTO_REALIZADO) ou SEM_SE5 (tem BAIXA_SEM_SE5)."""
    import pandas as pd

    case_col = "case:concept:name"
    act_col = "concept:name"
    has_pago = set(
        log_df[log_df[act_col] == "PAGAMENTO_REALIZADO"][case_col].dropna().astype(str)
    )
    has_baixa = set(
        log_df[log_df[act_col] == "BAIXA_SEM_SE5"][case_col].dropna().astype(str)
    )
    def seg(cid):
        c = str(cid)
        if c in has_pago:
            return "COM_SE5"
        if c in has_baixa:
            return "SEM_SE5"
        return "INCOMPLETO"

    log_df = log_df.copy()
    log_df["segment"] = log_df[case_col].map(seg)
    return log_df


def load_log(parquet_path: Path):
    """Carrega Parquet e retorna DataFrame no formato PM4Py com segment."""
    import pandas as pd

    df = pd.read_parquet(parquet_path)
    df = _ensure_pm4py_format(df)
    df = add_segment(df)
    return df


def filter_by_variant(log_df, variant_activities: list[str]):
    """Mantém apenas casos que seguem exatamente a variante (ordem de atividades)."""
    import pm4py

    variants = pm4py.get_variants(log_df)
    if not hasattr(variants, "items"):
        return log_df
    # variant é tuple de atividades
    target = tuple(variant_activities)
    if target not in variants:
        return log_df.iloc[0:0]
    trace_indices = variants[target]
    if not trace_indices:
        return log_df.iloc[0:0]
    # Em PM4Py 2.7 get_variants pode retornar list de trace index
    try:
        cases = set()
        for idx in trace_indices:
            if hasattr(log_df, "index"):
                # DataFrame: precisamos dos case_ids da variante
                pass
        # Abordagem simples: filtrar por variant via pm4py.filter_variants
        return pm4py.filter_variants(log_df, [list(variant_activities)])
    except Exception:
        return log_df


def get_dfg_filtered_by_frequency(log_df, min_edge_ratio: float = 0.01):
    """
    DFG mantendo apenas arcos com frequência >= min_edge_ratio do arco mais frequente.
    Reduz ruído para visualização executiva.
    """
    import pm4py

    dfg, start_activities, end_activities = pm4py.discover_dfg(log_df)
    if not dfg:
        return dfg, start_activities, end_activities
    max_count = max(dfg.values())
    threshold = max(min_edge_ratio * max_count, 1)
    filtered = {k: v for k, v in dfg.items() if v >= threshold}
    return filtered, start_activities, end_activities


def run_com_se5_vs_sem_se5(log_df, output_dir: Path):
    """Gera DFG e Heuristics Net para COM_SE5 e SEM_SE5 separadamente."""
    import pm4py

    output_dir.mkdir(parents=True, exist_ok=True)

    for segment, label in [("COM_SE5", "Com SE5 (pagamento bancário)"), ("SEM_SE5", "Sem SE5 (baixa operacional)")]:
        sub = log_df[log_df["segment"] == segment].copy()
        if sub.empty:
            print(f"  [{segment}] Sem casos.")
            continue
        n_cases = sub["case:concept:name"].nunique()
        print(f"  [{segment}] {n_cases:,} casos — {label}")

        # DFG
        dfg, start_a, end_a = pm4py.discover_dfg(sub)
        out_dfg = output_dir / f"dfg_{segment.lower()}.png"
        try:
            gviz = pm4py.visualization.dfg.visualizer.apply(
                dfg, log=sub, variant=pm4py.visualization.dfg.visualizer.Variants.FREQUENCY
            )
            pm4py.visualization.dfg.visualizer.save(gviz, str(out_dfg))
            print(f"    DFG: {out_dfg}")
        except Exception as e:
            if "dot" in str(e).lower() or "graphviz" in str(e).lower():
                try:
                    from process_mining_analysis import _save_dfg_matplotlib
                    _save_dfg_matplotlib(dfg, start_a, end_a, out_dfg)
                except ImportError:
                    print(f"    DFG (matplotlib fallback): import falhou.")
            else:
                print(f"    DFG falhou: {e}")

        # Heuristics Net
        try:
            heu_net = pm4py.discover_heuristics_net(sub)
            out_heu = output_dir / f"heuristics_net_{segment.lower()}.png"
            try:
                gviz = pm4py.visualization.heuristics_net.visualizer.apply(heu_net)
                pm4py.visualization.heuristics_net.visualizer.save(gviz, str(out_heu))
                print(f"    Heuristics Net: {out_heu}")
            except Exception as e2:
                if "dot" in str(e2).lower():
                    print(f"    Heuristics Net (salvar PNG): Graphviz não disponível.")
                else:
                    print(f"    Heuristics Net: {e2}")
        except Exception as e:
            print(f"    Heuristics Net discovery: {e}")


def run_dfg_filtered(log_df, output_dir: Path, min_ratio: float = 0.02):
    """DFG com filtro de frequência (arcos pouco usados removidos)."""
    import pm4py

    output_dir.mkdir(parents=True, exist_ok=True)
    dfg, start_a, end_a = get_dfg_filtered_by_frequency(log_df, min_edge_ratio=min_ratio)
    print(f"  DFG filtrado (ratio >= {min_ratio}): {len(dfg)} arcos")
    out_path = output_dir / "dfg_filtered_frequency.png"
    try:
        gviz = pm4py.visualization.dfg.visualizer.apply(
            dfg, log=log_df, variant=pm4py.visualization.dfg.visualizer.Variants.FREQUENCY
        )
        pm4py.visualization.dfg.visualizer.save(gviz, str(out_path))
        print(f"  Salvo: {out_path}")
    except Exception as e:
        if "dot" in str(e).lower():
            try:
                from process_mining_analysis import _save_dfg_matplotlib
                _save_dfg_matplotlib(dfg, start_a, end_a, out_path)
            except ImportError:
                pass
        else:
            print(f"  Falha: {e}")


def run_dominant_path_process_tree(log_df, output_dir: Path, coverage: float = 0.80):
    """Process tree apenas com variantes que cobrem `coverage` dos casos (reduz overfitting)."""
    import pm4py

    variants = pm4py.get_variants(log_df)
    if not hasattr(variants, "items"):
        print("  Variantes: formato não suportado.")
        return
    total = sum(len(v) if isinstance(v, (list, tuple)) else v for v in variants.values())
    sorted_v = sorted(
        variants.items(),
        key=lambda x: -(len(x[1]) if isinstance(x[1], (list, tuple)) else x[1]),
    )
    cum = 0
    dominant_variants = []
    for var, traces in sorted_v:
        n = len(traces) if isinstance(traces, (list, tuple)) else traces
        cum += n
        dominant_variants.append(var)
        if total and cum / total >= coverage:
            break
    # filter_variants: lista de variantes (cada uma é lista de atividades)
    variants_as_lists = [list(v) for v in dominant_variants]
    try:
        filtered = pm4py.filter_variants(log_df, variants_as_lists)
    except (TypeError, Exception):
        try:
            from pm4py.algo.filtering.pandas.variants import variants_filter
            filtered = variants_filter.apply(log_df, variants_as_lists)
        except Exception:
            filtered = log_df.iloc[0:0]
    if filtered.empty and len(dominant_variants) > 0:
        # Fallback: usar só a variante top 1
        try:
            filtered = pm4py.filter_variants(log_df, [list(dominant_variants[0])])
        except Exception:
            filtered = log_df
    if filtered.empty:
        print("  Nenhum caso após filtro de variantes dominantes; usando log completo.")
        filtered = log_df
    print(f"  Variantes dominantes (cobertura {coverage:.0%}): {len(dominant_variants)} variantes, {len(filtered)} eventos")
    tree = pm4py.discover_process_tree_inductive(filtered)
    out_path = output_dir / "process_tree_dominant.png"
    try:
        gviz = pm4py.visualization.process_tree.visualizer.apply(tree)
        pm4py.visualization.process_tree.visualizer.save(gviz, str(out_path))
        print(f"  Process tree (dominante): {out_path}")
    except Exception as e:
        if "dot" in str(e).lower():
            try:
                from process_mining_analysis import _save_process_tree_matplotlib
                _save_process_tree_matplotlib(tree, out_path)
            except ImportError:
                pass
        else:
            print(f"  Falha: {e}")


def run_semantic_classification(log_df):
    """Classifica caminhos por segmento do caso: COM_SE5 = pagamento real, SEM_SE5 = baixa operacional, INCOMPLETO = anômalo."""
    import pm4py

    print("\n--- Classificação semântica dos caminhos ---")
    # Usar segmento do caso (já definido por PAGAMENTO_REALIZADO vs BAIXA_SEM_SE5)
    for segment, label in [
        ("COM_SE5", "a) Pagamento real (COM_SE5)"),
        ("SEM_SE5", "b) Baixa manual/operacional (SEM_SE5)"),
        ("INCOMPLETO", "c) Incompletos ou anômalos (sem evento final)"),
    ]:
        sub = log_df[log_df["segment"] == segment]
        if sub.empty:
            print(f"  {label}: 0 casos")
            continue
        variants = pm4py.get_variants(sub)
        if not hasattr(variants, "items"):
            print(f"  {label}: {sub['case:concept:name'].nunique():,} casos")
            continue
        items = []
        for var, traces in variants.items():
            path = tuple(var) if isinstance(var, (list, tuple)) else (var,)
            n = len(traces) if isinstance(traces, (list, tuple)) else traces
            items.append((path, n))
        items.sort(key=lambda x: -x[1])
        total_cases = sum(x[1] for x in items)
        print(f"  {label}: {total_cases:,} casos, {len(items)} variantes")

        for (path, cnt) in items[:5]:
            path_str = " → ".join(path) if path else "(vazio)"
            print(f"    [{cnt:,}] {path_str[:75]}{'...' if len(path_str) > 75 else ''}")


def run_inconsistencies(log_df):
    """Resumo para investigação: EVENTO_FINANCEIRO_GERADO isolado, sem TITULO_LIBERADO, ordem BAIXA vs LANCAMENTO."""
    import pandas as pd

    print("\n--- Indicadores para investigação de inconsistências ---")
    case_col = "case:concept:name"
    act_col = "concept:name"
    ts_col = "time:timestamp"

    # Casos com só EVENTO_FINANCEIRO_GERADO (ou variante muito curta)
    variants = set()
    for cid, grp in log_df.groupby(case_col):
        acts = tuple(grp.sort_values(ts_col)[act_col].tolist())
        variants.add(acts)
    only_efg = [p for p in variants if p == ("EVENTO_FINANCEIRO_GERADO",)]
    n_only_efg = sum(1 for cid, grp in log_df.groupby(case_col) if tuple(grp.sort_values(ts_col)[act_col].tolist()) == ("EVENTO_FINANCEIRO_GERADO",))
    print(f"  Casos com apenas EVENTO_FINANCEIRO_GERADO: {n_only_efg:,}")

    # Casos que pulam TITULO_LIBERADO (têm LANCAMENTO ou PAGAMENTO/BAIXA mas não TITULO_LIBERADO)
    def has_skip_liberado(grp):
        acts = set(grp[act_col])
        if "LANCAMENTO_CONTABIL" in acts or "PAGAMENTO_REALIZADO" in acts or "BAIXA_SEM_SE5" in acts:
            if "TITULO_LIBERADO" not in acts:
                return True
        return False

    skip = log_df.groupby(case_col).filter(has_skip_liberado)
    n_skip = skip[case_col].nunique() if not skip.empty else 0
    print(f"  Casos que pulam TITULO_LIBERADO (têm lançamento/pagamento/baixa): {n_skip:,}")

    # BAIXA_SEM_SE5 antes vs depois de LANCAMENTO_CONTABIL (por caso)
    baixa_antes = 0
    baixa_depois = 0
    for cid, grp in log_df.groupby(case_col):
        grp = grp.sort_values(ts_col)
        acts = grp[act_col].tolist()
        if "BAIXA_SEM_SE5" not in acts or "LANCAMENTO_CONTABIL" not in acts:
            continue
        pos_baixa = next(i for i, a in enumerate(acts) if a == "BAIXA_SEM_SE5")
        pos_lanc = next(i for i, a in enumerate(acts) if a == "LANCAMENTO_CONTABIL")
        if pos_baixa < pos_lanc:
            baixa_antes += 1
        else:
            baixa_depois += 1
    print(f"  Casos BAIXA_SEM_SE5 antes de LANCAMENTO_CONTABIL: {baixa_antes:,}")
    print(f"  Casos BAIXA_SEM_SE5 depois de LANCAMENTO_CONTABIL: {baixa_depois:,}")


def main():
    parser = argparse.ArgumentParser(description="Análise semântica — Process Mining Contas a Pagar")
    parser.add_argument("event_log", nargs="?", default=None, help="Parquet do event log")
    parser.add_argument("-o", "--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--min-dfg-ratio", type=float, default=0.02, help="Mín. ratio de frequência para arco no DFG filtrado")
    parser.add_argument("--tree-coverage", type=float, default=0.80, help="Cobertura de variantes para process tree dominante")
    args = parser.parse_args()

    if args.event_log:
        path = Path(args.event_log)
    else:
        for p in [REPO_ROOT / "data" / "marts" / "cp_event_log_semantic.parquet", REPO_ROOT / "data" / "marts" / "event_log.parquet", Path("event_log.parquet")]:
            if p.exists():
                path = p
                break
        else:
            print("ERRO: Nenhum event log encontrado. Informe o caminho do Parquet.")
            sys.exit(1)

    print("=== Análise semântica — Process Mining ===\n")
    print(f"  Log: {path}")

    try:
        log_df = load_log(path)
    except Exception as e:
        print(f"ERRO ao carregar: {e}")
        sys.exit(1)

    n_events = len(log_df)
    n_cases = log_df["case:concept:name"].nunique()
    print(f"  Eventos: {n_events:,} | Casos: {n_cases:,}")
    for seg in ("COM_SE5", "SEM_SE5", "INCOMPLETO"):
        cases_seg = log_df[log_df["segment"] == seg]["case:concept:name"].nunique()
        print(f"  Segmento {seg}: {cases_seg:,} casos")

    out = Path(args.output_dir)

    print("\n--- 1. Fluxos COM_SE5 vs SEM_SE5 (DFG + Heuristics Net) ---")
    run_com_se5_vs_sem_se5(log_df, out)

    print("\n--- 2. DFG filtrado por frequência ---")
    run_dfg_filtered(log_df, out, min_ratio=args.min_dfg_ratio)

    print("\n--- 3. Process Tree (variantes dominantes) ---")
    run_dominant_path_process_tree(log_df, out, coverage=args.tree_coverage)

    run_semantic_classification(log_df)
    run_inconsistencies(log_df)

    print("\n=== Concluído ===")
    print(f"  Saídas: {out}")


if __name__ == "__main__":
    main()
