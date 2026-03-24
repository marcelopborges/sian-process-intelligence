-- Teste: quando vl_pago_e_inferido = true, não deve haver SE5 (valor foi inferido por falta de SE5).
select case_id, vl_pago_e_inferido, tem_se5
from {{ ref('mart_cp_case_base') }}
where vl_pago_e_inferido = true
  and tem_se5 = true
