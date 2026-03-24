# Configuração do laboratório local

Para o fluxo `run_local_lab.sh` (BigQuery → Parquet → DuckDB) funcionar, é preciso configurar **credenciais GCP**. Projeto e dataset já vêm preenchidos para o ambiente SIAN (dois projetos: suprimentos e financeiro).

## Mapeamento SIAN (já embutido no código)

| Tabela   | Project ID                  | Dataset | Camada  |
|----------|-----------------------------|---------|---------|
| SIAN_SE2 | gcp-sian-proj-suprimentos   | silver  | silver  |
| SE5      | gcp-sian-proj-suprimentos   | raw     | raw     |
| FK7      | gcp-sian-proj-financeiro    | silver  | silver  |
| FK2      | gcp-sian-proj-financeiro    | silver  | silver  |

O lab usa: **SE2** ← `SIAN_SE2` (suprimentos/silver), **SE5** ← `SE5` (suprimentos/raw), **FK7** e **FK2** (financeiro/silver). Para outro ambiente, defina no `.env` as variáveis por tabela (ex.: `BQ_PROJECT_SE2`, `BQ_DATASET_SE2`, `BQ_TABLE_SE2`).

## Passo a passo

### 1. Criar o arquivo `.env` (opcional)

Se quiser sobrescrever projetos/datasets ou usar variáveis do lab:

```bash
cp .env.example .env
```

Para usar só os defaults SIAN, **não é obrigatório** ter `.env`; só é necessário ter credenciais GCP (passo 3).

### 2. (Opcional) Sobrescrever projeto/dataset

Só se não for usar o SIAN: no `.env` defina `BQ_PROJECT_ID`/`BQ_DATASET_RAW` (fallback único) ou por tabela: `BQ_PROJECT_SE2`, `BQ_DATASET_SE2`, `BQ_TABLE_SE2`, etc. Ver `.env.example`.

### 3. Credenciais GCP (obrigatório para extração)

Escolha uma das opções:

**Opção A — Application Default Credentials (recomendado para máquina local)**

```bash
gcloud auth application-default login
```

Não é preciso definir nada no `.env`; o cliente BigQuery usa as credenciais do ADC.

**Opção B — Service account (CI ou servidor)**

1. Crie uma service account no GCP com permissão de **BigQuery Data Viewer** (ou equivalente).
2. Baixe o JSON da chave e coloque em um caminho seguro (fora do repo).
3. No `.env`, descomente e preencha:

   ```
   GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/sua-service-account.json
   ```

### 4. Variáveis opcionais do lab

No `.env` você pode ajustar:

- `LOCAL_LAB_EXTRACT_LIMIT` — limite de linhas por tabela (padrão: 0 = sem limite, extrai tudo; use ex. 10000 para amostra).
- `LOCAL_LAB_DATE_FILTER` — filtro SQL opcional (ex.: `E2_EMISSAO >= '2024-01-01'`).
- `BQ_TABLE_SE2` (default `SIAN_SE2`), `BQ_TABLE_FK7` (`FK7`), `BQ_TABLE_FK2` (`FK2`), `BQ_TABLE_SE5` (`SE5`) — nomes das tabelas no BQ.

### 5. Rodar o fluxo

```bash
./scripts/run_local_lab.sh
```

O script carrega o `.env` automaticamente se o arquivo existir na raiz do projeto.

## Resumo mínimo (SIAN)

1. Configurar credenciais: `gcloud auth application-default login` **ou** no `.env`: `GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/sa.json`
2. `./scripts/run_local_lab.sh` (projetos/datasets já são os da tabela acima)

## Sem acesso ao BigQuery

Se você não tiver projeto/dataset ou credenciais:

- Coloque os Parquets manualmente em `data/extracts/` (`se2.parquet`, `fk7.parquet`, `fk2.parquet`, `se5.parquet`) e rode só as etapas de carga e materialização (veja [local-lab-duckdb.md](local-lab-duckdb.md)).

## Process mining (imagens com Graphviz)

O script `scripts/process_mining_analysis.py` gera process tree e DFG. Para usar o layout nativo do PM4Py (Graphviz), instale o **Graphviz** no sistema:

| SO / ambiente | Comando |
|---------------|---------|
| **Fedora**    | `sudo dnf install graphviz` |
| **Ubuntu/Debian** | `sudo apt install graphviz` |
| **Conda**     | `conda install -c conda-forge graphviz` |
| **Fedora Toolbox** | Dentro do container: `dnf install graphviz`. Rode o script **de dentro do toolbox** (`toolbox enter` e depois `python scripts/process_mining_analysis.py ...`) para que o `dot` seja encontrado. |

Sem Graphviz, o script gera as mesmas imagens usando matplotlib (fallback). As saídas ficam em `output/process_mining/`.
