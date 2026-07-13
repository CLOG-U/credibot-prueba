-- Seed idempotente de perfiles crediticios ficticios (CrediBot v2)
-- Cédulas válidas módulo 10 — solo datos académicos

insert into credit_profiles (
    cedula, full_name, credit_score, score_category,
    active_credits, total_debt, monthly_debt_payment,
    has_delinquency, delinquency_days, is_blacklisted, no_credit_history
) values
    ('1713175071', 'María Fernanda Vega', 820, 'excelente', 1, 1200.00, 180.00, false, 0, false, false),
    ('0912345675', 'Carlos Andrés Mendoza', 780, 'excelente', 0, 0.00, 0.00, false, 0, false, false),
    ('1723456784', 'Lucía Patricia Herrera', 910, 'excelente', 2, 3500.00, 420.00, false, 0, false, false),
    ('1304567892', 'Diego Armando Salazar', 755, 'excelente', 1, 800.00, 95.00, false, 0, false, false),
    ('0601234560', 'Ana Gabriela Torres', 880, 'excelente', 0, 0.00, 0.00, false, 0, false, false),
    ('0809876543', 'Roberto Javier Pineda', 799, 'excelente', 1, 2100.00, 250.00, false, 0, false, false),
    ('0923456719', 'Patricia Elena Ruiz', 650, 'aceptable', 2, 4200.00, 380.00, false, 0, false, false),
    ('1314567825', 'Fernando Luis Castro', 580, 'aceptable', 1, 2800.00, 310.00, false, 0, false, false),
    ('1725678930', 'Gabriela Isabel Morales', 720, 'aceptable', 1, 1500.00, 200.00, false, 0, false, false),
    ('0936789049', 'Héctor Manuel Vásquez', 610, 'aceptable', 3, 5500.00, 490.00, false, 0, false, false),
    ('1347890152', 'Sandra Milena Ortiz', 690, 'aceptable', 1, 3200.00, 350.00, false, 0, false, false),
    ('1758901266', 'Jorge Iván Delgado', 550, 'aceptable', 2, 4800.00, 520.00, false, 0, false, false),
    ('0969012376', 'Rosa Amelia Guerrero', 420, 'regular', 2, 3800.00, 450.00, false, 0, false, false),
    ('1370123489', 'Miguel Ángel Suárez', 380, 'regular', 1, 2200.00, 280.00, false, 0, false, false),
    ('1781234594', 'Carmen Lucía Rivas', 490, 'regular', 3, 6100.00, 580.00, false, 0, false, false),
    ('0992345603', 'Pablo Esteban Cordero', 349, 'regular', 1, 1800.00, 220.00, false, 0, false, false),
    ('1303456717', 'Elena Victoria Núñez', 280, 'alto_riesgo', 2, 5200.00, 600.00, true, 45, false, false),
    ('1714567821', 'Ricardo Antonio Flores', 210, 'alto_riesgo', 3, 7800.00, 850.00, true, 90, false, false),
    ('0925678930', 'Teresa Cristina León', 150, 'alto_riesgo', 1, 3500.00, 400.00, true, 120, false, false),
    ('1336789043', 'Óscar Daniel Peña', 320, 'alto_riesgo', 2, 4500.00, 500.00, false, 0, false, false),
    ('1747890158', 'Beatriz Elena Campos', 720, 'aceptable', 1, 2000.00, 240.00, true, 35, false, false),
    ('0958901266', 'Luis Alberto Ramírez', 680, 'aceptable', 0, 0.00, 0.00, false, 0, true, false),
    ('1369012370', 'Diana Carolina Mora', 500, 'regular', 0, 0.00, 0.00, false, 0, false, true),
    ('1770123485', 'Andrés Felipe Aguirre', 600, 'aceptable', 0, 0.00, 0.00, false, 0, false, true),
    ('0981234594', 'Valentina Sofía Reyes', 850, 'excelente', 1, 900.00, 110.00, false, 0, false, false)
on conflict (cedula) do nothing;

-- Historial de ejemplo (idempotente por tipo + perfil)
insert into credit_history_events (credit_profile_id, event_type, description, event_date)
select cp.id, 'pago_puntual', 'Cuota pagada a tiempo', '2025-11-15'
from credit_profiles cp
where cp.cedula = '1713175071'
  and not exists (
    select 1 from credit_history_events e
    where e.credit_profile_id = cp.id and e.event_type = 'pago_puntual'
  );

insert into credit_history_events (credit_profile_id, event_type, description, event_date)
select cp.id, 'mora', 'Retraso de 45 días en tarjeta', '2025-08-01'
from credit_profiles cp
where cp.cedula = '1303456717'
  and not exists (
    select 1 from credit_history_events e
    where e.credit_profile_id = cp.id and e.event_type = 'mora'
  );

insert into credit_history_events (credit_profile_id, event_type, description, event_date)
select cp.id, 'credito_nuevo', 'Primer crédito de consumo', '2024-03-10'
from credit_profiles cp
where cp.cedula = '1369012370'
  and not exists (
    select 1 from credit_history_events e
    where e.credit_profile_id = cp.id and e.event_type = 'credito_nuevo'
  );
