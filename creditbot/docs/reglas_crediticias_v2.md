# Reglas crediticias ficticias v2

**Versión:** v2.0  
**Ámbito:** Precalificación académica — no producción

## Categorías de score (Ecuador 1–999)

| Categoría | Rango | TEA anual |
|---|---|---|
| Excelente | 750–999 | 14,5% |
| Aceptable | 550–749 | 16,0% |
| Regular | 349–549 | 16,5% |
| Alto riesgo | 1–348 | No elegible |

## Elegibilidad

- Score &lt; 349 → no elegible
- Mora activa &gt; 30 días → no elegible
- Lista negra → no elegible
- Sin historial → tratar como regular (monto conservador)

## Capacidad y montos

```
capacidad = ingreso × 0.35 - cuotas_actuales - gastos_mensuales
```

| Categoría | Techo (× ingreso) |
|---|---|
| Excelente | 6× |
| Aceptable | 4× |
| Regular | 1,5× |

## Cuota — sistema francés

```
r = TEA / 12
cuota = monto × [r(1+r)^n] / [(1+r)^n − 1]
```

## Resultado

- Alto riesgo → `no_cumple`
- Regular → `observado`
- Cuota ≤ capacidad (excelente/aceptable) → `preaprobado`
- Cuota ≤ capacidad × 1,15 → `observado`
- Cuota &gt; capacidad × 1,15 → `no_cumple`
