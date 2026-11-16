import json, time, datetime, urllib.parse, urllib.request
from pathlib import Path

UA = {"User-Agent": "revision-literatura-curso-ML/1.0", "Accept": "application/vnd.github+json"}
CONSULTAS = ["ordinal random forest", "ordinal forest", "ordered forest", "cumulative probability random forest ordinal",
             "wine quality ordinal", "extremely randomized trees ordinal", "threshold weighted ranked probability score"]


def buscar(q):
    """Busca repositorios en GitHub ordenados por relevancia.

    Parameters
    ----------
    q : str
        Texto de la consulta.

    Returns
    -------
    dict
        Consulta, número total de repositorios y los 15 primeros.
    """
    url = "https://api.github.com/search/repositories?per_page=15&q=" + urllib.parse.quote(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        j = json.loads(r.read())
    items = [{"repo": i["full_name"], "estrellas": i["stargazers_count"], "lenguaje": i["language"],
              "descripcion": (i["description"] or "")[:200]} for i in j.get("items", [])]
    return {"consulta": q, "total": j.get("total_count"), "items": items}


salida = {"fecha": datetime.datetime.now().isoformat(timespec="seconds"), "consultas": []}
for q in CONSULTAS:
    salida["consultas"].append(buscar(q))
    print(q, salida["consultas"][-1]["total"], flush=True)
    time.sleep(7)
Path(__file__).with_name(f"repositorios_{datetime.date.today().isoformat()}.json").write_text(
    json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
