#!/usr/bin/env python3
"""
Análise de Process Mining para Contas a Pagar (Protheus).

Carrega event_log.parquet, padroniza para PM4Py e gera:
- Descoberta do processo (Inductive Miner, process tree)
- Directly-Follows Graph (DFG) com frequências
- Top 10 variantes (caminhos)
- Performance: tempo TITULO_CRIADO → PAGAMENTO_REALIZADO e → BAIXA_SEM_SE5
- Log filtrado (apenas atividades principais) e visualização
- Análise segmentada: PAGO (com SE5) vs PAGO_SEM_SE5

Uso:
  python scripts/process_mining_analysis.py [caminho_event_log.parquet]

Se não informar caminho, usa event_log.parquet no diretório atual ou
data/marts/event_log.parquet / data/marts/cp_event_log.parquet.

Requisitos opcionais (para imagens com layout Graphviz):
  - Fedora:  sudo dnf install graphviz
  - Ubuntu:   sudo apt install graphviz
  - Conda:    conda install -c conda-forge graphviz
  Sem Graphviz, o script gera as imagens com matplotlib (fallback).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# -----------------------------------------------------------------------------
# Constantes
# -----------------------------------------------------------------------------

# Atividades consideradas "principais" para o log filtrado (redução de ruído)
ACTIVIDADES_PRINCIPAIS = {
    "TITULO_CRIADO",
    "EVENTO_FINANCEIRO_GERADO",
    "LANCAMENTO_CONTABIL",
    "PAGAMENTO_REALIZADO",
    "BAIXA_SEM_SE5",
}

# Colunas possíveis no parquet (mapeamento flexível)
CASE_ID_COLUMNS = ("case_id", "case:concept:name")
ACTIVITY_COLUMNS = ("activity", "concept:name")
TIMESTAMP_COLUMNS = (
    "timestamp",
    "time:timestamp",
    "event_timestamp_original",
    "event_timestamp_adjusted",
)
STATUS_MACRO_COLUMNS = ("status_macro", "status")

# Diretório de saída para visualizações
OUTPUT_DIR = REPO_ROOT / "output" / "process_mining"


def _save_dfg_matplotlib(dfg, start_activities, end_activities, out_path: Path):
    """
    Fallback: desenha o DFG com networkx + matplotlib e salva em out_path.
    Usado quando Graphviz (dot) não está instalado.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx

    G = nx.DiGraph()
    # Nós especiais início/fim
    G.add_node("__start__", label="START")
    G.add_node("__end__", label="END")
    for (a, b), count in dfg.items():
        G.add_node(a, label=a)
        G.add_node(b, label=b)
        G.add_edge(a, b, weight=count)
    for act, count in start_activities.items():
        G.add_edge("__start__", act, weight=count)
    for act, count in end_activities.items():
        G.add_edge(act, "__end__", weight=count)

    if G.number_of_edges() == 0:
        return
    weights = [G.edges[u, v].get("weight", 1) for u, v in G.edges()]
    max_w = max(weights) or 1
    edge_widths = [2 + 4 * (w / max_w) for w in weights]

    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=1200, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=7, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, arrows=True, ax=ax)
    edge_labels = {(u, v): str(d.get("weight", "")) for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, ax=ax)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  (fallback matplotlib) DFG salvo: {out_path}")


def _process_tree_to_nx(tree, G=None, parent_id=None, node_counter=None):
    """Converte process tree do PM4Py em grafo networkx (árvore) para desenho."""
    import networkx as nx

    if G is None:
        G = nx.DiGraph()
        node_counter = [0]
    nid = node_counter[0]
    node_counter[0] += 1
    label = getattr(tree, "label", None) or getattr(tree, "get_label", lambda: None)()
    if label is not None:
        lab = str(label)
    else:
        op = getattr(tree, "operator", None)
        if op is not None:
            lab = str(op).split(".")[-1] if hasattr(op, "split") else str(op)
        else:
            lab = "?"
    G.add_node(nid, label=lab)
    if parent_id is not None:
        G.add_edge(parent_id, nid)
    for child in getattr(tree, "children", []) or []:
        _process_tree_to_nx(child, G, nid, node_counter)
    return G


def _save_process_tree_matplotlib(tree, out_path: Path):
    """
    Fallback: desenha a process tree com networkx + matplotlib (layout hierárquico).
    Usado quando Graphviz (dot) não está instalado.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx

    G = _process_tree_to_nx(tree)
    if G.number_of_nodes() == 0:
        return
    # Layout em camadas (raiz no topo)
    pos = nx.spring_layout(G, k=1.5, iterations=80, seed=42)
    # Ajustar para que raiz fique em cima (raiz = nó 0)
    if 0 in pos:
        root_y = pos[0][1]
        for n in pos:
            pos[n][1] = -pos[n][1] + root_y
    fig, ax = plt.subplots(figsize=(14, 10))
    labels = {n: d.get("label", str(n)) for n, d in G.nodes(data=True)}
    nx.draw_networkx_nodes(G, pos, node_color="lightyellow", node_size=800, ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, ax=ax)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  (fallback matplotlib) Process tree salva: {out_path}")


def _normalize_column(df, possible_names, default_name):
    """Retorna nome da coluna encontrada no DataFrame ou default."""
    for name in possible_names:
        if name in df.columns:
            return name
    return default_name


def load_and_prepare_log(parquet_path: Path):
    """
    Carrega o Parquet do event log e prepara para PM4Py.

    - Detecta colunas case_id, activity e timestamp (nomes flexíveis).
    - Converte timestamp para datetime, remove linhas com timestamp inválido.
    - Remove linhas com case_id ou activity nulos.
    - Padroniza nomes para case:concept:name, concept:name, time:timestamp.

    Returns:
        DataFrame com colunas PM4Py e time:timestamp como datetime64[ns].
    """
    import pandas as pd
    import pm4py

    if not parquet_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {parquet_path}")

    df = pd.read_parquet(parquet_path)

    if df.empty:
        raise ValueError("Event log vazio.")

    # Detectar colunas
    case_col = _normalize_column(df, CASE_ID_COLUMNS, "case_id")
    act_col = _normalize_column(df, ACTIVITY_COLUMNS, "activity")
    ts_col = _normalize_column(df, TIMESTAMP_COLUMNS, "timestamp")

    # Manter apenas colunas necessárias + status_macro se existir (para segmentação)
    use_cols = [case_col, act_col, ts_col]
    status_col = _normalize_column(df, STATUS_MACRO_COLUMNS, None)
    if status_col and status_col in df.columns:
        use_cols.append(status_col)
    use_cols = [c for c in use_cols if c in df.columns]
    df = df[use_cols].copy()

    # Converter timestamp e remover inválidos
    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
    before = len(df)
    df = df.dropna(subset=[ts_col])
    if len(df) < before:
        print(f"  Aviso: {before - len(df)} eventos removidos (timestamp inválido).")

    # Remover eventos sem case_id ou activity
    df = df.dropna(subset=[case_col, act_col])
    df[case_col] = df[case_col].astype(str)
    df[act_col] = df[act_col].astype(str).str.strip()
    df = df[df[act_col] != ""]

    if df.empty:
        raise ValueError("Nenhum evento válido após limpeza.")

    # Formatar para PM4Py (renomeia para case:concept:name, concept:name, time:timestamp)
    df = pm4py.format_dataframe(
        df,
        case_id=case_col,
        activity_key=act_col,
        timestamp_key=ts_col,
    )
    # Padronizar nome da coluna de status para segmentação
    if status_col and status_col in df.columns and status_col != "status_macro":
        df = df.rename(columns={status_col: "status_macro"})

    print(f"  Eventos: {len(df):,} | Casos: {df['case:concept:name'].nunique():,}")
    return df


def run_discovery_process_tree(log_df, output_dir: Path):
    """
    Descoberta do processo com Inductive Miner e visualização da process tree.
    Salva figura em output_dir/process_tree.png.
    """
    import pm4py

    print("\n--- 2.1 Descoberta do processo (Inductive Miner) ---")
    process_tree = pm4py.discover_process_tree_inductive(log_df)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "process_tree.png"
    try:
        gviz = pm4py.visualization.process_tree.visualizer.apply(process_tree)
        pm4py.visualization.process_tree.visualizer.save(gviz, str(out_path))
        print(f"  Process tree salva: {out_path}")
    except Exception as e:
        if "dot" in str(e).lower() or "graphviz" in str(e).lower():
            _save_process_tree_matplotlib(process_tree, out_path)
        else:
            print(f"  Aviso: não foi possível salvar process tree: {e}")
    try:
        pm4py.view_process_tree(process_tree)
    except Exception:
        pass
    return process_tree


def run_dfg(log_df, output_dir: Path):
    """
    Gera Directly-Follows Graph com frequência e salva visualização.
    """
    import pm4py

    print("\n--- 2.2 Directly-Follows Graph (DFG) ---")
    dfg, start_activities, end_activities = pm4py.discover_dfg(log_df)
    print(f"  Arcos (atividade A → B): {len(dfg)}")
    # Mostrar alguns arcos mais frequentes
    sorted_arcs = sorted(dfg.items(), key=lambda x: -x[1])[:10]
    for (a, b), count in sorted_arcs:
        print(f"    {a} → {b}: {count}")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "dfg.png"
    try:
        gviz = pm4py.visualization.dfg.visualizer.apply(
            dfg, log=log_df, variant=pm4py.visualization.dfg.visualizer.Variants.FREQUENCY
        )
        pm4py.visualization.dfg.visualizer.save(gviz, str(out_path))
        print(f"  DFG salvo: {out_path}")
    except Exception as e:
        if "dot" in str(e).lower() or "graphviz" in str(e).lower():
            _save_dfg_matplotlib(dfg, start_activities, end_activities, out_path)
        else:
            print(f"  Aviso: não foi possível salvar DFG: {e}")
    try:
        pm4py.view_dfg(dfg, start_activities, end_activities)
    except Exception:
        pass
    return dfg, start_activities, end_activities


def run_variants(log_df, top_n: int = 10):
    """
    Lista as top_n variantes (caminhos) e quantidade de casos por variante.
    """
    import pm4py

    print(f"\n--- 2.3 Variantes (top {top_n} caminhos) ---")
    variants = pm4py.get_variants(log_df)
    # variants: dict variant_tuple -> list of trace indices (ou count)
    if not hasattr(variants, "items"):
        variant_counts = [(v, 1) for v in variants]
    else:
        variant_counts = []
        for variant, traces in variants.items():
            cnt = len(traces) if isinstance(traces, (list, tuple)) else traces
            variant_counts.append((variant, cnt))
        variant_counts.sort(key=lambda x: -x[1])

    for i, (variant, count) in enumerate(variant_counts[:top_n], 1):
        path_str = " → ".join(variant) if isinstance(variant, (list, tuple)) else str(variant)
        print(f"  {i}. [{count:,} casos] {path_str}")
    print(f"  Total de variantes distintas: {len(variant_counts)}")
    return variant_counts


def run_performance(log_df):
    """
    Tempo médio e mediana entre:
    - TITULO_CRIADO → PAGAMENTO_REALIZADO
    - TITULO_CRIADO → BAIXA_SEM_SE5
    """
    import pandas as pd

    print("\n--- 2.4 Performance (tempo entre eventos) ---")
    case_col = "case:concept:name"
    act_col = "concept:name"
    ts_col = "time:timestamp"

    # Por caso: primeiro timestamp de TITULO_CRIADO
    titulo = (
        log_df[log_df[act_col] == "TITULO_CRIADO"]
        .groupby(case_col)[ts_col]
        .min()
        .reset_index()
    )
    titulo = titulo.rename(columns={ts_col: "ts_inicio"})

    def stats_from_series(s: pd.Series, label: str):
        s = s.dropna()
        s = s[s.dt.total_seconds() >= 0]
        if s.empty:
            print(f"  {label}: sem dados.")
            return
        total_seconds = s.dt.total_seconds()
        media_dias = total_seconds.mean() / (24 * 3600)
        mediana_dias = total_seconds.median() / (24 * 3600)
        print(f"  {label}: média = {media_dias:.1f} dias | mediana = {mediana_dias:.1f} dias (n={len(s):,})")

    # TITULO_CRIADO → PAGAMENTO_REALIZADO
    pagamento = (
        log_df[log_df[act_col] == "PAGAMENTO_REALIZADO"]
        .groupby(case_col)[ts_col]
        .min()
        .reset_index()
    )
    pagamento = pagamento.rename(columns={ts_col: "ts_pago"})
    merge_p = titulo.merge(pagamento, on=case_col, how="inner")
    merge_p["duracao"] = merge_p["ts_pago"] - merge_p["ts_inicio"]
    stats_from_series(merge_p["duracao"], "TITULO_CRIADO → PAGAMENTO_REALIZADO")

    # TITULO_CRIADO → BAIXA_SEM_SE5
    baixa = (
        log_df[log_df[act_col] == "BAIXA_SEM_SE5"]
        .groupby(case_col)[ts_col]
        .min()
        .reset_index()
    )
    baixa = baixa.rename(columns={ts_col: "ts_baixa"})
    merge_b = titulo.merge(baixa, on=case_col, how="inner")
    merge_b["duracao"] = merge_b["ts_baixa"] - merge_b["ts_inicio"]
    stats_from_series(merge_b["duracao"], "TITULO_CRIADO → BAIXA_SEM_SE5")


def filter_main_activities(log_df):
    """Retorna log contendo apenas eventos das atividades principais."""
    return log_df[log_df["concept:name"].isin(ACTIVIDADES_PRINCIPAIS)].copy()


def run_filtered_log_visualization(log_df, output_dir: Path):
    """
    Gera visualização do processo usando apenas atividades principais.
    """
    import pm4py

    print("\n--- 3. Log filtrado (apenas atividades principais) ---")
    filtered = filter_main_activities(log_df)
    if filtered.empty:
        print("  Aviso: nenhum evento após filtro.")
        return
    print(f"  Eventos: {len(filtered):,} | Casos: {filtered['case:concept:name'].nunique():,}")

    process_tree = pm4py.discover_process_tree_inductive(filtered)
    out_path = output_dir / "process_tree_filtered.png"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        gviz = pm4py.visualization.process_tree.visualizer.apply(process_tree)
        pm4py.visualization.process_tree.visualizer.save(gviz, str(out_path))
        print(f"  Process tree (filtrado) salva: {out_path}")
    except Exception as e:
        if "dot" in str(e).lower() or "graphviz" in str(e).lower():
            _save_process_tree_matplotlib(process_tree, out_path)
        else:
            print(f"  Aviso: não foi possível salvar: {e}")
    try:
        pm4py.view_process_tree(process_tree)
    except Exception:
        pass

    dfg, start_activities, end_activities = pm4py.discover_dfg(filtered)
    out_dfg = output_dir / "dfg_filtered.png"
    try:
        gviz = pm4py.visualization.dfg.visualizer.apply(
            dfg, log=filtered, variant=pm4py.visualization.dfg.visualizer.Variants.FREQUENCY
        )
        pm4py.visualization.dfg.visualizer.save(gviz, str(out_dfg))
        print(f"  DFG (filtrado) salvo: {out_dfg}")
    except Exception as e:
        if "dot" in str(e).lower() or "graphviz" in str(e).lower():
            _save_dfg_matplotlib(dfg, start_activities, end_activities, out_dfg)
        else:
            print(f"  Aviso: não foi possível salvar DFG filtrado: {e}")


def infer_status_macro(log_df):
    """
    Se status_macro não existir no log, infere por caso:
    - Presença de PAGAMENTO_REALIZADO → PAGO
    - Presença de BAIXA_SEM_SE5 (e sem PAGAMENTO_REALIZADO) → PAGO_SEM_SE5
    """
    if "status_macro" in log_df.columns:
        return log_df
    case_col = "case:concept:name"
    act_col = "concept:name"
    has_pago = (
        log_df[log_df[act_col] == "PAGAMENTO_REALIZADO"][case_col]
        .unique()
    )
    has_baixa_sem_se5 = (
        log_df[log_df[act_col] == "BAIXA_SEM_SE5"][case_col]
        .unique()
    )
    set_pago = set(has_pago)
    set_baixa = set(has_baixa_sem_se5)
    status_by_case = {}
    for c in log_df[case_col].unique():
        if c in set_pago:
            status_by_case[c] = "PAGO"
        elif c in set_baixa:
            status_by_case[c] = "PAGO_SEM_SE5"
        else:
            status_by_case[c] = "OUTRO"
    log_df = log_df.copy()
    log_df["status_macro"] = log_df[case_col].map(status_by_case)
    return log_df


def run_segmented_analysis(log_df, output_dir: Path):
    """
    Análises separadas para PAGO (com SE5) e PAGO_SEM_SE5.
    Compara caminhos (variantes) e tempo médio.
    """
    import pandas as pd
    import pm4py

    print("\n--- 4. Segmentação por tipo de pagamento ---")
    log_df = infer_status_macro(log_df)

    for segment_name, status_val in [("PAGO (com SE5)", "PAGO"), ("PAGO_SEM_SE5", "PAGO_SEM_SE5")]:
        sub = log_df[log_df["status_macro"] == status_val]
        if sub.empty:
            print(f"  {segment_name}: nenhum caso.")
            continue
        n_cases = sub["case:concept:name"].nunique()
        print(f"  {segment_name}: {n_cases:,} casos")

        # Top 3 variantes
        variants = pm4py.get_variants(sub)
        if hasattr(variants, "items"):
            variant_counts = []
            for v, trs in variants.items():
                cnt = len(trs) if isinstance(trs, (list, tuple)) else trs
                variant_counts.append((v, cnt))
            variant_counts.sort(key=lambda x: -x[1])
        else:
            variant_counts = [(v, 1) for v in variants]
        for i, (variant, count) in enumerate(variant_counts[:3], 1):
            path_str = " → ".join(variant) if isinstance(variant, (list, tuple)) else str(variant)
            print(f"    Variante {i}: [{count:,}] {path_str[:80]}{'...' if len(path_str) > 80 else ''}")

        # Tempo médio TITULO_CRIADO → evento final (PAGAMENTO ou BAIXA)
        case_col = "case:concept:name"
        act_col = "concept:name"
        ts_col = "time:timestamp"
        titulo = (
            sub[sub[act_col] == "TITULO_CRIADO"]
            .groupby(case_col)[ts_col]
            .min()
            .reset_index()
        )
        titulo = titulo.rename(columns={ts_col: "ts_inicio"})
        if status_val == "PAGO":
            end_act = "PAGAMENTO_REALIZADO"
        else:
            end_act = "BAIXA_SEM_SE5"
        fim = (
            sub[sub[act_col] == end_act]
            .groupby(case_col)[ts_col]
            .min()
            .reset_index()
        )
        fim = fim.rename(columns={ts_col: "ts_fim"})
        merge = titulo.merge(fim, on=case_col, how="inner")
        merge["duracao"] = merge["ts_fim"] - merge["ts_inicio"]
        total_seconds = merge["duracao"].dt.total_seconds()
        media_dias = total_seconds.mean() / (24 * 3600)
        mediana_dias = total_seconds.median() / (24 * 3600)
        print(f"    Tempo médio (TITULO_CRIADO → {end_act}): média = {media_dias:.1f} dias, mediana = {mediana_dias:.1f} dias")

    output_dir.mkdir(parents=True, exist_ok=True)


def main():
    # Verificar dependência usada pelo PM4Py (evita erro genérico "No module named 'packaging'")
    try:
        import packaging  # noqa: F401
    except ImportError:
        print("ERRO: Falta o pacote 'packaging'. Instale com:")
        print("  pip install packaging")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Process Mining - Contas a Pagar")
    parser.add_argument(
        "event_log",
        nargs="?",
        default=None,
        help="Caminho para event_log.parquet",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Diretório de saída das visualizações",
    )
    args = parser.parse_args()

    # Resolver caminho do parquet
    if args.event_log:
        parquet_path = Path(args.event_log)
    else:
        candidates = [
            Path("event_log.parquet"),
            REPO_ROOT / "data" / "marts" / "event_log.parquet",
            REPO_ROOT / "data" / "marts" / "cp_event_log.parquet",
        ]
        parquet_path = None
        for p in candidates:
            if p.exists():
                parquet_path = p
                break
        if parquet_path is None:
            print("ERRO: Nenhum event log encontrado. Informe o caminho:")
            print("  python scripts/process_mining_analysis.py <caminho_event_log.parquet>")
            sys.exit(1)

    print("=== Process Mining - Contas a Pagar ===\n")
    print(f"  Event log: {parquet_path}")

    try:
        log_df = load_and_prepare_log(parquet_path)
    except Exception as e:
        print(f"ERRO ao carregar log: {e}")
        sys.exit(1)

    out_dir = Path(args.output_dir)

    # 2.1 Process tree
    run_discovery_process_tree(log_df, out_dir)

    # 2.2 DFG
    run_dfg(log_df, out_dir)

    # 2.3 Variantes
    run_variants(log_df, top_n=10)

    # 2.4 Performance
    run_performance(log_df)

    # 3. Log filtrado
    run_filtered_log_visualization(log_df, out_dir)

    # 4. Segmentação PAGO vs PAGO_SEM_SE5
    run_segmented_analysis(log_df, out_dir)

    print("\n=== Análise concluída ===")
    print(f"  Saídas: {out_dir}")


if __name__ == "__main__":
    main()
