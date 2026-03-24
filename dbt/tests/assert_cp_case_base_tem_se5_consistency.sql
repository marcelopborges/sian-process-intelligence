-- Teste: consistência entre tem_se5 e presença de dt_pagamento/fonte_dt_pagamento.
-- tem_se5 = true deve implicar fonte_dt_pagamento não nulo (quando há SE5 há data).
select case_id, tem_se5, fonte_dt_pagamento
from {{ ref('mart_cp_case_base') }}
where tem_se5 = true
  and fonte_dt_pagamento is null
