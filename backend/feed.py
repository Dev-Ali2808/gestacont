import feedparser
from datetime import datetime

FEEDS = [
    "https://www.contabeis.com.br/rss/noticias/",
    "https://www.portaltributario.com.br/feed",
    "https://receita.economia.gov.br/noticias/feed",
]

def buscar_noticias(limite=10):
    noticias = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                noticias.append({
                    "titulo": entry.get("title", "Sem titulo"),
                    "link": entry.get("link", ""),
                    "resumo": entry.get("summary", "")[:200],
                    "fonte": feed.feed.get("title", "Fonte desconhecida"),
                    "data": entry.get("published", str(datetime.utcnow()))
                })
        except:
            continue
    return noticias[:limite]
