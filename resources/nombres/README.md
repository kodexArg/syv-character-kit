# resources/nombres/

Pool curado de nombres para el generador de identidad (ver [`gddr/01-flujo-obligatorio-creacion.md`](../../gddr/01-flujo-obligatorio-creacion.md) §2.3 — Fase 2, Nombre).

## Archivos

- `nombres_m.txt` — 25 nombres masculinos argentinos modernos. Formato `Nombre|Apodo`.
- `nombres_f.txt` — 25 nombres femeninos argentinos modernos. Formato `Nombre|Apodo`.
- `apellidos.txt` — 50 apellidos argentinos (mix hispano + inmigración).

Las líneas que empiezan con `#` son comentarios.

## Regla de muestreo

El generador (ver [`scripts/sample_name.py`](../../scripts/sample_name.py)) elige:

1. Un nombre del pool según género (peso uniforme).
2. Con **50%** de probabilidad, el apodo asignado al nombre. Si no, `sobrenombre = null`.
3. Un apellido del pool de apellidos (peso uniforme).

## Fuentes de referencia (datos crudos, no incluidos en el repo)

Para escalar el pool a futuro, las fuentes públicas relevantes son:

- **RENAPER (oficial)** — https://datos.gob.ar/dataset/renaper-nombres-propios-argentina
  20 nombres más frecuentes por provincia y año (2012–2024), separados por género. CSV/PDF.
- **datos.gob.ar interactivo** — https://nombres.datos.gob.ar/
  Histórico de nacimientos en Argentina, filtrable por género. Descarga CSV.
- **CABA Registro Civil** — https://data.buenosaires.gob.ar/dataset/nombres
  Primeros nombres inscriptos en CABA, CSV trimestral.
- **CalmRott7915/Nombres_Argentina** — https://github.com/CalmRott7915/Nombres_Argentina
  Reprocesamiento limpio de 9M+ registros oficiales (encoding/duplicados resueltos).
- **philipperemy/name-dataset** — https://github.com/philipperemy/name-dataset
  730K nombres + 983K apellidos globales con `country_code` (AR filtrable). 3.3GB ZIP.

Sobrenombres argentinos: no existe dataset estructurado público; los apodos de este pool están curados a mano (Francisco→Pancho, Ignacio→Nacho, etc.).
