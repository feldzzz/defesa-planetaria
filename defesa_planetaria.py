# =====================================================================
#  DEFESA PLANETÁRIA - simulador de sistema solar e impacto de asteroides
#  Requisitos: Python 3.8+  e  matplotlib  ->  pip install matplotlib
#  Como rodar: python defesa_planetaria.py
# =====================================================================

# ---------- 1) IMPORTAÇÕES ----------
import math                      # funções matemáticas (seno, cosseno, raiz...)
import random                    # sorteios (direção do meteoro, 50% impacto)
from datetime import datetime, timezone   # para pegar a data de hoje

import matplotlib.pyplot as plt                  # gráficos
from matplotlib.animation import FuncAnimation   # animação do meteoro

# ---------- 2) CONSTANTES ----------
D = math.pi / 180        # converte graus em radianos
UA_EM_DL = 389.17        # 1 UA (distância Terra-Sol) = 389,17 distâncias Terra-Lua
UA_KM = 149597870.7      # 1 UA em quilômetros
MT_J = 4.184e15          # 1 megaton de TNT em joules
HIROSHIMA_KT = 15        # bomba de Hiroshima ≈ 15 quilotons

# ---------- 3) DADOS DOS PLANETAS ----------
# nome, cor, elementos [a, e, I, L, long.periélio, Ω], variação por século
# a = semi-eixo maior (UA), e = excentricidade, I = inclinação (graus)
# L = longitude média, Ω = nó ascendente (fonte: JPL/NASA, Standish)
PLANETAS = [
    ("Mercúrio", "gray",   [.38709927, .20563593, 7.00497902, 252.2503235, 77.45779628, 48.33076593],
                           [.00000037, .00001906, -.00594749, 149472.67411175, .16047689, -.12534081]),
    ("Vênus",    "gold",   [.72333566, .00677672, 3.39467605, 181.9790995, 131.60246718, 76.67984255],
                           [.0000039, -.00004107, -.0007889, 58517.81538729, .00268329, -.27769418]),
    ("Terra",    "dodgerblue", [1.00000261, .01671123, -.00001531, 100.46457166, 102.93768193, 0],
                           [.00000562, -.00004392, -.01294668, 35999.37244981, .32327364, 0]),
    ("Marte",    "orangered", [1.52371034, .0933941, 1.84969142, -4.55343205, -23.94362959, 49.55953891],
                           [.00001847, .00007882, -.00813131, 19140.30268499, .44441088, -.29257343]),
    ("Júpiter",  "peru",   [5.202887, .04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909],
                           [-.00011607, -.00013253, -.00183714, 3034.74612775, .21252668, .20469106]),
    ("Saturno",  "khaki",  [9.53667594, .05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448],
                           [-.0012506, -.00050991, .00193609, 1222.49362201, -.41897216, -.28867794]),
    ("Urano",    "turquoise", [19.18916464, .04725744, .77263783, 313.23810451, 170.9542763, 74.01692503],
                           [-.00196176, -.00004397, -.00242939, 428.48202785, .40805281, .04240589]),
    ("Netuno",   "royalblue", [30.06992276, .00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574],
                           [.00026291, .00005105, .00035372, 218.45945325, -.32241464, -.00508664]),
]
INDICE_TERRA = 2         # posição da Terra na lista acima

# ---------- 4) DADOS DOS ASTEROIDES ----------
# nome, designação, a, e, i, Ω, ω, M0 (época JD 2460000.5), PHA?, diâmetro (m), JD do periélio
# PHA: 1 = potencialmente perigoso, 0 = comum, 2 = interestelar (hiperbólico)
# Obs: o formato das órbitas é real (JPL), mas a posição de cada asteroide
# na órbita é aproximada. O 3I/ATLAS usa a data real do periélio.
ASTEROIDES = [
    ("Apophis",    "99942",    .9224, .1911, 3.34, 203.9, 126.7, 215, 1, 370,   None),
    ("Bennu",      "101955",   1.1264, .2037, 6.03, 2.06, 66.22, 102, 1, 490,   None),
    ("Ryugu",      "162173",   1.1896, .1903, 5.88, 251.6, 211.4, 330, 1, 900,  None),
    ("Didymos",    "65803",    1.6444, .3838, 3.41, 73.2, 319.3, 40, 1, 780,    None),
    ("Eros",       "433",      1.4582, .223, 10.83, 304.3, 178.9, 150, 0, 16800, None),
    ("Itokawa",    "25143",    1.324, .28, 1.62, 69.1, 162.8, 270, 1, 330,      None),
    ("Ícaro",      "1566",     1.078, .8269, 22.8, 88.0, 31.3, 5, 1, 1400,      None),
    ("Toutatis",   "4179",     2.5336, .6294, .45, 124.4, 278.7, 95, 1, 4600,   None),
    ("Faetonte",   "3200",     1.2714, .89, 22.3, 265.2, 322.2, 60, 1, 5100,    None),
    ("2024 YR4",   "2024 YR4", 2.5155, .6615, 3.4, 271.4, 134.4, 180, 0, 60,    None),
    ("Geographos", "1620",     1.2458, .3356, 13.3, 337.2, 276.9, 230, 1, 2500, None),
    ("3I/ATLAS",   "C/2025 N1", -.264, 6.139, 175.11, 322.16, 128.01, 0, 2, 5600, 2460977.98),
]

# ---------- 5) CLASSIFICAÇÃO DE RISCO ----------
# (limite em log10 de megatons, nome, descrição). Quanto maior a energia, maior o risco.
RISCOS = [
    (-3, "Queima no céu",         "Queima na atmosfera, nada chega ao chão"),
    (-1, "Bola de fogo",          "Explode no ar, dano mínimo"),
    (1,  "Dano local",            "Quebra vidros e derruba árvores"),
    (3,  "Destruição regional",   "Destrói uma cidade ou região"),
    (5,  "Catástrofe continental", "Tsunamis e danos em vários países"),
    (99, "Catástrofe global",     "Extinção em massa no planeta"),
]


def classificar_risco(energia_mt):
    """Recebe a energia em megatons e devolve (nome, descrição) do risco."""
    lg = math.log10(energia_mt)               # escala logarítmica
    for limite, nome, desc in RISCOS:         # percorre as faixas na ordem
        if lg < limite:
            return nome, desc
    return RISCOS[-1][1], RISCOS[-1][2]


# ---------- 6) CÁLCULO DO IMPACTO (parte principal do trabalho) ----------
def calcular_impacto(diametro_m, velocidade_kms, densidade=3000):
    """Calcula massa, energia e risco de um asteroide.
    diametro_m: diâmetro em metros | velocidade_kms: km/s | densidade: kg/m³
    Rochoso = 3000, metálico = 7800, gelado = 1000."""
    raio = diametro_m / 2
    volume = 4 / 3 * math.pi * raio ** 3            # volume da esfera
    massa = densidade * volume                       # massa = densidade x volume (kg)
    v = velocidade_kms * 1000                        # km/s -> m/s
    energia_j = 0.5 * massa * v ** 2                 # energia cinética = ½·m·v² (joules)
    energia_mt = energia_j / MT_J                    # joules -> megatons de TNT
    nome, desc = classificar_risco(energia_mt)       # classifica o risco
    return {
        "massa_kg": massa, "energia_j": energia_j, "energia_mt": energia_mt,
        "energia_kt": energia_mt * 1000,
        "hiroshimas": energia_mt * 1000 / HIROSHIMA_KT,
        "risco": nome, "descricao": desc,
    }


def mostrar_impacto(nome, diametro, velocidade, densidade=3000):
    """Imprime o resultado do cálculo de forma organizada."""
    r = calcular_impacto(diametro, velocidade, densidade)
    print(f"\n=== {nome} ===")
    print(f"Diâmetro:     {diametro:,.2f} m")
    print(f"Velocidade:   {velocidade:,.2f} km/s")
    print(f"Massa:        {r['massa_kg']:.3e} kg")
    print(f"Energia:      {r['energia_j']:.3e} J  ({r['energia_kt']:.3e} kt de TNT)")
    print(f"Equivale a:   {r['hiroshimas']:.3e} bombas de Hiroshima")
    print(f"RISCO:        {r['risco'].upper()}  ->  {r['descricao']}")


# ---------- 7) MATEMÁTICA DAS ÓRBITAS ----------
def jd_atual():
    """Data de hoje em Dia Juliano (contagem contínua de dias usada na astronomia)."""
    agora = datetime.now(timezone.utc)
    return agora.timestamp() / 86400 + 2440587.5


def resolver_kepler(M_graus, e):
    """Resolve a equação de Kepler (M = E - e·sen E) pelo método de Newton."""
    M = (M_graus % 360) * D
    E = M if e < .8 else math.pi                     # chute inicial
    for _ in range(12):                              # 12 iterações bastam
        E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    return E


def girar_orbita(r, v, i, O, w):
    """Converte (distância r, ângulo v) no plano da órbita para x, y, z no espaço 3D."""
    u = w * D + v
    cO, sO = math.cos(O * D), math.sin(O * D)
    ci, si = math.cos(i * D), math.sin(i * D)
    return [r * (cO * math.cos(u) - sO * math.sin(u) * ci),
            r * (sO * math.cos(u) + cO * math.sin(u) * ci),
            r * math.sin(u) * si]


def posicao_eliptica(a, e, i, O, w, M_graus):
    """Posição (x,y,z) em UA de um corpo em órbita elíptica."""
    E = resolver_kepler(M_graus, e)
    xv = a * (math.cos(E) - e)
    yv = a * math.sqrt(1 - e * e) * math.sin(E)
    return girar_orbita(math.hypot(xv, yv), math.atan2(yv, xv), i, O, w)


def posicao_planeta(p, jd, M_graus=None):
    """Posição de um planeta na data jd (dia juliano)."""
    T = (jd - 2451545) / 36525                       # séculos desde o ano 2000
    a, e, I, L, wb, O = [v + t * T for v, t in zip(p[2], p[3])]
    M = L - wb if M_graus is None else M_graus       # anomalia média
    return posicao_eliptica(a, e, I, O, wb - O, M)


def posicao_hiperbolica(ast, H):
    """Posição de um objeto em órbita hiperbólica (3I/ATLAS), parâmetro H."""
    a, e = -ast[2], ast[3]
    xv = a * (e - math.cosh(H))
    yv = a * math.sqrt(e * e - 1) * math.sinh(H)
    return girar_orbita(math.hypot(xv, yv), math.atan2(yv, xv), ast[4], ast[5], ast[6])


def posicao_asteroide(ast, jd):
    """Posição de um asteroide/cometa na data jd."""
    if ast[10]:                                      # tem data de periélio -> hiperbólico
        a, e = -ast[2], ast[3]
        M = .01720209895 / a ** 1.5 * (jd - ast[10])
        H = math.asinh(M / e)
        for _ in range(30):                          # Newton para a equação hiperbólica
            H -= (e * math.sinh(H) - H - M) / (e * math.cosh(H) - 1)
        return posicao_hiperbolica(ast, H)
    n = .9856076686 / ast[2] ** 1.5                  # movimento médio (graus/dia)
    M = ast[7] + n * (jd - 2460000.5)
    return posicao_eliptica(ast[2], ast[3], ast[4], ast[5], ast[6], M)


def pontos_orbita_planeta(p, n=200):
    """Lista de pontos para desenhar a órbita de um planeta."""
    a, e, I, L, wb, O = p[2]
    return [posicao_eliptica(a, e, I, O, wb - O, k / n * 360) for k in range(n + 1)]


def pontos_orbita_asteroide(ast, n=200):
    """Lista de pontos para desenhar a órbita de um asteroide/cometa."""
    if ast[10]:                                      # hipérbole: varre H de -3,9 a 3,9
        return [posicao_hiperbolica(ast, -3.9 + 7.8 * k / n) for k in range(n + 1)]
    return [posicao_eliptica(ast[2], ast[3], ast[4], ast[5], ast[6], k / n * 360)
            for k in range(n + 1)]


def cor_asteroide(ast):
    """Cor por categoria: vermelho = perigoso, laranja = comum, roxo = interestelar."""
    return {2: "mediumpurple", 1: "red"}.get(ast[8], "orange")


# ---------- 8) DESENHO DO SISTEMA SOLAR (câmera focada na Terra) ----------
def desenhar_sistema(ax, jd, raio, centro, orbitas_planetas, orbitas_asteroides):
    """Desenha Sol, planetas, órbitas e asteroides no eixo 3D.
    centro = posição que fica no meio da tela (a Terra)."""
    def rel(p):                                      # posição relativa ao centro (Terra)
        return [p[0] - centro[0], p[1] - centro[1], p[2] - centro[2]]

    # órbitas dos planetas (linhas cinza)
    for orb in orbitas_planetas:
        pts = [rel(p) for p in orb]
        ax.plot(*zip(*pts), color="#3a4a6b", lw=.7)
    # órbitas dos asteroides (o 3I/ATLAS não tem linha, como pedido)
    for ast, orb in zip(ASTEROIDES, orbitas_asteroides):
        if ast[10]:
            continue
        pts = [rel(p) for p in orb]
        ax.plot(*zip(*pts), color=cor_asteroide(ast), lw=.6, alpha=.35)
    # Sol
    sol = rel([0, 0, 0])
    ax.scatter(*sol, color="yellow", s=80)
    # planetas
    for p in PLANETAS:
        pos = rel(posicao_planeta(p, jd))
        ax.scatter(*pos, color=p[1], s=30)
        ax.text(*pos, " " + p[0], color="white", fontsize=7)
    # asteroides
    for ast in ASTEROIDES:
        pos = rel(posicao_asteroide(ast, jd))
        ax.scatter(*pos, color=cor_asteroide(ast), s=14)
        ax.text(*pos, " " + ast[0], color=cor_asteroide(ast), fontsize=6)
    # limites da câmera (zoom)
    ax.set_xlim(-raio, raio); ax.set_ylim(-raio, raio); ax.set_zlim(-raio, raio)


def preparar_figura():
    """Cria a janela 3D com fundo escuro."""
    fig = plt.figure(figsize=(10, 7), facecolor="#04060d")
    ax = fig.add_subplot(111, projection="3d", facecolor="#04060d")
    ax.set_axis_off()                                # esconde eixos
    return fig, ax


def ver_sistema_solar():
    """Mostra o sistema solar hoje, com foco na Terra."""
    jd = jd_atual()
    orb_p = [pontos_orbita_planeta(p) for p in PLANETAS]
    orb_a = [pontos_orbita_asteroide(a) for a in ASTEROIDES]
    fig, ax = preparar_figura()
    terra = posicao_planeta(PLANETAS[INDICE_TERRA], jd)
    desenhar_sistema(ax, jd, 2.5, terra, orb_p, orb_a)
    ax.set_title("Defesa Planetária - foco na Terra", color="white")
    plt.show()


# ---------- 9) SIMULAÇÃO: LANÇAR METEORO CONTRA A TERRA ----------
def lancar_meteoro(nome, diametro, velocidade, densidade=3000):
    """Meteoro vem de longe em linha reta. 50% bate na Terra, 50% passa perto."""
    info = calcular_impacto(diametro, velocidade, densidade)
    va = velocidade * 86400 / UA_KM                  # velocidade em UA por dia
    dist_inicial = 4.0                               # começa a 4 UA da Terra
    T = dist_inicial / va                            # dias até a aproximação máxima
    j0 = jd_atual()

    # direção aleatória de viagem (vetor unitário)
    th, ph = random.random() * 6.283, (random.random() - .5) * .5
    d = [-math.cos(th) * math.cos(ph), -math.sin(th) * math.cos(ph), -math.sin(ph)]

    # vetores perpendiculares à direção (para o desvio quando erra a Terra)
    n = math.hypot(d[0], d[1]) or 1
    p1 = [d[1] / n, -d[0] / n, 0]
    p2 = [d[1] * p1[2] - d[2] * p1[1], d[2] * p1[0] - d[0] * p1[2], d[0] * p1[1] - d[1] * p1[0]]

    # SORTEIO 50/50: True = vai bater; False = passa perto (3 a 9 centésimos de UA)
    vai_bater = random.random() < 0.5
    desvio = 0 if vai_bater else .03 + random.random() * .06
    ang = random.random() * 6.283

    # ponto onde o meteoro estará quando a Terra chegar lá (alvo)
    terra_T = posicao_planeta(PLANETAS[INDICE_TERRA], j0 + T)
    alvo = [terra_T[i] + desvio * (math.cos(ang) * p1[i] + math.sin(ang) * p2[i]) for i in range(3)]

    def pos_meteoro(t):                              # posição do meteoro no dia t
        k = va * (t - T)
        return [alvo[i] + d[i] * k for i in range(3)]

    # distância mínima prevista (varre o tempo e guarda a menor distância)
    dist_min = 0 if vai_bater else min(
        math.dist(pos_meteoro(t), posicao_planeta(PLANETAS[INDICE_TERRA], j0 + t))
        for t in [x * .25 for x in range(int(T * 1.12 / .25))])

    orb_p = [pontos_orbita_planeta(p, 100) for p in PLANETAS]
    orb_a = [pontos_orbita_asteroide(a, 100) for a in ASTEROIDES]
    fig, ax = preparar_figura()
    QUADROS = 150
    estado = {"raio": 5.5}

    def quadro(f):
        ax.clear(); ax.set_axis_off()
        t = min(f / (QUADROS - 1) * T * 1.12, T * 1.12)       # tempo simulado
        jd = j0 + t
        terra = posicao_planeta(PLANETAS[INDICE_TERRA], jd)
        bateu = vai_bater and t >= T                          # chegou na Terra e vai bater?
        p = terra if bateu else pos_meteoro(t)                # meteoro congela na Terra
        dist = math.dist(p, terra)
        estado["raio"] += (max(.3, dist * 1.2) - estado["raio"]) * .12   # zoom automático
        desenhar_sistema(ax, jd, estado["raio"], terra, orb_p, orb_a)
        # rota do meteoro (linha cheia = já percorrida)
        ini, atual = pos_meteoro(0), p
        r = lambda q: [q[i] - terra[i] for i in range(3)]
        ax.plot(*zip(r(ini), r(atual)), color="orange", lw=1.5)
        ax.scatter(*r(atual), color="orange", s=60)
        # cartão de informações (sempre visível, com a classificação ANTES do impacto)
        faltam = max(0, T - t)
        if bateu:
            status, cor = "IMPACTOU!", "red"
        elif t >= T * 1.12 - 1e-9:
            status, cor = f"PASSOU A {dist_min * UA_EM_DL:.1f} DL - SEM IMPACTO", "lime"
        else:
            status, cor = f"Aproximação máxima em {faltam:.0f} dias", "orange"
        passa = "impacto direto" if vai_bater else f"{dist_min * UA_EM_DL:.1f} DL da Terra"
        texto = (f"{nome}\nDiâmetro: {diametro:,.0f} m\nVelocidade: {velocidade:.1f} km/s\n"
                 f"Massa: {info['massa_kg']:.2e} kg\nEnergia: {info['energia_kt']:.2e} kt\n"
                 f"Passa a: {passa}\nRISCO SE ATINGISSE: {info['risco'].upper()}")
        fig.texts.clear()
        fig.text(.02, .95, texto, color="white", va="top", fontsize=9,
                 bbox=dict(facecolor="#0b1120", edgecolor=cor))
        fig.text(.5, .05, status, color=cor, ha="center", fontsize=15, weight="bold")

    animacao = FuncAnimation(fig, quadro, frames=QUADROS, interval=80, repeat=False)
    plt.show()
    return animacao


# ---------- 10) MENU PRINCIPAL (terminal) ----------
def escolher_asteroide():
    """Deixa o usuário escolher um asteroide da lista ou digitar os valores."""
    print("\nEscolha um asteroide:")
    for k, a in enumerate(ASTEROIDES, 1):
        print(f"  {k:2d}) {a[0]} (~{a[9]:,} m)")
    print("   0) Digitar diâmetro e velocidade")
    op = int(input("Opção: "))
    if op == 0:
        return "Meteoro personalizado", float(input("Diâmetro (m): ")), float(input("Velocidade (km/s): "))
    a = ASTEROIDES[op - 1]
    vel = 58 if a[8] == 2 else float(input("Velocidade de impacto (km/s) [ex.: 15]: ") or 15)
    return a[0], a[9], vel


def menu():
    """Loop principal do programa."""
    while True:
        print("\n===== DEFESA PLANETÁRIA =====")
        print("1) Calcular impacto de um asteroide")
        print("2) Ver o sistema solar (foco na Terra)")
        print("3) Lançar meteoro contra a Terra (simulação)")
        print("0) Sair")
        op = input("Opção: ").strip()
        if op == "1":
            nome, dia, vel = escolher_asteroide()
            mostrar_impacto(nome, dia, vel)
        elif op == "2":
            ver_sistema_solar()
        elif op == "3":
            nome, dia, vel = escolher_asteroide()
            lancar_meteoro(nome, dia, vel)
        elif op == "0":
            break


# ---------- 11) PONTO DE ENTRADA ----------
if __name__ == "__main__":      # só roda o menu se o arquivo for executado diretamente
    menu()
