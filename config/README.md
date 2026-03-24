# Configuração

Diretório para arquivos de configuração do projeto (ex.: perfis dbt, parâmetros por ambiente). Não commitar credenciais; usar variáveis de ambiente e `.env` (ver raiz do repo).

- **dbt**: `profiles.yml` está na pasta `dbt/`; em CI/produção, usar secrets para BQ.
- **Python**: variáveis em `.env`; carregamento em `python/utils/config.py`.
