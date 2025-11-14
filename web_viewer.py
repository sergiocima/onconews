#!/usr/bin/env python3
"""
OncoNews Web Viewer - Visualizzazione articoli via browser
Supporta sia SQLite che PostgreSQL
"""
import os
from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)

# Rileva quale database usare
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor

# Template HTML semplice e pulito
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OncoNews - Articoli</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-box {
            background: #3498db;
            color: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        .stat-box.success { background: #27ae60; }
        .stat-box.warning { background: #f39c12; }
        .stat-box.danger { background: #e74c3c; }
        .stat-value { font-size: 2em; font-weight: bold; display: block; }
        .stat-label { font-size: 0.9em; opacity: 0.9; margin-top: 5px; }

        .filters {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .filters input, .filters select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-right: 10px;
            font-size: 14px;
        }
        .filters button {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .filters button:hover { background: #2980b9; }

        .article {
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .article:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .article-title {
            color: #2c3e50;
            font-size: 1.4em;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .article-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 15px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .meta-item {
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .article-description {
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .article-text {
            color: #666;
            line-height: 1.8;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        .article-text.collapsed {
            max-height: 150px;
            overflow: hidden;
            position: relative;
        }
        .article-text.collapsed::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 50px;
            background: linear-gradient(transparent, white);
        }
        .expand-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
            font-size: 14px;
        }
        .expand-btn:hover {
            background: #2980b9;
        }
        .keywords {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 10px 0;
        }
        .keyword {
            background: #e8f4f8;
            color: #3498db;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .article-link {
            display: inline-block;
            color: #3498db;
            text-decoration: none;
            margin-top: 10px;
            font-weight: 500;
        }
        .article-link:hover { text-decoration: underline; }

        .no-results {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
        }
        .pagination a, .pagination span {
            padding: 8px 15px;
            background: white;
            border-radius: 4px;
            text-decoration: none;
            color: #3498db;
        }
        .pagination span { background: #3498db; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🩺 OncoNews - Notizie Terapie Antitumorali</h1>

        <div class="stats">
            <h3>Statistiche Database</h3>
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-value">{{ stats.total }}</span>
                    <span class="stat-label">Articoli Totali</span>
                </div>
                <div class="stat-box success">
                    <span class="stat-value">{{ stats.scraped }}</span>
                    <span class="stat-label">Testo Completo</span>
                </div>
                <div class="stat-box warning">
                    <span class="stat-value">{{ stats.pending }}</span>
                    <span class="stat-label">In Attesa</span>
                </div>
                <div class="stat-box danger">
                    <span class="stat-value">{{ stats.failed }}</span>
                    <span class="stat-label">Falliti</span>
                </div>
            </div>
        </div>

        <div class="filters">
            <form method="GET">
                <input type="text" name="search" placeholder="Cerca per titolo..." value="{{ search }}" style="width: 300px;">
                <select name="source">
                    <option value="">Tutte le fonti</option>
                    {% for source in sources %}
                    <option value="{{ source }}" {% if source == selected_source %}selected{% endif %}>{{ source }}</option>
                    {% endfor %}
                </select>
                <button type="submit">🔍 Cerca</button>
                <a href="/" style="margin-left: 10px; color: #3498db; text-decoration: none;">Ripristina</a>
            </form>
        </div>

        {% if articles %}
            {% for article in articles %}
            <div class="article">
                <div class="article-title">{{ article.title }}</div>
                <div class="article-meta">
                    <span class="meta-item">📰 {{ article.source_name or 'Fonte sconosciuta' }}</span>
                    <span class="meta-item">📅 {{ article.published_at }}</span>
                    {% if article.author %}
                    <span class="meta-item">✍️ {{ article.author }}</span>
                    {% endif %}
                </div>

                {% if article.keywords_matched %}
                <div class="keywords">
                    {% for keyword in article.keywords_matched.split(',') %}
                    <span class="keyword">{{ keyword.strip() }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                {% if article.description %}
                <div class="article-description">{{ article.description }}</div>
                {% endif %}

                {% if article.full_text %}
                <div class="article-text collapsed" id="text-{{ loop.index }}">
                    {{ article.full_text }}
                </div>
                {% if article.full_text|length > 500 %}
                <button class="expand-btn" onclick="toggleText('text-{{ loop.index }}', this)">📖 Leggi tutto ({{ article.full_text|length }} caratteri)</button>
                {% endif %}
                {% endif %}

                <a href="{{ article.url }}" target="_blank" class="article-link">🔗 Leggi articolo originale →</a>
            </div>
            {% endfor %}

            {% if total_pages > 1 %}
            <div class="pagination">
                {% if page > 1 %}
                <a href="?page={{ page - 1 }}{% if search %}&search={{ search }}{% endif %}{% if selected_source %}&source={{ selected_source }}{% endif %}">← Precedente</a>
                {% endif %}

                <span>Pagina {{ page }} di {{ total_pages }}</span>

                {% if page < total_pages %}
                <a href="?page={{ page + 1 }}{% if search %}&search={{ search }}{% endif %}{% if selected_source %}&source={{ selected_source }}{% endif %}">Successiva →</a>
                {% endif %}
            </div>
            {% endif %}
        {% else %}
            <div class="no-results">
                <h2>📭 Nessun articolo trovato</h2>
                <p>Prova a modificare i filtri di ricerca</p>
            </div>
        {% endif %}
    </div>

    <script>
    function toggleText(id, btn) {
        const textDiv = document.getElementById(id);
        if (textDiv.classList.contains('collapsed')) {
            textDiv.classList.remove('collapsed');
            btn.textContent = '📕 Comprimi';
        } else {
            textDiv.classList.add('collapsed');
            const charCount = textDiv.textContent.length;
            btn.textContent = `📖 Leggi tutto (${charCount} caratteri)`;
        }
    }
    </script>
</body>
</html>
"""

def get_db_connection():
    """Connessione al database (SQLite o PostgreSQL)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect('onconews.db')
        conn.row_factory = sqlite3.Row
        return conn

@app.route('/')
def index():
    """Pagina principale con lista articoli"""
    conn = get_db_connection()

    # Parametri di ricerca
    search = request.args.get('search', '')
    source = request.args.get('source', '')
    page = int(request.args.get('page', 1))
    per_page = 20

    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Statistiche
        cursor.execute('SELECT COUNT(*) as count FROM news')
        stats_total = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM news WHERE full_text IS NOT NULL')
        stats_scraped = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM news WHERE full_text IS NULL AND scraping_status != %s', ('failed',))
        stats_pending = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM news WHERE scraping_status = %s', ('failed',))
        stats_failed = cursor.fetchone()['count']

        stats = {
            'total': stats_total,
            'scraped': stats_scraped,
            'pending': stats_pending,
            'failed': stats_failed
        }

        # Lista fonti per filtro
        cursor.execute('SELECT DISTINCT source_name FROM news WHERE source_name IS NOT NULL ORDER BY source_name')
        sources = [row['source_name'] for row in cursor.fetchall()]

        # Query articoli con filtri
        query = 'SELECT * FROM news WHERE 1=1'
        params = []

        if search:
            query += ' AND (title LIKE %s OR description LIKE %s)'
            params.extend([f'%{search}%', f'%{search}%'])

        if source:
            query += ' AND source_name = %s'
            params.append(source)

        query += ' ORDER BY published_at DESC'

        # Conta totale risultati
        count_query = query.replace('SELECT *', 'SELECT COUNT(*) as count')
        cursor.execute(count_query, params)
        total_results = cursor.fetchone()['count']
        total_pages = (total_results + per_page - 1) // per_page

        # Paginazione
        query += ' LIMIT %s OFFSET %s'
        params.extend([per_page, (page - 1) * per_page])

        cursor.execute(query, params)
        articles = cursor.fetchall()

    else:
        # SQLite
        cursor = conn.cursor()

        # Statistiche
        stats = {
            'total': conn.execute('SELECT COUNT(*) as count FROM news').fetchone()['count'],
            'scraped': conn.execute('SELECT COUNT(*) as count FROM news WHERE full_text IS NOT NULL').fetchone()['count'],
            'pending': conn.execute('SELECT COUNT(*) as count FROM news WHERE full_text IS NULL AND scraping_status != "failed"').fetchone()['count'],
            'failed': conn.execute('SELECT COUNT(*) as count FROM news WHERE scraping_status = "failed"').fetchone()['count']
        }

        # Lista fonti per filtro
        sources = [row['source_name'] for row in conn.execute('SELECT DISTINCT source_name FROM news WHERE source_name IS NOT NULL ORDER BY source_name').fetchall()]

        # Query articoli con filtri
        query = 'SELECT * FROM news WHERE 1=1'
        params = []

        if search:
            query += ' AND (title LIKE ? OR description LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])

        if source:
            query += ' AND source_name = ?'
            params.append(source)

        query += ' ORDER BY published_at DESC'

        # Conta totale risultati
        total_results = conn.execute(query.replace('SELECT *', 'SELECT COUNT(*) as count'), params).fetchone()['count']
        total_pages = (total_results + per_page - 1) // per_page

        # Paginazione
        query += ' LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])

        articles = conn.execute(query, params).fetchall()

    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        articles=articles,
        stats=stats,
        sources=sources,
        search=search,
        selected_source=source,
        page=page,
        total_pages=total_pages
    )

if __name__ == '__main__':
    print("=" * 60)
    print("  ONCONEWS WEB VIEWER")
    print("=" * 60)
    print()
    print("🌐 Server avviato!")
    print()

    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    print(f"📊 Database: {db_type}")

    if USE_POSTGRES:
        print("🔗 Database URL: [CONFIGURED]")
    else:
        print("📁 Database File: onconews.db")

    print()
    print("Accedi da:")
    print("  - Locale: http://localhost:5000")
    if not USE_POSTGRES:
        print("  - Remoto: http://TUO_IP_VPS:5000")
    print()
    print("Premi Ctrl+C per fermare il server")
    print("=" * 60)

    # Avvia server accessibile da remoto
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
