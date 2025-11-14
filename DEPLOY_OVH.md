# 🚀 Guida Deploy OncoNews su VPS OVH - Step by Step

Guida completa per portare OncoNews sul tuo VPS OVH con comandi pronti da copiare/incollare.

---

## 📋 Prerequisiti

Prima di iniziare, assicurati di avere:
- ✅ **IP del VPS OVH** (ricevuto via email da OVH)
- ✅ **Credenziali di accesso** (username e password o chiave SSH)
- ✅ **API key di News API** (da https://newsapi.org)

---

## FASE 1: Connessione al VPS OVH

### Step 1.1 - Apri il Terminale

**Su Windows:**
- Usa PowerShell o scarica [PuTTY](https://www.putty.org/)

**Su Mac/Linux:**
- Apri il Terminale (già installato)

### Step 1.2 - Connettiti via SSH

Sostituisci `INDIRIZZO_IP_VPS` con il tuo IP reale:

```bash
ssh root@INDIRIZZO_IP_VPS
```

Esempio:
```bash
ssh root@51.38.123.45
```

**Cosa succede:**
- Ti chiederà di confermare il fingerprint (digita `yes`)
- Ti chiederà la password (quella ricevuta via email da OVH)

✅ **Sei dentro!** Vedrai un prompt tipo `root@vps123456:~#`

---

## FASE 2: Sicurezza Iniziale

### Step 2.1 - Cambia la Password di Root

```bash
passwd
```

Ti chiederà di inserire una nuova password sicura (2 volte).

### Step 2.2 - Aggiorna il Sistema

```bash
apt update && apt upgrade -y
```

⏱️ Attendi 2-5 minuti (installerà aggiornamenti)

### Step 2.3 - Installa Dipendenze Base

```bash
apt install -y python3 python3-pip python3-venv git curl
```

### Step 2.4 - Crea Utente Dedicato

```bash
adduser onconews
```

Ti chiederà:
- **Password**: scegli una password sicura
- **Nome completo**: premi Invio (lascia vuoto)
- **Numero stanza, telefono, ecc.**: premi Invio (lascia vuoto)
- Conferma con `Y`

### Step 2.5 - Dai Privilegi Sudo

```bash
usermod -aG sudo onconews
```

### Step 2.6 - Passa al Nuovo Utente

```bash
su - onconews
```

✅ Il prompt cambierà in `onconews@vps123456:~$`

---

## FASE 3: Deploy OncoNews

### Step 3.1 - Clone del Repository

**Opzione A: Repository Pubblico** (se il repo è pubblico su GitHub)

```bash
cd ~
git clone https://github.com/sergiocima/onconews.git
cd onconews
```

**Opzione B: Repository Privato** (se richiede autenticazione)

```bash
cd ~
git clone https://github.com/sergiocima/onconews.git
# Ti chiederà username e password/token GitHub
cd onconews
```

**Opzione C: Upload Manuale** (se preferisci caricare i file)

Dal tuo PC locale (apri un NUOVO terminale, non chiudere quello del VPS):

```bash
# Comprimi il progetto
cd /percorso/al/progetto/onconews
tar -czf onconews.tar.gz .

# Carica sul VPS (sostituisci IP)
scp onconews.tar.gz onconews@INDIRIZZO_IP_VPS:/home/onconews/

# Torna al terminale SSH del VPS ed estrai
cd ~
tar -xzf onconews.tar.gz
rm onconews.tar.gz
```

### Step 3.2 - Rendi Eseguibile lo Script di Deploy

```bash
chmod +x deploy_ovh.sh
```

### Step 3.3 - Configura la API Key

```bash
nano .env
```

**Scrivi dentro il file:**
```
NEWS_API_KEY=la_tua_chiave_api_vera
```

**Salva e esci:**
1. Premi `Ctrl + X`
2. Premi `Y` (per confermare)
3. Premi `Invio`

### Step 3.4 - Esegui lo Script di Deploy Automatico

```bash
./deploy_ovh.sh
```

**Cosa fa lo script:**
1. ✅ Verifica Python
2. ✅ Crea ambiente virtuale
3. ✅ Installa tutte le dipendenze
4. ✅ Scarica dati NLTK
5. ✅ Verifica API key
6. ✅ Esegue un test completo
7. ✅ Configura esecuzione automatica giornaliera

⏱️ Durata: 3-5 minuti

Quando ti chiede **"Vuoi configurare l'esecuzione automatica?"**, digita `y` e premi Invio.

---

## FASE 4: Verifica che Tutto Funzioni

### Step 4.1 - Controlla i Log

```bash
tail -f onconews.log
```

Dovresti vedere:
- ✅ Validazione API key riuscita
- ✅ Articoli recuperati
- ✅ Scraping completato
- ✅ Statistiche database

Premi `Ctrl + C` per uscire dalla visualizzazione log.

### Step 4.2 - Verifica Database

```bash
sqlite3 onconews.db "SELECT COUNT(*) FROM news;"
```

Dovresti vedere un numero > 0 (gli articoli scaricati).

### Step 4.3 - Analisi Dettagliata

```bash
source venv/bin/activate
python3 analyze.py
```

Ti mostrerà statistiche dettagliate.

### Step 4.4 - Verifica Cron

```bash
crontab -l
```

Dovresti vedere una riga tipo:
```
0 8 * * * cd /home/onconews/onconews && /home/onconews/onconews/venv/bin/python3 main.py >> /home/onconews/onconews_cron.log 2>&1
```

Significa: **ogni giorno alle 8:00** il sistema scaricherà automaticamente nuove notizie.

---

## FASE 5: Configurazione Firewall (Opzionale ma Consigliato)

```bash
sudo ufw allow OpenSSH
sudo ufw enable
```

Conferma con `y`.

---

## 🎉 COMPLETATO!

Il tuo sistema OncoNews è attivo sul VPS OVH e funzionerà automaticamente ogni giorno.

---

## 📊 Comandi Utili Quotidiani

### Visualizzare i Log in Tempo Reale
```bash
tail -f ~/onconews/onconews.log
```

### Vedere il Log del Cron
```bash
tail -f ~/onconews_cron.log
```

### Eseguire Manualmente (per test)
```bash
cd ~/onconews
source venv/bin/activate
python3 main.py
```

### Statistiche Database
```bash
cd ~/onconews
source venv/bin/activate
python3 analyze.py
```

### Backup Manuale Database
```bash
cp ~/onconews/onconews.db ~/onconews_backup_$(date +%Y%m%d).db
```

### Controllare Spazio Disco
```bash
df -h
```

### Aggiornare il Codice (se fai modifiche su GitHub)
```bash
cd ~/onconews
git pull
```

---

## 🔄 Come Riconnettersi al VPS

Ogni volta che vorrai accedere di nuovo al VPS:

```bash
ssh onconews@INDIRIZZO_IP_VPS
```

Poi vai nella directory del progetto:
```bash
cd onconews
source venv/bin/activate
```

---

## 🐛 Risoluzione Problemi

### Errore: "Permission denied" durante SSH

**Causa:** Password errata o IP bloccato

**Soluzione:**
1. Verifica di usare la password corretta
2. Controlla dallo Spazio Cliente OVH che il VPS sia attivo
3. Prova a fare reboot del VPS dal pannello OVH

### Errore: "NEWS_API_KEY not found"

**Causa:** File .env non configurato correttamente

**Soluzione:**
```bash
cd ~/onconews
cat .env  # Verifica il contenuto
nano .env  # Modifica se necessario
```

### Errore: "No space left on device"

**Causa:** Disco pieno

**Soluzione:**
```bash
df -h  # Controlla lo spazio
# Cancella vecchi backup se necessario
rm ~/onconews_backup_*.db
```

### Il Cron Non Parte

**Verifica che il cron service sia attivo:**
```bash
sudo systemctl status cron
```

**Se non è attivo, avvialo:**
```bash
sudo systemctl start cron
sudo systemctl enable cron
```

### Script Non Si Connette a News API

**Causa:** Chiave API non valida o limite raggiunto

**Soluzione:**
1. Verifica la chiave su https://newsapi.org/account
2. Controlla di non aver superato il limite di 100 richieste/giorno
3. Aspetta 24h se hai raggiunto il limite

---

## 📞 Support

- **News API:** https://newsapi.org/docs
- **Documentazione OVH:** https://help.ovhcloud.com/
- **Issues GitHub:** https://github.com/sergiocima/onconews/issues

---

## 💾 Backup Automatico (Consigliato)

Per configurare un backup settimanale automatico:

```bash
crontab -e
```

Aggiungi questa riga in fondo:
```
0 3 * * 0 cp /home/onconews/onconews/onconews.db /home/onconews/backups/onconews_$(date +\%Y\%m\%d).db
```

Prima crea la directory backup:
```bash
mkdir -p ~/backups
```

---

## 🎯 Prossimi Passi

Dopo alcuni giorni di raccolta dati:
1. Analizza le statistiche con `analyze.py`
2. Esporta i dati per analisi avanzate con SBERT
3. Crea dashboard di visualizzazione
4. Implementa analisi di sentiment

---

**🚀 Buon lavoro con OncoNews!**
