#!/usr/bin/env python3
"""
Gera municipios.json (contornos + ponto de cálculo) dos 15 municípios do PMIF a partir do shapefile
da malha municipal do IBGE (RJ_Municipios_2025.shp, SIRGAS 2000).

Uso:  pip install pyshp
      python preparar_municipios.py caminho/RJ_Municipios_2025.shp
Só precisa rodar de novo se a lista de municípios ou a malha mudar.

O contorno é simplificado (Douglas-Peucker, ~90 m) para o painel carregar rápido.
Ponto de cálculo (onde o modelo é consultado): centro de massa do maior polígono; se cair fora do município
(forma côncava), usa o ponto interior mais afastado das bordas. Use PONTO_MANUAL para impor outro ponto.
"""
import json
import math
import sys
from pathlib import Path

import shapefile  # pyshp

NOMES = ["Barra do Piraí", "Engenheiro Paulo de Frontin", "Itaguaí", "Japeri", "Mangaratiba", "Mendes", "Miguel Pereira",
         "Nova Iguaçu", "Paracambi", "Piraí", "Queimados", "Rio Claro", "Rio de Janeiro", "Seropédica", "Vassouras"]
PONTO_MANUAL = {}          # nome -> (lat, lon)
TOLERANCIA = 0.0008        # graus (~90 m)


def _dist_seg(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - x1 - t * dx, y - y1 - t * dy)


def simplificar(pts, tol):
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


def area_assinada(anel):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(anel, anel[1:] + anel[:1])) / 2


def centro(anel):
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(anel, anel[1:] + anel[:1]):
        f = x0 * y1 - x1 * y0
        a += f
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    a /= 2
    return (cx / (6 * a), cy / (6 * a))


def dentro(pt, anel):
    x, y = pt
    r = False
    for (x0, y0), (x1, y1) in zip(anel, anel[1:] + anel[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            r = not r
    return r


def ponto_interior(anel, passos=60):
    xs, ys = [p[0] for p in anel], [p[1] for p in anel]
    melhor, bd = None, -1
    for i in range(passos + 1):
        for j in range(passos + 1):
            pt = (min(xs) + (max(xs) - min(xs)) * i / passos, min(ys) + (max(ys) - min(ys)) * j / passos)
            if dentro(pt, anel):
                d = min(_dist_seg(pt, a, b) for a, b in zip(anel, anel[1:] + anel[:1]))
                if d > bd:
                    melhor, bd = pt, d
    return melhor


def aneis_do_shape(sh):
    """Separa os anéis do shape em polígonos (anel externo + buracos). Shapefile: externo = sentido horário."""
    partes = list(sh.parts) + [len(sh.points)]
    aneis = [[tuple(p) for p in sh.points[partes[i]:partes[i + 1]]] for i in range(len(partes) - 1)]
    externos = [a for a in aneis if area_assinada(a) < 0]
    buracos = [a for a in aneis if area_assinada(a) >= 0]
    polis = [[e] for e in externos]
    for b in buracos:
        for p in polis:
            if dentro(b[0], p[0]):
                p.append(b)
                break
    return polis


def area_km2(anel):
    lat = sum(p[1] for p in anel) / len(anel)
    return abs(area_assinada(anel)) * (111.32 ** 2) * math.cos(math.radians(lat))


def main(caminho):
    r = shapefile.Reader(caminho, encoding="utf-8")
    campos = [f[0] for f in r.fields[1:]]
    por_nome = {}
    for sr in r.shapeRecords():
        reg = dict(zip(campos, sr.record))
        por_nome[reg["NM_MUN"]] = (reg, sr.shape)
    faltando = [n for n in NOMES if n not in por_nome]
    if faltando:
        raise SystemExit(f"não encontrados no arquivo: {faltando}")
    saida = []
    for n in NOMES:
        reg, sh = por_nome[n]
        polis = aneis_do_shape(sh)
        maior = max(polis, key=lambda p: abs(area_assinada(p[0])))
        c = centro(maior[0])
        origem = "centro de massa"
        if not dentro(c, maior[0]):
            c, origem = ponto_interior(maior[0]), "ponto interior"
        lon, lat = c
        if n in PONTO_MANUAL:
            lat, lon = PONTO_MANUAL[n]
            origem = "manual"
        polis = [p for p in polis if p is maior or abs(area_assinada(p[0])) * 111.32 ** 2 * 0.92 > 0.3]  # descarta ilhotas < 0,3 km2
        arred = lambda an: [[round(x, 4), round(y, 4)] for x, y in an]
        saida.append({"codigo_ibge": reg["CD_MUN"], "nome": n, "latitude": round(lat, 4), "longitude": round(lon, 4),
                      "poligonos": [[arred(simplificar(an, TOLERANCIA)) for an in p] for p in polis]})
        a_calc = sum(area_km2(p[0]) - sum(area_km2(h) for h in p[1:]) for p in aneis_do_shape(sh))
        print(f"{reg['CD_MUN']} {n:28s} ponto ({lat:.4f}, {lon:.4f}) [{origem}]  área IBGE {reg['AREA_KM2']:.0f} km2, "
              f"calculada {a_calc:.0f} km2, {len(polis)} polígonos, {sum(len(an) for p in saida[-1]['poligonos'] for an in p)} vértices")
    Path(__file__).with_name("municipios.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
