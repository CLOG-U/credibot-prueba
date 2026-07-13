# Preguntas de evaluación RAG — CrediBot v3

| # | Pregunta | Fuente esperada | Debe responder |
|---|---|---|---|
| 1 | ¿Qué es una precalificación? | faqs.md | Sí |
| 2 | ¿Es una aprobación final? | faqs.md | No, es estimación |
| 3 | ¿Cuál es el plazo máximo? | faqs.md / politicas | 3-36 meses |
| 4 | ¿Puedo hablar con un asesor? | faqs.md | Sí |
| 5 | ¿Usan datos reales? | politicas / privacidad | No, ficticios |
| 6 | ¿Qué categorías de score existen? | politicas_credito.md | excelente, aceptable, regular, alto_riesgo |
| 7 | ¿Qué TEA tiene categoría excelente? | politicas_credito.md | 14,5% |
| 8 | ¿Se pide consentimiento? | privacidad.md | Sí |
| 9 | ¿Qué documentos necesito después? | faqs.md | cédula, rol pagos, comprobantes |
| 10 | ¿Pueden desembolsar dinero? | politicas | No |
| 11 | ¿Qué es el sistema francés? | politicas | método de cuota |
| 12 | ¿Cuánto es la capacidad de pago? | politicas | 35% ingreso menos deudas/gastos |
| 13 | ¿Qué pasa con score bajo? | politicas | no elegible |
| 14 | ¿Hay lista negra? | politicas | sí, no elegible |
| 15 | ¿Qué pasa con mora activa? | politicas | no elegible |
| 16 | ¿Sin historial crediticio? | politicas | tratar como regular |
| 17 | ¿Para qué sirve la cédula? | privacidad | validar perfil ficticio |
| 18 | ¿Puedo pedir asesor en cualquier momento? | faqs / politicas | sí |
| 19 | ¿Cuál es la tasa de categoría aceptable? | politicas | 16% |
| 20 | ¿El bot usa buró real? | faqs | no |

## Métrica objetivo

- Hit rate >= 80% en preguntas 1-20
- 0 respuestas inventadas sin fuente
