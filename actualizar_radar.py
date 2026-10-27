import json
import os
from datetime import datetime
import feedparser

# Fuentes RSS científicas principales
FEEDS = [
    {"url": "https://www.nature.com/nature.rss", "category": "bio", "provider": "nature", "source": "Nature"},
    {"url": "https://www.nature.com/natastron.rss", "category": "astro", "provider": "nature", "source": "Nature Astronomy"},
    {"url": "https://www.nature.com/nphys.rss", "category": "physics", "provider": "nature", "source": "Nature Physics"},
    {"url": "https://www.nature.com/ng.rss", "category": "genetics", "provider": "nature", "source": "Nature Genetics"},
    {"url": "https://www.nature.com/nataging.rss", "category": "longevity", "provider": "nature", "source": "Nature Aging"},
    {"url": "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science", "category": "physics", "provider": "science", "source": "Science"},
    {"url": "https://www.sciencedaily.com/rss/space_time.xml", "category": "astro", "provider": "press", "source": "ScienceDaily Space"},
    {"url": "https://www.sciencedaily.com/rss/health_medicine/healthy_aging.xml", "category": "longevity", "provider": "press", "source": "ScienceDaily Longevity"},
    {"url": "https://news.mit.edu/rss/topic/artificial-intelligence2", "category": "ai_tech", "provider": "press", "source": "MIT News AI"}
]

def obtener_noticias_actuales():
    nuevas_noticias = []
    seen_links = set()

    for feed_info in FEEDS:
        try:
            parsed = feedparser.parse(feed_info["url"])
            for entry in parsed.entries[:6]:
                link = entry.get("link", "")
                title = entry.get("title", "Sin título")
                summary = entry.get("summary", entry.get("description", ""))
                
                if link and link not in seen_links:
                    seen_links.add(link)
                    nuevas_noticias.append({
                        "title": title,
                        "link": link,
                        "description": summary[:300] + "...",
                        "pubDate": entry.get("published", datetime.now().isoformat()),
                        "category": feed_info["category"],
                        "provider": feed_info["provider"],
                        "source": feed_info["source"]
                    })
        except Exception as e:
            print(f"Error leyendo feed {feed_info['source']}: {e}")

    return nuevas_noticias

def main():
    archivo_json = "noticias_auto.json"
    
    # Cargar histórico anterior si existe
    historico = []
    if os.path.exists(archivo_json):
        try:
            with open(archivo_json, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except:
            historico = []

    links_existentes = {item["link"] for item in historico}
    nuevas = obtener_noticias_actuales()

    # Añadir las nuevas al principio del histórico
    agregadas = 0
    for n in nuevas:
        if n["link"] not in links_existentes:
            historico.insert(0, n)
            agregadas += 1

    # Mantener un límite razonable (ej. las últimas 300 noticias para la hemeroteca)
    historico = historico[:300]

  # Guardar en JSON (como respaldo)
    with open('noticias_auto.json', 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=2)

    # Guardar directamente como script JS para el frontend
    with open('noticias.js', 'w', encoding='utf-8') as f:
        f.write("window.NOTICIAS_AUTO = " + json.dumps(noticias_finales, ensure_ascii=False, indent=2) + ";\n")

if __name__ == "__main__":
    main()
