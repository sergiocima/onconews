# 🔍 Sistema di Filtri Intelligente OncoNews

Il sistema di filtri intelligente esclude automaticamente articoli **non pertinenti** PRIMA dello scraping, risparmiando tempo e risorse.

## Come Funziona

### Flusso di Lavoro

1. **News API** restituisce articoli in base alle keyword configurate
2. **Filtro Intelligente** analizza titolo + description di ogni articolo
3. **Solo articoli validi** vengono inseriti nel database e scrapati

### Criteri di Filtro

#### ❌ Articoli SCARTATI se contengono keyword negative:

**Necrologi/Lutti:**
- morto, è morto, lutto, addio, necrologio, scomparso, deceduto

**Eventi Non Scientifici:**
- oroscopo, solidarietà, beneficenza, raccolta fondi, torneo, gara, concerto

**Sport/Cronaca:**
- calcio, serie A, campionato, scudetto, attaccante, allenatore

#### ✅ Articoli ACCETTATI se contengono almeno una keyword positiva:

- terapia, cura, farmaco, trattamento
- trial, sperimentazione, studio, ricerca
- approvazione, approvato, efficace
- prevenzione, diagnosi, screening, molecola, protocollo

## Configurazione

Modifica il file `config.yaml`:

```yaml
content_filter:
  enabled: true  # Attiva/disattiva il filtro

  # Aggiungi keyword da escludere
  excluded_keywords:
    - "parola_da_escludere"

  # Aggiungi keyword richieste
  required_keywords:
    - "parola_richiesta"

  # Log articoli filtrati
  log_filtered: true
  log_file: "filtered_articles.log"
```

## Log degli Articoli Filtrati

Gli articoli scartati vengono salvati in `filtered_articles.log` per permetterti di:
- ✅ Verificare che il filtro funzioni correttamente
- ✅ Identificare eventuali falsi positivi
- ✅ Affinare le keyword

### Esempio Log:

```
================================================================================
Filter Run: 2025-11-13 15:45:30
Rejected: 3 articles
================================================================================

TITLE: Lutto nel calcio: è morto l'ex attaccante Salvatore Garritano
SOURCE: La Repubblica
URL: https://...
REASON: Excluded keyword found: 'è morto'
DESCRIPTION: L'ex calciatore del Torino...
--------------------------------------------------------------------------------
```

## Statistiche

Durante l'esecuzione vedrai:

```
Total articles fetched: 50
ContentFilter Results:
  - Total articles: 50
  - Accepted: 35
  - Rejected: 15
After filtering: 35 articles kept, 15 rejected
```

## Disabilitare il Filtro

Se vuoi disabilitare temporaneamente il filtro:

```yaml
content_filter:
  enabled: false
```

## Esempi di Articoli Filtrati

### ❌ SCARTATI (Non pertinenti)

- "Lutto nel calcio: è morto l'ex attaccante..."
- "L'oroscopo di oggi - mercoledì 12 novembre"
- "Tennis e solidarietà, 10.000 euro per l'Istituto di Candiolo"
- "Grande gala di beneficenza per la ricerca sul cancro"

### ✅ ACCETTATI (Pertinenti)

- "Nuova terapia CAR-T approvata dall'AIFA per linfoma"
- "Trial clinico: immunoterapia efficace per tumore polmone"
- "Scoperta molecola promettente per cura melanoma"
- "Studio conferma efficacia della prevenzione per tumore seno"

## Troubleshooting

### Il filtro scarta troppi articoli validi (Falsi Positivi)

**Soluzione:** Rimuovi keyword dalla lista `excluded_keywords` o aggiungi eccezioni.

### Il filtro lascia passare articoli non pertinenti (Falsi Negativi)

**Soluzione:** Aggiungi più keyword a `excluded_keywords` o rendi più restrittive le `required_keywords`.

### Come testare il filtro

```bash
# Esegui manualmente e controlla i log
python3 main.py

# Verifica articoli filtrati
cat filtered_articles.log

# Controlla log principale
tail -f onconews.log
```

## Performance

Il filtro è **molto veloce** perché:
- ✅ Lavora solo su titolo + description (già disponibili da News API)
- ✅ Usa semplici ricerche di stringhe (no AI/API esterne)
- ✅ Evita scraping inutile di articoli non pertinenti

**Risparmio stimato:**
- ~30% di articoli filtrati = ~30% meno scraping
- Più veloce, meno banda, meno errori

## Aggiornamento sul VPS

Per attivare il filtro sul tuo VPS:

```bash
cd ~/onconews
git pull
python3 main.py  # Test manuale
```

Il filtro sarà attivo anche per le esecuzioni automatiche del cron! 🎉
