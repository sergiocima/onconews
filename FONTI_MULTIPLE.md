# 📡 Sistema Multi-Fonte OncoNews

OncoNews ora raccoglie articoli da **3 fonti diverse** per massimizzare la copertura e catturare una varietà di contenuti (da fonti affidabili a potenzialmente problematiche).

---

## 🔍 Fonti Attive

### 1. **News API** (Mainstream News)
**Tipo:** Aggregatore notizie professionale
**Copertura:** Testate giornalistiche italiane e internazionali
**Limite:** 100 richieste/giorno (piano gratuito)
**Articoli/giorno:** ~20-50

**Caratteristiche:**
- ✅ Fonti verificate e professionali
- ✅ Metadati strutturati (autore, data, fonte)
- ✅ Qualità medio-alta
- ❌ Ritardo 24h sulle notizie
- ❌ Solo testate registrate

**Fonti tipiche:** Repubblica, Corriere, ANSA, Il Sole 24 Ore, Wired, HWUpgrade, ecc.

---

### 2. **Google News RSS** (Ampia Copertura)
**Tipo:** Aggregatore Google tramite feed RSS
**Copertura:** TUTTI i siti indicizzati da Google News
**Limite:** Nessuno (gratis, illimitato)
**Articoli/giorno:** ~50-150

**Caratteristiche:**
- ✅ Copertura vastissima (include blog, siti minori)
- ✅ Notizie in tempo reale
- ✅ Gratis e illimitato
- ⚠️ Qualità variabile
- ⚠️ Include siti meno noti/affidabili

**Fonti tipiche:** Mix di tutto - da Fondazione Veronesi a blog personali

---

### 3. **Reddit** (Discussioni Utenti)
**Tipo:** Forum/social con discussioni utenti
**Copertura:** Subreddit italiani e internazionali su salute/medicina
**Limite:** Nessuno (API pubblica gratuita)
**Post/giorno:** ~20-50

**Subreddit monitorati:**
- r/italy (discussioni italiane generali)
- r/cancer (supporto pazienti e famiglie)
- r/CancerFamilySupport
- r/AskDocs (domande mediche)
- r/medicine
- r/Health

**Caratteristiche:**
- ✅ Esperienze personali e discussioni
- ✅ Domande/risposte dirette
- ✅ Linguaggio colloquiale
- ⚠️ Qualità molto variabile
- ⚠️ Possibile disinformazione
- ⚠️ Opinioni non verificate

**Utilità:** Ottimo per identificare claim dubbi, esperienze aneddotiche, consigli non scientifici

---

## 📊 Flusso di Lavoro

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│  News API   │────▶│              │     │          │
│  (~30 art.) │     │              │     │          │
└─────────────┘     │   AGGREG.    │────▶│  FILTRO  │
                    │   ~200 art.  │     │  SMART   │
┌─────────────┐     │              │     │          │
│Google News  │────▶│              │     │          │
│ (~100 art.) │     │              │     │          │
└─────────────┘     └──────────────┘     └─────┬────┘
                                                │
┌─────────────┐                                 │
│   Reddit    │                                 ▼
│  (~30 post) │                          ┌─────────────┐
└─────────────┘                          │  DATABASE   │
                                         │  ~100 art.  │
                                         └─────────────┘
```

### Step 1: Aggregazione
- Raccoglie da tutte le 3 fonti
- Deduplica per URL
- Normalizza formato

### Step 2: Filtro Intelligente
Applica i filtri configurati:
- ❌ Esclude: sport, necrologi, politica, oroscopi
- ✅ Richiede: almeno una keyword medica/terapeutica
- ✅ Topic: deve parlare di tumori/terapie

### Step 3: Scraping
- Estrae testo completo
- Usa newspaper3k + BeautifulSoup
- Salva in database

---

## 🎯 Risultati Attesi

**Prima (solo News API):**
- ~20-50 articoli/giorno
- Solo fonti mainstream
- Qualità alta ma coverage limitato

**Ora (3 fonti):**
- ~100-300 articoli/giorno
- Mix di fonti (mainstream + blog + discussioni)
- Qualità variabile (OTTIMO per analisi affidabilità!)

---

## ⚙️ Configurazione

Tutte le fonti usano le stesse **keywords** configurate in `config.yaml`:

```yaml
keywords:
  - "terapia antitumorale"
  - "immunoterapia"
  - "CAR-T"
  - "tumore polmone"
  # ... ecc
```

### Abilitare/Disabilitare Fonti

Per disabilitare temporaneamente una fonte, commenta nel `main.py`:

```python
# FONTE 2: Google News
# try:
#     logger.info("\n>>> Fonte 2/3: Google News RSS")
#     google_fetcher = GoogleNewsFetcher(config)
#     google_articles = google_fetcher.fetch_all_keywords(keywords, max_per_keyword=30)
#     ...
```

---

## 🔧 Installazione sul VPS

```bash
cd ~/onconews
git pull

# Installa nuova dipendenza
source venv/bin/activate
pip install feedparser

# Test
python3 main.py
```

---

## 📈 Monitoraggio

### Vedere da Quale Fonte Proviene un Articolo

Nel database, campo `source_name`:
- **News API**: nome testata (es: "La Repubblica")
- **Google News**: nome sito estratto da RSS
- **Reddit**: "Reddit r/subreddit" (es: "Reddit r/cancer")

### Query SQL per Statistiche per Fonte

```sql
-- Conta articoli per fonte
SELECT source_name, COUNT(*) as count
FROM news
GROUP BY source_name
ORDER BY count DESC
LIMIT 20;

-- Articoli da Reddit
SELECT title, source_name
FROM news
WHERE source_name LIKE 'Reddit%'
LIMIT 10;
```

---

## 🎨 Esempi di Contenuti Catturati

### News API
```
Titolo: "Nuovo farmaco immunoterapico approvato da AIFA per melanoma"
Fonte: ANSA
Qualità: Alta
```

### Google News
```
Titolo: "Terapia CAR-T: la mia esperienza al San Raffaele"
Fonte: blog-salute-personale.it
Qualità: Media-Bassa (esperienza personale)
```

### Reddit
```
Titolo: "Mio padre ha il tumore al polmone, quali terapie consigliate?"
Fonte: Reddit r/cancer
Qualità: Bassa (domanda utente, non verificato)
```

**Tutti e 3 i tipi sono utili per l'analisi dell'affidabilità!**

---

## 🐛 Troubleshooting

### Google News non restituisce risultati

**Causa:** Google potrebbe bloccare temporaneamente se troppi request
**Soluzione:** Riduci `max_per_keyword` nel main.py

### Reddit API fallisce

**Causa:** Rate limiting o Reddit down
**Soluzione:** Il sistema continua con le altre fonti, Reddit sarà ritentato al prossimo run

### Troppi articoli duplicati

**Causa:** Stesso articolo appare su più fonti
**Soluzione:** Il sistema deduplica automaticamente per URL

---

## 📚 Prossimi Step

Fonti potenziali da aggiungere:
- [ ] Forum italiani (ForumSalute.it, Medicitalia.it)
- [ ] PubMed (articoli scientifici peer-reviewed)
- [ ] Twitter/X (richiede API a pagamento)
- [ ] RSS feed siti oncologici (AIOM, Fondazione Veronesi)

---

**🎉 Buona raccolta dati!**
