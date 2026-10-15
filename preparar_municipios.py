#!/usr/bin/env python3
"""
Gera municipios.json (contornos + ponto de cálculo) dos 15 municípios do PMIF.

Fonte dos contornos: pacote npm "ibge-cidades-com-poligonos" (malha municipal do IBGE; arquivo municipios-poligonos.json).
Uso:  python preparar_municipios.py caminho/municipios-poligonos.json
Só precisa rodar de novo se a lista de municípios mudar.

O contorno é simplificado (Douglas-Peucker, ~100 m) para o painel carregar rápido. O ponto de cálculo (onde o modelo
é consultado) é o centro de massa do maior polígono do município, exceto onde esse centro cai fora de terra firme
ou em área pouco representativa (ver PONTO_MANUAL).
"""
import ast
import json
import sys
from pathlib import Path

NOMES = ["Barra do Piraí", "Engenheiro Paulo de Frontin", "Itaguaí", "Japeri", "Mangaratiba", "Mendes", "Miguel Pereira",
         "Nova Iguaçu", "Paracambi", "Piraí", "Queimados", "Rio Claro", "Rio de Janeiro", "Seropédica", "Vassouras"]
PONTO_MANUAL = {}          # nome -> (lat, lon), preencher se o centro de massa cair no mar
TOLERANCIA = 0.0008        # graus (~90 m)


def _dist_seg(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** 0.5


def simplificar(pts, tol):
    """Douglas-Peucker iterativo (anel fechado: mantém primeiro e último)."""
    if len(pts) < 5:
        return pts
    manter = [False] * len(pts)
    manter[0] = manter[-1] = True
    pilha = [(0, len(pts) - 1)]
    while pilha:
        i, j = pilha.pop()
        dmax, k = 0.0, None
        for n in range(i + 1, j):
            d = _dist_seg(pts[n], pts[i], pts[j])
            if d > dmax:
                dmax, k = d, n
        if k is not None and dmax > tol:
            manter[k] = True
            pilha += [(i, k), (k, j)]
    return [p for p, m in zip(pts, manter) if m]


def centro(anel):
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(anel, anel[1:] + anel[:1]):
        f = x0 * y1 - x1 * y0
        a += f
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    a /= 2
    return abs(a), (cx / (6 * a), cy / (6 * a))


def main(caminho):
    base = json.loads(Path(caminho).read_text(encoding="utf-8"))
    por_nome = {m["municipioNome"]: m for m in base if m["ufSigla"] == "RJ"}
    faltando = [n for n in NOMES if n not in por_nome]
    if faltando:
        raise SystemExit(f"não encontrados no arquivo: {faltando}")
    saida = []
    for n in NOMES:
        m = por_nome[n]
        g = m["poligono"]
        if isinstance(g, str):
            g = ast.literal_eval(g)   # no pacote o GeoJSON vem como texto
        polis = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        maior = max(polis, key=lambda p: centro(p[0])[0])
        lon, lat = centro(maior[0])[1]
        if n in PONTO_MANUAL:
            lat, lon = PONTO_MANUAL[n]
        arred = lambda an: [[round(x, 4), round(y, 4)] for x, y in an]
        # descarta ilhotas muito pequenas (ruído visual) mas mantém o polígono principal
        polis = [p for p in polis if centro(p[0])[0] > 2e-5 or p is maior]
        saida.append({"codigo_ibge": m["municipioCodigo"], "nome": n, "latitude": round(lat, 4), "longitude": round(lon, 4),
                      "poligonos": [[arred(simplificar(an, TOLERANCIA)) for an in p] for p in polis]})
    Path(__file__).with_name("municipios.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for m in saida:
        print(m["codigo_ibge"], m["nome"], m["latitude"], m["longitude"], len(m["poligonos"]), "polígonos,",
              sum(len(p[0]) for p in m["poligonos"]), "vértices")


if __name__ == "__main__":
    main(sys.argv[1])
