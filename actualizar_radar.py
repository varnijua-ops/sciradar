import json
import os
import re
from datetime import datetime
import feedparser

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

def limpiar_html(texto):
    """Elimina etiquetas HTML residuales del RSS para dejar texto plano limpio."""
    if not texto:
        return ""
    texto_limpio = re.sub(r'<[^>]+>', '', texto)
    return ' '.join(texto_limpio.split())

def obtener_noticias_actuales():
    nuevas_noticias = []
    seen_links = set()

    for feed_info in FEEDS:
        try:
            parsed = feedparser.parse(feed_info["url"])
            for entry in parsed.entries[:6]:
                link = entry.get("link", "")
                title = limpiar_html(entry.get("title", "Sin título"))
                
                # Obtener el texto más largo posible disponible en el feed
                full_text = ""
                if "content" in entry and len(entry.content) > 0:
                    full_text = entry.content[0].get("value", "")
                if not full_text:
                    full_text = entry.get("summary", entry.get("description", ""))
                
                full_text_limpio = limpiar_html(full_text)
                
                # Resumen corto (copete para la tarjeta)
                copete = full_text_limpio[:220] + ("..." if len(full_text_limpio) > 220 else "")

                if link and link not in seen_links:
                    seen_links.add(link)
                    nuevas_noticias.append({
                        "title": title,
                        "link": link,
                        "description": copete,
                        "abstract": full_text_limpio if full_text_limpio else "Consulta el documento original para acceder al abstract completo.",
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
    historico = []
    
    if os.path.exists(archivo_json):
        try:
            with open(archivo_json, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except Exception:
            historico = []

    links_existentes = {item["link"] for item in historico if "link" in item}
    nuevas = obtener_noticias_actuales()

    agregadas = 0
    for n in nuevas:
        if n["link"] not in links_existentes:
            historico.insert(0, n)
            agregadas += 1

    historico = historico[:300]
    print(f"Nuevas: {agregadas} | Total: {len(historico)}")

    with open('noticias_auto.json', 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

    with open('noticias.js', 'w', encoding='utf-8') as f:
        f.write("window.NOTICIAS_AUTO = " + json.dumps(historico, ensure_ascii=False, indent=2) + ";\n")

if __name__ == "__main__":
    main()
