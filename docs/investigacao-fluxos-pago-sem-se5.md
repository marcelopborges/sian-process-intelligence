# Investigação: fluxos alternativos de pagamento (PAGO_SEM_SE5)

Relatório gerado por `scripts/investigate_pago_sem_se5_flows.py`.
Casos-alvo: `cp_case_base` onde `status_macro = 'PAGO_SEM_SE5'`.

---

## Resumo dos casos PAGO_SEM_SE5

- Total de casos no case_base: **95144**
- Casos PAGO_SEM_SE5: **39485**
- Percentual: **41.5%**

## 1. SE5 — E5_IDORIG vazio/nulo e ligação por chave

- Total de registros SE5: **168050**
- Registros com E5_IDORIG vazio ou nulo: **1**
- Percentual sem IDORIG: **0.0%**

Chave candidata SE5 ↔ título (7 campos): filial, prefixo, número, parcela, tipo, fornecedor/clifor, loja.

Amostra SE5 (20 registros):

| e5_filial | e5_data | e5_tipo | e5_moeda | e5_valor | e5_naturez | e5_banco | e5_agencia | e5_conta | e5_numcheq | e5_documen | e5_vencto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 010401 | 20250603 | RA | 01 | 475000.0 | 100160001 | 341 | 4325 | 28104 |  |  |  |
| 010401 | 20250605 | RA | 01 | 2075000.0 | 100160001 | 341 | 4325 | 28104 |  |  |  |
| 010601 | 20250602 |  | 01 | 10000.0 | 200390001 | 341 | 7934 | 30318 |  |  |  |
| 010701 | 20250602 | RA | 01 | 10000.0 | 100160001 | 341 | 5453 | 0022747 |  |  |  |
| 010701 | 20250602 |  | 01 | 10000.0 | 100160001 | 341 | 5453 | 0022747 |  |  |  |
| 010701 | 20250602 | RA | 01 | 10000.0 | 100160001 | 341 | 5453 | 0022747 |  |  |  |
| 010101 | 20250623 | RA | 01 | 3240000.0 | 100160001 | 341 | 0147 | 00093 |  |  |  |
| 010601 | 20250626 |  | M1 | 0.24 | 100100015 | 341 | 7934 | 30318 |  |  | 20250626 |
| 010601 | 20250626 |  | M1 | 0.24 | 100100015 | 341 | 7934 | 30318 |  |  | 20250626 |
| 010601 | 20250627 | PA | 01 | 50000.0 | 200390001 | 341 | 7934 | 30318 |  |  |  |
| 010601 | 20250627 |  | 01 | 50000.0 | 200390001 | 341 | 7934 | 30318 |  |  |  |
| 010202 | 20250603 | RA | 01 | 2794.76 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250603 | RA | 01 | 2794.76 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250603 | RA | 01 | 27.5 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250603 | RA | 01 | 27.5 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250603 | RA | 01 | 16.5 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250603 | RA | 01 | 16.5 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250610 | RA | 01 | 489.6 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250610 | RA | 01 | 489.6 | 100160001 | 070 | 040 | 040033860 |  |  |  |
| 010202 | 20250617 | RA | 01 | 534.7 | 100160001 | 070 | 040 | 040033860 |  |  |  |

## 2. FK1 — cobertura para PAGO_SEM_SE5 (borderô)

- Total de registros FK1: **57608**
- Colunas (chaves candidatas para SE2): FK1_FILIAL, FK1_IDFK1, FK1_DATA, FK1_VALOR, FK1_MOEDA, FK1_NATURE, FK1_VENCTO, FK1_RECPAG, FK1_TPDOC, FK1_HISTOR, FK1_VLMOE2, FK1_LOTE, FK1_MOTBX, FK1_ORDREC, FK1_FILORI, FK1_ARCNAB, FK1_CNABOC, FK1_TXMOED, FK1_SITCOB, FK1_SERREC, FK1_MULNAT, FK1_AUTBCO, FK1_CCUSTO, FK1_ORIGEM, FK1_SEQ
- Casos PAGO_SEM_SE5 que aparecem em FK1 (via FK7_IDDOC): **5**
- Percentual dos PAGO_SEM_SE5 com borderô (FK1): **0.0%**

## 3. FK5 — cobertura para PAGO_SEM_SE5 (remessa CNAB)

- Total de registros FK5: **140630**
- Colunas (amostra): FK5_FILIAL, FK5_IDMOV, FK5_DATA, FK5_VALOR, FK5_MOEDA, FK5_NATURE, FK5_RECPAG, FK5_TPDOC, FK5_FILORI, FK5_ORIGEM, FK5_BANCO, FK5_AGENCI, FK5_CONTA, FK5_NUMCH, FK5_DOC, FK5_HISTOR, FK5_VLMOE2, FK5_DTCONC, FK5_DTDISP, FK5_MODSPB, FK5_SEQCON, FK5_TERCEI, FK5_TPMOV, FK5_OK, FK5_STATUS
- Casos PAGO_SEM_SE5 com remessa CNAB (FK5): **544**
- Percentual: **1.4%**

## 4. FK6 — cobertura para PAGO_SEM_SE5 (retorno bancário)

- Total de registros FK6: **3771**
- Colunas (amostra): FK6_FILIAL, FK6_IDFK6, FK6_VALCAL, FK6_VALMOV, FK6_TPDESC, FK6_RECPAG, FK6_TPDOC, FK6_IDORIG, FK6_TABORI, FK6_HISTOR, FK6_CODVAL, FK6_ACAO, FK6_IDFKD, FK6_DATA, FK6_MOEDA, FK6_VLMOE2, FK6_TXMOED, FK6_LA, FK6_ORIGEM, DBALTERACAO, HASH_ID, FLAGDELET, RECNO, RECNODEL, DATA_EXECUTION
- Campos de data/confirmação candidatos: FK6_DATA, DATA_EXECUTION, DATA_INGESTION

## Amostra FK1 (20 registros)

| FK1_FILIAL | FK1_IDFK1 | FK1_DATA | FK1_VALOR | FK1_MOEDA | FK1_NATURE | FK1_VENCTO | FK1_RECPAG | FK1_TPDOC | FK1_HISTOR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 010101 | B19EE115F9374F11881900505 | 2024-07-01 | 337.73 | 01 | 100030002 | None | R | CP | Compensao Nota de Crdito |
| 010101 | B59EE115F9374F11A81900505 | 2024-07-01 | 337.73 | 01 | 200050001 | None | R | BA | Baixa por Compensao |
| 010101 | B89EE115F9374F11B81900505 | 2024-07-01 | 4728.2 | 01 | 100030002 | None | R | CP | Compensao Nota de Crdito |
| 010101 | BB9EE115F9374F11981900505 | 2024-07-01 | 4728.2 | 01 | 200030001 | None | R | BA | Baixa por Compensao |
| 010101 | CF6FF380FA374F11B81900505 | 2024-07-01 | 337.73 | 01 | 200050001 | None | P | ES | Cancel. de Compensacao |
| 010101 | D36FF380FA374F11B81900505 | 2024-07-01 | 337.73 | 01 | 100030002 | None | P | ES | Cancel. de Compensacao |
| 010101 | D76FF380FA374F11A81900505 | 2024-07-01 | 4728.2 | 01 | 200030001 | None | P | ES | Cancel. de Compensacao |
| 010101 | DB6FF380FA374F11B81900505 | 2024-07-01 | 4728.2 | 01 | 100030002 | None | P | ES | Cancel. de Compensacao |
| 010301 | 155909FF40394F11A81A00505 | 2024-07-01 | 245400.0 | 01 | 100050003 | 2024-06-06 | R | VL | Valor recebido s/ Titulo |
| 010101 | B72303BB48394F11A81A00505 | 2024-07-01 | 242442.01 | 01 | 100010001 | 2024-06-27 | R | VL | Valor recebido s/ Titulo |
| 010101 | 61F2AD914C394F11B81C00505 | 2024-07-02 | 251179.81 | 01 | 100010001 | 2024-07-02 | R | VL | Valor recebido s /Titulo |
| 010101 | 161888AE4C394F11B81C00505 | 2024-07-02 | 126476.31 | 01 | 100010001 | 2024-07-02 | R | VL | Valor recebido s /Titulo |
| 010101 | 1D1888AE4C394F11B81C00505 | 2024-07-02 | 26667.13 | 01 | 100010001 | 2024-07-02 | R | VL | Valor recebido s /Titulo |
| 010101 | 06B9F1AE1C3A4F11881C00505 | 2024-07-04 | 69.95 | 01 | 200050001 | None | P | BA | Valor recebido s/ Titulo |
| 010101 | C51B4D141D3A4F11981C00505 | 2024-07-04 | 69.95 | 01 | 200050001 | None | R | ES | Cancelamento da Baixa |
| 010101 | 4BD0DA01F73A4F11881900505 | 2024-07-05 | 69.95 | 01 | 100030002 | None | R | CP | Compensao Nota de Crdito |
| 010101 | 4FD0DA01F73A4F11981900505 | 2024-07-05 | 69.95 | 01 | 200050001 | None | R | BA | Baixa por Compensao |
| 010101 | 52D0DA01F73A4F11A81900505 | 2024-07-05 | 979.36 | 01 | 100030002 | None | R | CP | Compensao Nota de Crdito |
| 010101 | 55D0DA01F73A4F11981900505 | 2024-07-05 | 979.36 | 01 | 200030001 | None | R | BA | Baixa por Compensao |
| 010101 | 183676AFFA3A4F11981900505 | 2024-07-05 | 69.95 | 01 | 100030002 | None | P | ES | Cancel. de Compensacao |

## Amostra FK5 (20 registros)

| FK5_FILIAL | FK5_IDMOV | FK5_DATA | FK5_VALOR | FK5_MOEDA | FK5_NATURE | FK5_RECPAG | FK5_TPDOC | FK5_FILORI | FK5_ORIGEM |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 010301 | 76C3903708374F11B81900505 | 2024-06-30 | 34393.46 | M1 | 600010001 | R | DH | 010301 | FINA100 |
| 010301 | 8A40E2B20E374F11A81900505 | 2024-06-30 | 34393.46 | M1 | 600010001 | P | ES | 010301 | FINA100 |
| 010301 | F8C8DF90F1374F11B81900505 | 2024-06-30 | 34393.46 | M1 | 600010002 | R | DH | 010301 | FINA100 |
| 010301 | 56F826CDF1374F11A81900505 | 2024-06-30 | 1290959.5 | M1 | 600010002 | R | DH | 010301 | FINA100 |
| 010101 | 042C8D05F2374F11881900505 | 2024-06-30 | 54308.38 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010101 | C2BCFF31F2374F11A81900505 | 2024-06-30 | 11473649.23 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010101 | 2AF8A22CF3374F11881900505 | 2024-06-30 | 2172.12 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010101 | 9223D3FDF3374F11881900505 | 2024-06-30 | 2117.08 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010101 | 49F2EF38F4374F11881900505 | 2024-06-30 | 1.0 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010101 | D3EF9591F4374F11B81900505 | 2024-06-30 | 207.91 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010101 | 26AE71B4F4374F11981900505 | 2024-06-30 | 0.99 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010101 | C3511975F5374F11981900505 | 2024-06-30 | 6680441.94 | M1 | 600010002 | R | DH | 010101 | FINA100 |
| 010201 | E2C99109F6374F11A81900505 | 2024-06-30 | 189795.99 | M1 | 600010002 | R | DH | 010201 | FINA100 |
| 010201 | FFCB7F54F6374F11981900505 | 2024-06-30 | 1269620.87 | M1 | 600010002 | R | DH | 010201 | FINA100 |
| 010201 | 38DA209EF6374F11A81900505 | 2024-06-30 | 83467927.22 | M1 | 600010002 | R | DH | 010201 | FINA100 |
| 010201 | 9E9EFBD0F6374F11981900505 | 2024-06-30 | 19252.49 | M1 | 600010002 | R | DH | 010201 | FINA100 |
| 010201 | 2C9CF0FDF6374F11B81900505 | 2024-06-30 | 7297.71 | M1 | 600010002 | R | DH | 010201 | FINA100 |
| 010201 | FD427516F7374F11981900505 | 2024-06-30 | 0.47 | M1 | 600010002 | R | DH | 010201 | FINA100 |
| 010201 | 44636C8DF7374F11881900505 | 2024-06-30 | 11072213.64 | M1 | 600010002 | R | DH | 010201 | FINA100 |
| 010101 | 00F3441881384F11881A00505 | 2024-06-30 | 1604282.59 | M1 | 600010002 | R | DH | 010101 | FINA100 |

## Amostra FK6 (20 registros)

| FK6_FILIAL | FK6_IDFK6 | FK6_VALCAL | FK6_VALMOV | FK6_TPDESC | FK6_RECPAG | FK6_TPDOC | FK6_IDORIG | FK6_TABORI | FK6_HISTOR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 010101 | 0000000002 | 326.25 | 326.25 | 1 | P | DC | A777D4485B394F11981600505 | FK2 | Desconto s/Pgto de Titulo |
| 010101 | 0000000004 | 0.19 | 0.19 | 1 | R | JR | 36507AE23B3D4F11B81600505 | FK1 | Juros s/Receb.Titulo |
| 010101 | 0000000005 | 124.56 | 124.56 | 1 | P | JR | A76109D046404F11B81600505 | FK2 | Juros s/Pgto de Titulo |
| 010101 | 0000000006 | 12.78 | 12.78 | 1 | P | JR | 6443DEB49C424F11A81900505 | FK2 | Juros s/Pgto de Titulo |
| 010201 | 0000000001 | 279.03 | 279.03 | 1 | P | JR | 4F48DAC0A2424F11B81600505 | FK2 | Juros s/Pgto de Titulo |
| 010201 | 0000000002 | 167.38 | 167.38 | 1 | P | JR | 5448DAC0A2424F11881600505 | FK2 | Juros s/Pgto de Titulo |
| 010101 | 0000000007 | 0.0 | 0.01 | 1 | R | JR | CDCE6FE2F6424F11A81900505 | FK1 | Juros s/Receb.Titulo |
| 010101 | 0000000008 | 0.0 | 0.01 | 1 | R | DC | 3ABB5A34F7424F11A81900505 | FK1 | Desconto s/Receb.Titulo |
| 010101 | 0000000009 | 0.0 | 0.01 | 1 | R | JR | 59320677F7424F11981900505 | FK1 | Juros s/Receb.Titulo |
| 010101 | 0000000010 | 0.0 | 0.01 | 1 | R | JR | BCE68FBFF7424F11981900505 | FK1 | Juros s/Receb.Titulo |
| 010101 | 0000000011 | 108.31 | 108.31 | 2 | P | JR | 9F7F8B8268434F11A81900505 | FK2 | Juros s/Pgto de Titulo |
| 010101 | 0000000012 | 0.01 | 0.01 | 1 | R | JR | C6E7C14AAA434F11881A00505 | FK1 | Juros s/Receb.Titulo |
| 010101 | 0000000013 | 0.01 | 0.01 | 1 | R | JR | 50788977AA434F11981A00505 | FK1 | Juros s/Receb.Titulo |
| 010101 | 0000000014 | 0.01 | 0.01 | 1 | R | JR | 160485A0AA434F11881A00505 | FK1 | Juros s/Receb.Titulo |
| 010101 | 0000000015 | 0.01 | 0.01 | 1 | R | DC | E5F909C0AD434F11881600505 | FK1 | Desconto s/Receb.Titulo |
| 010101 | 0000000016 | 0.01 | 0.01 | 1 | R | DC | DB4E0938AE434F11A81600505 | FK1 | Desconto s/Receb.Titulo |
| 010101 | 0000000017 | 0.01 | 0.01 | 1 | R | DC | 24BFD60BAF434F11A81900505 | FK1 | Desconto s/Receb.Titulo |
| 010201 | 0000000003 | 21.33 | 21.33 | 1 | P | JR | 690C10D62F444F11A81900505 | FK2 | Juros s/Pgto de Titulo |
| 010201 | 0000000004 | 5.21 | 5.21 | 1 | P | JR | 6E0C10D62F444F11881900505 | FK2 | Juros s/Pgto de Titulo |
| 010202 | 0000000001 | 4.16 | 4.16 | 2 | P | JR | AA3F9CBD35444F11981900505 | FK2 | Juros s/Pgto de Titulo |

---
## Conclusões e recomendações

- **Fluxos alternativos confirmados:** FK1 (borderô) e FK5 (remessa CNAB) têm ligação com o caso via FK7 (IDDOC). A cobertura sobre PAGO_SEM_SE5 é baixa: FK1 cobre **5 casos (0,0%)**, FK5 cobre **544 casos (1,4%)**. A grande maioria dos PAGO_SEM_SE5 (39.485) não aparece em borderô nem em remessa CNAB neste ambiente. FK6 (retorno bancário) tem coluna FK6_IDORIG apontando para FK1/FK2, não para FK7; a cobertura por case_id não foi calculada nesta versão do script.
- **Tabelas que ajudam a fechar o processo:** FK5 traz alguma evidência (1,4%); FK1 quase nenhuma para PAGO_SEM_SE5. Para “fechar” o processo dos 39.485 casos sem SE5, as tabelas atuais (FK1/FK5/FK6) não explicam o volume — a baixa operacional (e2_baixa) continua sendo a evidência principal já usada no mart.
- **Novos eventos sugeridos para o event_log:** Só faria sentido evento de REMESSA_CNAB (FK5) se a modelagem quiser representar o 1,4% com traço explícito; BORDERÓ (FK1) e RETORNO (FK6) têm cobertura/ligação insuficiente para justificar evento próprio nesta etapa.
- **Hipóteses refutadas:** A hipótese de que “muitos PAGO_SEM_SE5 passam por borderô (FK1)” não se confirmou (0,0%). A de que “remessa CNAB (FK5) cobre boa parte” também não (1,4%).

*Este relatório é apenas evidência; não altera marts até decisão de modelagem.*