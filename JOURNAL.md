### [2026-06-21] # SINCRO: Estandarización de Esquema `meta.json` (Synquork Core)

Se ha consolidado el esquema definitivo para los archivos de metadatos de los activos de ingeniería (`meta.json`). El scanner de Synquork ahora procesará un esquema estricto de un solo nivel de indentación para las claves raíz, forzando empaquetado inline en estructuras densas (`status`, `_telemetry`) para optimizar el peso del pipeline, evitar diffs masivos de Git y garantizar la legibilidad en crudo.

#### 1. Estructura de Referencia (`NE555 RC Circuit Simulator`)

```json
{
  "id": "15",
  "title": "NE555 RC Circuit Simulator",
  "category": "Electronic Simulation",
  "visibility": "PRIVATE",
  "tags": "SOFTWARE",
  "status": { "activity": "ACTIVE", "maturity": "ALPHA", "version": "0.1.0", "progress_pct": 40, "scopes": { "model": { "status": "PROTOTYPE", "progress": 0}, "cli": { "status": "BETA", "progress": 50 }, "setup": { "status": "ALPHA", "progress": 50 }, "core": { "status": "ALPHA", "progress": 25 }, "data": { "status": "PROTOTYPE", "progress": 50} } },
  "environment": { "os": "Fedora 43", "shell": "fish" },
  "repository": { "ssh": "git@github.com:MarcosBernardC/ne555-rc-simulator.git", "https": "https://github.com/MarcosBernardC/ne555-rc-simulator" },
  "stack": ["Python 3.14", "NumPy", "Matplotlib"],
  "description": "Simulador de transitorios RC y 555.",
  "_telemetry": { "last_update": "2026-06-17", "last_commit_log": "feat(setup): crear función obtención", "changelog": [{ "version": "0.1.0", "date": "2026-06-17", "summary": "Estructura base y setup inicial." }] }
}
```

#### 2. Matriz de Parámetros Válidos (Validador Core)

El parser de Synquork rechazará cualquier `meta.json` local que no se homologue estrictamente a los siguientes tokens del sistema:

| **Dimensión**    | **Parámetros Permitidos (Estricto)**                  | **Propósito / Renderizado en UI**                            |
| ---------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| **`tags`**       | `SOFTWARE`, `WEB APP`, `ELECTRONICS`, `DOCUMENTATION` | Enrutamiento y filtrado por categorías en el frontend del portafolio. |
| **`maturity`**   | `PROTOTYPE`, `ALPHA`, `BETA`, `STABLE`                | Define el ciclo de vida del desarrollo y flags visuales de madurez. |
| **`visibility`** | `PUBLIC`, `PRIVATE`                                   | Control de visibilidad para exclusión automatizada en compilaciones públicas. |
| **`activity`**   | `ACTIVE`, `ARCHIVED`                                  | Clasificación de laboratorios activos frente a históricos o congelados. |

#### 3. Formulación Matemática

El porcentaje de progreso final se determina según la ecuación en bloque:

$$
P_{\text{global}} = \text{round}\left( \frac{\sum_{i=1}^{n} (P_i \cdot W_i)}{\sum_{i=1}^{n} W_i} \right)
$$

#### 4. Matriz de Coeficientes de Ponderación (W)

El peso algorítmico asignado a cada scope penaliza las etapas tempranas de desarrollo y premia los esfuerzos invertidos en módulos maduros, aplicando los siguientes multiplicadores fijos:

- **`PROTOTYPE`**: Coeficiente 0.5 (Fase inicial, bajo impacto en el global).
- **`ALPHA`**: Coeficiente 1.0 (Estructura base operativa).
- **`BETA`**: Coeficiente 2.0 (Módulo en pruebas avanzadas).
- **`STABLE` / `PROD` / `RELEASE`**: Coeficiente 3.0 (Módulo finalizado o en producción).
