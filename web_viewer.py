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

# Template HTML moderno ispirato ad Art Design Pro
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OncoNews - Notizie Terapie Antitumorali</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Modern Color Palette - Inspired by Art Design Pro */
            --primary-50: #eef2ff;
            --primary-100: #e0e7ff;
            --primary-500: #6366f1;
            --primary-600: #4f46e5;
            --primary-700: #4338ca;

            --success-50: #ecfdf5;
            --success-500: #10b981;
            --success-600: #059669;

            --warning-50: #fef3c7;
            --warning-500: #f59e0b;
            --warning-600: #d97706;

            --danger-50: #fef2f2;
            --danger-500: #ef4444;
            --danger-600: #dc2626;

            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;

            /* Theme Variables */
            --bg-primary: #ffffff;
            --bg-secondary: var(--gray-50);
            --bg-tertiary: var(--gray-100);
            --text-primary: var(--gray-900);
            --text-secondary: var(--gray-600);
            --text-tertiary: var(--gray-500);
            --border-color: var(--gray-200);

            /* Spacing */
            --spacing-xs: 0.5rem;
            --spacing-sm: 0.75rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;
            --spacing-2xl: 3rem;

            /* Border Radius */
            --radius-sm: 0.375rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            --radius-full: 9999px;

            /* Shadows */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, var(--gray-50) 0%, #fff 100%);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            padding: var(--spacing-lg);
        }

        .container {
            max-width: 1280px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
            color: white;
            padding: var(--spacing-2xl) var(--spacing-xl);
            border-radius: var(--radius-xl);
            margin-bottom: var(--spacing-xl);
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="0.5" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.1;
        }

        .header-content {
            position: relative;
            z-index: 1;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: var(--spacing-sm);
            letter-spacing: -0.02em;
        }

        .subtitle {
            font-size: 1.125rem;
            opacity: 0.9;
            font-weight: 400;
        }

        /* Stats Grid */
        .stats-section {
            margin-bottom: var(--spacing-xl);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-lg);
        }

        .stat-card {
            background: var(--bg-primary);
            padding: var(--spacing-xl);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--card-color) 0%, var(--card-color-dark) 100%);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }

        .stat-card:hover::before {
            opacity: 1;
        }

        .stat-card.primary { --card-color: var(--primary-500); --card-color-dark: var(--primary-600); }
        .stat-card.success { --card-color: var(--success-500); --card-color-dark: var(--success-600); }
        .stat-card.warning { --card-color: var(--warning-500); --card-color-dark: var(--warning-600); }
        .stat-card.danger { --card-color: var(--danger-500); --card-color-dark: var(--danger-600); }

        .stat-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }

        .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: var(--radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }

        .stat-card.primary .stat-icon { background: var(--primary-50); }
        .stat-card.success .stat-icon { background: var(--success-50); }
        .stat-card.warning .stat-icon { background: var(--warning-50); }
        .stat-card.danger .stat-icon { background: var(--danger-50); }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1;
            background: linear-gradient(135deg, var(--card-color) 0%, var(--card-color-dark) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Filters */
        .filters-card {
            background: var(--bg-primary);
            padding: var(--spacing-xl);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            margin-bottom: var(--spacing-xl);
            border: 1px solid var(--border-color);
        }

        .filters-title {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: var(--spacing-lg);
            color: var(--text-primary);
        }

        .filters-form {
            display: flex;
            gap: var(--spacing-md);
            flex-wrap: wrap;
            align-items: flex-end;
        }

        .form-group {
            flex: 1;
            min-width: 200px;
        }

        .form-label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: var(--spacing-xs);
        }

        .form-input, .form-select {
            width: 100%;
            padding: 0.625rem 1rem;
            border: 1.5px solid var(--border-color);
            border-radius: var(--radius-md);
            font-size: 0.9375rem;
            font-family: inherit;
            transition: all 0.2s;
            background: var(--bg-primary);
            color: var(--text-primary);
        }

        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: var(--primary-500);
            box-shadow: 0 0 0 3px var(--primary-50);
        }

        .btn {
            padding: 0.625rem 1.5rem;
            border-radius: var(--radius-md);
            font-weight: 500;
            font-size: 0.9375rem;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
            font-family: inherit;
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-xs);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
            color: white;
            box-shadow: var(--shadow-sm);
        }

        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }

        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
        }

        .btn-secondary:hover {
            background: var(--gray-200);
            color: var(--text-primary);
        }

        /* Articles */
        .article {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .article:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
            border-color: var(--primary-200);
        }

        .article-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: var(--spacing-md);
            line-height: 1.4;
        }

        .article-meta {
            display: flex;
            gap: var(--spacing-lg);
            flex-wrap: wrap;
            margin-bottom: var(--spacing-md);
            padding-bottom: var(--spacing-md);
            border-bottom: 1px solid var(--border-color);
        }

        .meta-item {
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-xs);
            font-size: 0.875rem;
            color: var(--text-secondary);
        }

        .keywords {
            display: flex;
            gap: var(--spacing-xs);
            flex-wrap: wrap;
            margin: var(--spacing-md) 0;
        }

        .keyword-tag {
            background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
            color: var(--primary-700);
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-full);
            font-size: 0.8125rem;
            font-weight: 500;
            border: 1px solid var(--primary-200);
        }

        .article-description {
            color: var(--text-secondary);
            line-height: 1.7;
            margin-bottom: var(--spacing-md);
        }

        .article-text {
            color: var(--text-secondary);
            line-height: 1.8;
            margin-top: var(--spacing-lg);
            padding-top: var(--spacing-lg);
            border-top: 1px solid var(--border-color);
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
            height: 80px;
            background: linear-gradient(to bottom, transparent, var(--bg-primary));
        }

        .expand-btn {
            margin-top: var(--spacing-md);
            background: var(--gray-100);
            color: var(--text-secondary);
            padding: 0.5rem 1rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
        }

        .expand-btn:hover {
            background: var(--primary-50);
            color: var(--primary-700);
            border-color: var(--primary-200);
        }

        .article-link {
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-xs);
            color: var(--primary-600);
            text-decoration: none;
            margin-top: var(--spacing-md);
            font-weight: 500;
            font-size: 0.9375rem;
            transition: all 0.2s;
        }

        .article-link:hover {
            color: var(--primary-700);
            gap: var(--spacing-sm);
        }

        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            gap: var(--spacing-sm);
            margin-top: var(--spacing-2xl);
        }

        .pagination a, .pagination span {
            padding: 0.625rem 1rem;
            border-radius: var(--radius-md);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9375rem;
            transition: all 0.2s;
        }

        .pagination a {
            background: var(--bg-primary);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }

        .pagination a:hover {
            background: var(--primary-50);
            color: var(--primary-700);
            border-color: var(--primary-200);
        }

        .pagination span {
            background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
            color: white;
            border: 1px solid var(--primary-600);
        }

        /* Empty State */
        .no-results {
            text-align: center;
            padding: var(--spacing-2xl);
            background: var(--bg-primary);
            border-radius: var(--radius-lg);
            border: 2px dashed var(--border-color);
        }

        .no-results-icon {
            font-size: 4rem;
            margin-bottom: var(--spacing-md);
            opacity: 0.3;
        }

        .no-results h2 {
            color: var(--text-primary);
            margin-bottom: var(--spacing-sm);
        }

        .no-results p {
            color: var(--text-secondary);
        }

        /* Responsive */
        @media (max-width: 768px) {
            body {
                padding: var(--spacing-md);
            }

            h1 {
                font-size: 2rem;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .filters-form {
                flex-direction: column;
            }

            .form-group {
                width: 100%;
            }
        }

        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .article {
            animation: fadeIn 0.5s ease-out;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-content">
                <h1>🩺 OncoNews</h1>
                <div class="subtitle">Sistema di raccolta notizie su terapie antitumorali innovative</div>
            </div>
        </div>

        <!-- Stats Section -->
        <div class="stats-section">
            <div class="stats-grid">
                <div class="stat-card primary">
                    <div class="stat-header">
                        <div class="stat-icon">📊</div>
                        <div class="stat-label">Articoli Totali</div>
                    </div>
                    <div class="stat-value">{{ stats.total }}</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-header">
                        <div class="stat-icon">✅</div>
                        <div class="stat-label">Testo Completo</div>
                    </div>
                    <div class="stat-value">{{ stats.scraped }}</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-header">
                        <div class="stat-icon">⏳</div>
                        <div class="stat-label">In Attesa</div>
                    </div>
                    <div class="stat-value">{{ stats.pending }}</div>
                </div>
                <div class="stat-card danger">
                    <div class="stat-header">
                        <div class="stat-icon">❌</div>
                        <div class="stat-label">Falliti</div>
                    </div>
                    <div class="stat-value">{{ stats.failed }}</div>
                </div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filters-card">
            <h3 class="filters-title">🔍 Filtra Articoli</h3>
            <form method="GET" class="filters-form">
                <div class="form-group">
                    <label class="form-label">Cerca per titolo</label>
                    <input type="text" name="search" class="form-input" placeholder="Inserisci parole chiave..." value="{{ search }}">
                </div>
                <div class="form-group">
                    <label class="form-label">Fonte</label>
                    <select name="source" class="form-select">
                        <option value="">Tutte le fonti</option>
                        {% for source in sources %}
                        <option value="{{ source }}" {% if source == selected_source %}selected{% endif %}>{{ source }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">🔍 Cerca</button>
                <a href="/" class="btn btn-secondary">↻ Ripristina</a>
            </form>
        </div>

        <!-- Articles List -->
        {% if articles %}
            {% for article in articles %}
            <article class="article">
                <h2 class="article-title">{{ article.title }}</h2>

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
                    <span class="keyword-tag">{{ keyword.strip() }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                {% if article.description %}
                <p class="article-description">{{ article.description }}</p>
                {% endif %}

                {% if article.full_text %}
                <div class="article-text collapsed" id="text-{{ loop.index }}">
                    {{ article.full_text }}
                </div>
                {% if article.full_text|length > 500 %}
                <button class="expand-btn" onclick="toggleText('text-{{ loop.index }}', this)">
                    📖 Leggi tutto ({{ article.full_text|length }} caratteri)
                </button>
                {% endif %}
                {% endif %}

                <a href="{{ article.url }}" target="_blank" class="article-link">
                    🔗 Leggi articolo originale →
                </a>
            </article>
            {% endfor %}

            <!-- Pagination -->
            {% if total_pages > 1 %}
            <div class="pagination">
                {% if page > 1 %}
                <a href="?page={{ page - 1 }}{% if search %}&search={{ search }}{% endif %}{% if selected_source %}&source={{ selected_source }}{% endif %}">
                    ← Precedente
                </a>
                {% endif %}

                <span>Pagina {{ page }} di {{ total_pages }}</span>

                {% if page < total_pages %}
                <a href="?page={{ page + 1 }}{% if search %}&search={{ search }}{% endif %}{% if selected_source %}&source={{ selected_source }}{% endif %}">
                    Successiva →
                </a>
                {% endif %}
            </div>
            {% endif %}
        {% else %}
            <!-- Empty State -->
            <div class="no-results">
                <div class="no-results-icon">📭</div>
                <h2>Nessun articolo trovato</h2>
                <p>Prova a modificare i filtri di ricerca o attendi la prossima raccolta automatica</p>
            </div>
        {% endif %}
    </div>

    <script>
    function toggleText(id, btn) {
        const textDiv = document.getElementById(id);
        if (textDiv.classList.contains('collapsed')) {
            textDiv.classList.remove('collapsed');
            btn.innerHTML = '📕 Comprimi';
        } else {
            textDiv.classList.add('collapsed');
            const charCount = textDiv.textContent.trim().length;
            btn.innerHTML = `📖 Leggi tutto (${charCount} caratteri)`;
        }
    }

    // Smooth scroll per i link interni
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Animazione fade-in al caricamento
    window.addEventListener('load', () => {
        document.querySelectorAll('.article').forEach((article, index) => {
            article.style.animationDelay = `${index * 0.05}s`;
        });
    });
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
