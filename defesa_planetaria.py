# =====================================================================
#  DEFESA PLANETÁRIA - sistema solar, impacto de asteroides e métodos de defesa
#  Como rodar: python defesa_planetaria.py       
# =====================================================================

# ---------- 1) IMPORTAÇÕES ----------
import math                      # funções matemáticas (seno, cosseno, raiz...)
import random                    # sorteios (direção do meteoro, 50% impacto, sucesso da defesa)
import sys                       # para ler o que foi digitado ao rodar (ex.: "menu")
from datetime import datetime, timezone   # para pegar a data de hoje

# tkinter = biblioteca de janelas que já vem junto com o Python (rápida e sem instalação)
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:              # se o Python não tiver tkinter, só o modo texto funciona
    tk = ttk = None

# ---------- 2) CONSTANTES ----------
D = math.pi / 180        # converte graus em radianos
UA_EM_DL = 389.17        # 1 UA (distância Terra-Sol) = 389,17 distâncias Terra-Lua
UA_KM = 149597870.7      # 1 UA em quilômetros
MT_J = 4.184e15          # 1 megaton de TNT em joules
HIROSHIMA_KT = 15        # bomba de Hiroshima ≈ 15 quilotons
RAIO_TERRA_M = 6371e3    # raio da Terra em metros
DIST_INICIAL_UA = 10.0   # o meteoro começa a 10 UA da Terra (quanto mais rápido, menos tempo de aviso)

# ---------- 3) DADOS DOS PLANETAS ----------
# nome, cor, elementos [a, e, I, L, long.periélio, Ω], variação por século
# a = semi-eixo maior (UA), e = excentricidade, I = inclinação (graus)
# L = longitude média, Ω = nó ascendente (fonte: JPL/NASA, Standish)
PLANETAS = [
    ("Mercúrio", "#b8b0a8", [.38709927, .20563593, 7.00497902, 252.2503235, 77.45779628, 48.33076593],
                            [.00000037, .00001906, -.00594749, 149472.67411175, .16047689, -.12534081]),
    ("Vênus",    "#e8c98a", [.72333566, .00677672, 3.39467605, 181.9790995, 131.60246718, 76.67984255],
                            [.0000039, -.00004107, -.0007889, 58517.81538729, .00268329, -.27769418]),
    ("Terra",    "#4da6ff", [1.00000261, .01671123, -.00001531, 100.46457166, 102.93768193, 0],
                            [.00000562, -.00004392, -.01294668, 35999.37244981, .32327364, 0]),
    ("Marte",    "#ff7a50", [1.52371034, .0933941, 1.84969142, -4.55343205, -23.94362959, 49.55953891],
                            [.00001847, .00007882, -.00813131, 19140.30268499, .44441088, -.29257343]),
    ("Júpiter",  "#e0b080", [5.202887, .04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909],
                            [-.00011607, -.00013253, -.00183714, 3034.74612775, .21252668, .20469106]),
    ("Saturno",  "#e8d8a0", [9.53667594, .05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448],
                            [-.0012506, -.00050991, .00193609, 1222.49362201, -.41897216, -.28867794]),
    ("Urano",    "#8ee8e8", [19.18916464, .04725744, .77263783, 313.23810451, 170.9542763, 74.01692503],
                            [-.00196176, -.00004397, -.00242939, 428.48202785, .40805281, .04240589]),
    ("Netuno",   "#6080ff", [30.06992276, .00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574],
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
# velocidade típica de impacto de cada asteroide (km/s) - estimativas
VELOCIDADES = {"Apophis": 12.6, "Bennu": 12.7, "Ryugu": 13, "Didymos": 14, "Eros": 15,
               "Itokawa": 12, "Ícaro": 30, "Toutatis": 24, "Faetonte": 32,
               "2024 YR4": 17, "Geographos": 25, "3I/ATLAS": 58}

# ---------- 5) CLASSIFICAÇÃO DE RISCO ----------
# (limite em log10 de megatons, nome, descrição, cor). Quanto maior a energia, maior o risco.
RISCOS = [
    (-3, "Queima no céu",          "Queima na atmosfera, nada chega ao chão", "#3ccf7a"),
    (-1, "Bola de fogo",           "Explode no ar, dano mínimo",              "#8fc43a"),
    (1,  "Dano local",             "Quebra vidros e derruba árvores",         "#d9a400"),
    (3,  "Destruição regional",    "Destrói uma cidade ou região",            "#ff9a3c"),
    (5,  "Catástrofe continental", "Tsunamis e danos em vários países",       "#ff5a3c"),
    (99, "Catástrofe global",      "Extinção em massa no planeta",            "#ff3355"),
]


def classificar_risco(energia_mt):
    """Recebe a energia em megatons e devolve (nome, descrição, cor, nível 0-5) do risco."""
    lg = math.log10(energia_mt)                           # escala logarítmica
    for nivel, (limite, nome, desc, cor) in enumerate(RISCOS):   # percorre as faixas na ordem
        if lg < limite:
            return nome, desc, cor, nivel
    return RISCOS[-1][1], RISCOS[-1][2], RISCOS[-1][3], 5


# ---------- 6) CÁLCULO DO IMPACTO (parte principal do trabalho) ----------
def calcular_impacto(diametro_m, velocidade_kms, densidade=3000):
    """Calcula massa, energia e risco de um asteroide.
    diametro_m: diâmetro em metros | velocidade_kms: km/s | densidade: kg/m³
    Rochoso = 3000, metálico = 7800, gelado = 1000."""
    raio = diametro_m / 2
    volume = 4 / 3 * math.pi * raio ** 3            
    massa = densidade * volume                    
    v = velocidade_kms * 1000                        
    energia_j = 0.5 * massa * v ** 2           
    energia_mt = energia_j / MT_J                
    nome, desc, cor, nivel = classificar_risco(energia_mt)  
    return {
        "massa_kg": massa, "energia_j": energia_j, "energia_mt": energia_mt,
        "energia_kt": energia_mt * 1000,
        "hiroshimas": energia_mt * 1000 / HIROSHIMA_KT,
        "risco": nome, "descricao": desc, "cor": cor, "nivel": nivel,
    }


def mostrar_impacto(nome, diametro, velocidade, densidade=3000):
    """Imprime o resultado do cálculo de forma organizada (versão texto)."""
    r = calcular_impacto(diametro, velocidade, densidade)
    print(f"\n=== {nome} ===")
    print(f"Diâmetro:     {diametro:,.2f} m")
    print(f"Velocidade:   {velocidade:,.2f} km/s")
    print(f"Massa:        {r['massa_kg']:.3e} kg")
    print(f"Energia:      {r['energia_j']:.3e} J  ({r['energia_kt']:.3e} kt de TNT)")
    print(f"Equivale a:   {r['hiroshimas']:.3e} bombas de Hiroshima")
    print(f"RISCO:        {r['risco'].upper()}  ->  {r['descricao']}")


# ---------- 7) MÉTODOS DE DEFESA PLANETÁRIA ----------
# A ideia: empurrar o asteroide um pouquinho (delta-v) com bastante antecedência.
# Se o desvio acumulado até a chegada passar de ~1,5 raio da Terra, ele erra o planeta.
# Cada método tem sorte envolvida, então nem sempre funciona!
EVACUAR = "Evacuação da região"
METODOS = ["Impactor cinético (5 t a 10 km/s)", "Explosão nuclear (1 megaton)",
           "Trator gravitacional (20 t)", "Laser de ablação (100 N)", EVACUAR]


def sorteio(a, b):
    """Número aleatório entre a e b (representa as incertezas da missão)."""
    return random.uniform(a, b)


def tentar_defesa(metodo, massa_kg, diametro_m, restante_s):
    """Simula UMA tentativa de defesa. restante_s = tempo (em segundos) até o impacto.
    Quanto MAIOR a massa, MENOR o delta-v obtido. Quanto MAIS tempo, MAIOR o desvio."""
    if metodo.startswith("Impactor"):
        # delta-v = β · massa_nave · velocidade_nave / massa_asteroide (β = ganho da ejeção de rocha)
        dv = sorteio(1, 4) * 5000 * 10000 / massa_kg
    elif metodo.startswith("Explosão"):
        # energia que vira empurrão: 2 · fração · energia / velocidade de ejeção (3 km/s)
        dv = 2 * sorteio(.003, .02) * MT_J / 3000 / massa_kg
    elif metodo.startswith("Trator"):
        # atração gravitacional da nave a 1 diâmetro de distância, durante todo o tempo
        dv = sorteio(.5, 1) * 6.674e-11 * 20000 / diametro_m ** 2 * restante_s
    else:
        # laser: força constante de 100 N empurrando durante todo o tempo
        dv = sorteio(.5, 1.2) * 100 * restante_s / massa_kg
    dv *= random.lognormvariate(0, 0.8)                    
    desvio_m = dv * restante_s                                
    necessario_m = 1.5 * RAIO_TERRA_M * sorteio(.8, 1.2)       
    return {"dv": dv, "desvio_m": desvio_m, "necessario_m": necessario_m,
            "sucesso": desvio_m >= necessario_m}


def chance_defesa(metodo, massa_kg, diametro_m, restante_s, tentativas=400):
    """Chance (%) de sucesso: repete a tentativa várias vezes e conta quantas deram certo."""
    acertos = 0
    for _ in range(tentativas):                           
        if tentar_defesa(metodo, massa_kg, diametro_m, restante_s)["sucesso"]:
            acertos += 1
    return acertos / tentativas * 100


# ---------- 8) MATEMÁTICA DAS ÓRBITAS ----------
def jd_atual():
    """Data de hoje em Dia Juliano (contagem contínua de dias usada na astronomia)."""
    agora = datetime.now(timezone.utc)
    return agora.timestamp() / 86400 + 2440587.5


def jd_para_texto(jd):
    """Converte dia juliano em data legível (dd/mm/aaaa)."""
    return datetime.fromtimestamp((jd - 2440587.5) * 86400, timezone.utc).strftime("%d/%m/%Y")


def resolver_kepler(M_graus, e):
    """Resolve a equação de Kepler (M = E - e·sen E) pelo método de Newton."""
    M = (M_graus % 360) * D
    E = M if e < .8 else math.pi                 
    for _ in range(12):                           
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


def posicao_planeta(p, jd):
    """Posição de um planeta na data jd (dia juliano)."""
    T = (jd - 2451545) / 36525                       # séculos desde o ano 2000
    a, e, I, L, wb, O = [v + t * T for v, t in zip(p[2], p[3])]
    return posicao_eliptica(a, e, I, O, wb - O, L - wb)


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


def pontos_orbita_planeta(p, n=100):
    """Lista de pontos para desenhar a órbita de um planeta."""
    a, e, I, L, wb, O = p[2]
    return [posicao_eliptica(a, e, I, O, wb - O, k / n * 360) for k in range(n + 1)]


def pontos_orbita_asteroide(ast, n=100):
    """Lista de pontos para desenhar a órbita de um asteroide (o 3I/ATLAS não tem linha)."""
    if ast[10]:
        return []
    return [posicao_eliptica(ast[2], ast[3], ast[4], ast[5], ast[6], k / n * 360)
            for k in range(n + 1)]


def cor_asteroide(ast):
    """Cor por categoria: vermelho = perigoso, laranja = comum, roxo = interestelar."""
    return {2: "#c77dff", 1: "#ff4d5e"}.get(ast[8], "#ffb84d")


# ---------- 9) TRAJETÓRIA DO METEORO (50% bate, 50% passa perto) ----------
def criar_trajetoria(velocidade, j0):
    """Cria a rota de um meteoro que vem de longe (10 UA), em linha reta, rumo à Terra."""
    va = velocidade * 86400 / UA_KM                  # velocidade em UA por dia
    T = DIST_INICIAL_UA / va                         # dias de viagem (rápido = pouco tempo de aviso)

    # direção aleatória de viagem (vetor unitário)
    th, ph = random.random() * 6.283, (random.random() - .5) * .5
    d = [-math.cos(th) * math.cos(ph), -math.sin(th) * math.cos(ph), -math.sin(ph)]

    # vetores perpendiculares à direção (para desviar a rota)
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

    tr = {"va": va, "T": T, "j0": j0, "vai_bater": vai_bater, "dist_min": 0, "desv": None,
          "defendeu": False}

    def pos(t):                                      # posição do meteoro no dia t (após j0)
        k = va * (t - T)
        p = [alvo[i] + d[i] * k for i in range(3)]
        if tr["desv"]:                               # se a defesa funcionou, a rota vai entortando
            tf, dv = tr["desv"]
            frac = max(0, (t - tf) / (T - tf)) if T > tf else 1
            p = [p[i] + dv[i] * frac for i in range(3)]
        return p

    def minimo(t_ini):
        """Menor distância até a Terra daqui para frente (varre o tempo em passos)."""
        passo = max(.25, T / 1200)
        menor, t = 9e9, t_ini
        while t <= T * 1.12:                   
            menor = min(menor, math.dist(pos(t), posicao_planeta(PLANETAS[INDICE_TERRA], j0 + t)))
            t += passo
        return menor

    def desviar(t_disparo, desvio_ua):
        """Aplica o empurrão da defesa: a rota entorta até errar a Terra."""
        a2 = random.random() * 6.283
        dv = [desvio_ua * (math.cos(a2) * p1[i] + math.sin(a2) * p2[i]) for i in range(3)]
        tr["desv"] = (t_disparo, dv)
        tr["vai_bater"] = False
        tr["dist_min"] = minimo(t_disparo)

    tr["pos"], tr["desviar"] = pos, desviar
    if not vai_bater:
        tr["dist_min"] = minimo(0)
    return tr


# ---------- 10) PAINEL COMPLETO (janela única, rápida) ----------
if tk:
    class Painel:
        """Janela com sistema solar 3D (foco na Terra), lista de asteroides,
        calculadora de impacto, lançamento de meteoro e métodos de defesa."""

        FUNDO, LADO, TXT, CIANO = "#04060d", "#0b1120", "#d6e2ff", "#4de1ff"

        def __init__(self, raiz, lancar_inicial=None):
            self.raiz = raiz
            self.orb_p = [pontos_orbita_planeta(p) for p in PLANETAS]     # órbitas (calculadas 1 vez)
            self.orb_a = [pontos_orbita_asteroide(a) for a in ASTEROIDES]
            # estado do programa: tudo que muda durante a execução
            self.jd, self.play, self.raio, self.dpq = jd_atual(), True, 2.5, 2.0
            self.yaw, self.pitch, self.mouse = -0.6, 1.0, (0, 0)
            self.traj, self.fim, self.nome, self.dados = None, False, ASTEROIDES[0][0], None
            self.msg_def, self.cor_def, self.fr_fim, self.larg, self.alt = "", "#ffb870", 0, 900, 700
            self.dpq_met = 1.0
            self.estrelas = [(random.random(), random.random()) for _ in range(90)]
            self.montar_interface()
            self.escolher()                                               # preenche o 1º asteroide
            if lancar_inicial:                                            # usado pelo menu de texto
                nome, dia, vel = lancar_inicial
                self.nome = nome
                self.v_d.set(str(dia)); self.v_v.set(str(vel))
                self.lancar()
            self.quadro()                                                 # começa a animação

        # ----- monta os botões, caixas e a tela -----
        def montar_interface(self):
            r = self.raiz
            r.title("Defesa Planetária"); r.geometry("1240x760"); r.configure(bg=self.FUNDO)
            self.tela = tk.Canvas(r, bg=self.FUNDO, highlightthickness=0)
            self.tela.pack(side="left", fill="both", expand=True)
            lado = tk.Frame(r, bg=self.LADO, width=330)
            lado.pack(side="right", fill="y"); lado.pack_propagate(False)

            def rotulo(texto, **kw):                 # cria um texto no painel lateral
                l = tk.Label(lado, text=texto, bg=self.LADO, fg=kw.pop("fg", self.TXT),
                             anchor="w", justify="left", wraplength=300, **kw)
                l.pack(fill="x", padx=10, pady=(4, 0))
                return l

            rotulo("ASTEROIDES MONITORADOS", fg=self.CIANO, font=("Arial", 9, "bold"))
            self.lista = tk.Listbox(lado, height=13, bg=self.FUNDO, fg=self.TXT, borderwidth=0,
                                    selectbackground="#1c3a66", exportselection=False,
                                    highlightthickness=0, font=("Arial", 9))
            for a in ASTEROIDES:
                self.lista.insert(tk.END, f"{a[0]}  (~{a[9]:,} m)")
            self.lista.insert(tk.END, "Personalizado")
            self.lista.selection_set(0)
            self.lista.pack(fill="x", padx=10, pady=4)
            self.lista.bind("<<ListboxSelect>>", self.escolher)

            # caixas de digitar: diâmetro e velocidade (recalculam na hora)
            self.v_d, self.v_v = tk.StringVar(), tk.StringVar()
            for texto, var in (("Diâmetro (m)", self.v_d), ("Velocidade (km/s)", self.v_v)):
                rotulo(texto)
                tk.Entry(lado, textvariable=var, bg=self.FUNDO, fg="white", relief="flat",
                         insertbackground="white").pack(fill="x", padx=10)
                var.trace_add("write", lambda *a: self.atualizar_info())

            self.l_info = rotulo("", font=("Arial", 9))
            self.l_risco = rotulo("", font=("Arial", 14, "bold"))

            rotulo("MÉTODO DE DEFESA", fg=self.CIANO, font=("Arial", 9, "bold"))
            self.v_met = tk.StringVar(value=METODOS[0])
            cb = ttk.Combobox(lado, textvariable=self.v_met, values=METODOS, state="readonly")
            cb.pack(fill="x", padx=10, pady=4)
            cb.bind("<<ComboboxSelected>>", lambda e: self.atualizar_info())
            self.l_def = rotulo("", font=("Arial", 9))

            def botao(texto, cmd, cor):
                tk.Button(lado, text=texto, command=cmd, bg=cor, fg="white", relief="flat",
                          activebackground="#1c3a66", activeforeground="white", cursor="hand2"
                          ).pack(fill="x", padx=10, pady=3)
            botao("☄  Lançar contra a Terra", self.lancar, "#5a1626")
            botao("🛡  Disparar defesa", self.disparar, "#12406b")
            botao("Pausar / Continuar", self.pausar, "#1c2a44")

            # sliders: zoom e velocidade do tempo
            kw = dict(orient="horizontal", bg=self.LADO, fg=self.TXT, highlightthickness=0,
                      troughcolor=self.FUNDO, resolution=0.1)
            self.esc_z = tk.Scale(lado, from_=0.3, to=35, label="Zoom (UA)", command=self.mudar_zoom, **kw)
            self.esc_z.set(2.5); self.esc_z.pack(fill="x", padx=10)
            self.esc_t = tk.Scale(lado, from_=0.1, to=20, label="Tempo (dias/quadro)",
                                  command=lambda v: setattr(self, "dpq", float(v)), **kw)
            self.esc_t.set(2.0); self.esc_t.pack(fill="x", padx=10)

            # mouse: arrastar gira, roda dá zoom
            t = self.tela
            t.bind("<ButtonPress-1>", lambda e: setattr(self, "mouse", (e.x, e.y)))
            t.bind("<B1-Motion>", self.arrastar)
            t.bind("<MouseWheel>", lambda e: self.zoom_fator(.9 if e.delta > 0 else 1.1))
            t.bind("<Button-4>", lambda e: self.zoom_fator(.9))
            t.bind("<Button-5>", lambda e: self.zoom_fator(1.1))
            t.bind("<Configure>", lambda e: (setattr(self, "larg", e.width), setattr(self, "alt", e.height)))

        # ----- controles -----
        def mudar_zoom(self, v):
            if not self.traj:                        # durante o voo o zoom é automático
                self.raio = float(v)

        def zoom_fator(self, f):
            self.raio = max(.3, min(35, self.raio * f))
            self.esc_z.set(self.raio)

        def arrastar(self, e):
            self.yaw += (e.x - self.mouse[0]) * .01
            self.pitch = max(0, min(1.9, self.pitch + (e.y - self.mouse[1]) * .01))
            self.mouse = (e.x, e.y)

        def valores(self):
            """Lê as caixas. Devolve (diâmetro, velocidade) ou None se digitou algo inválido."""
            try:
                d = float(self.v_d.get().replace(",", "."))
                v = float(self.v_v.get().replace(",", "."))
            except ValueError:                     
                return None
            if d > 0 and v > 0:
                return d, v
            return None

        def escolher(self, _=None):
            """Clicou num asteroide da lista: preenche diâmetro e velocidade."""
            sel = self.lista.curselection()
            k = sel[0] if sel else 0
            if k < len(ASTEROIDES):
                a = ASTEROIDES[k]
                self.nome = a[0]
                self.v_d.set(str(a[9])); self.v_v.set(str(VELOCIDADES[a[0]]))
            else:
                self.nome = "Personalizado"
            self.atualizar_info()

        def atualizar_info(self):
            """Recalcula massa, energia, risco e chance de sucesso da defesa."""
            vals = self.valores()
            if vals is None:
                self.l_info.config(text="Digite números válidos."); self.l_risco.config(text="")
                self.l_def.config(text="")
                return
            dia, vel = vals
            r = calcular_impacto(dia, vel)
            self.l_info.config(text=f"Massa: {r['massa_kg']:.3e} kg\nEnergia: {r['energia_j']:.3e} J\n"
                                    f"= {r['energia_kt']:.3e} kt de TNT\n"
                                    f"= {r['hiroshimas']:.2e} bombas de Hiroshima\n{r['descricao']}")
            self.l_risco.config(text=r["risco"].upper(), fg=r["cor"])
            tempo_s = DIST_INICIAL_UA / (vel * 86400 / UA_KM) * 86400   # tempo de aviso previsto
            metodo = self.v_met.get()
            if metodo == EVACUAR:
                chance = 100 if r["nivel"] <= 3 else 0                  
            else:
                chance = chance_defesa(metodo, r["massa_kg"], dia, tempo_s, 150)
            self.l_def.config(text=f"Aviso: {tempo_s / 86400 / 365.25:.1f} anos antes do impacto\n"
                                   f"Chance de sucesso: {chance:.0f}%")

        def lancar(self):
            """Lança o meteoro: vem de longe, 50% de chance de bater."""
            vals = self.valores()
            if vals is None:
                return
            self.traj = criar_trajetoria(vals[1], self.jd)
            self.dados = (self.nome, vals[0], vals[1])
            self.fim, self.play, self.raio, self.fr_fim = False, True, 12, 0
            self.msg_def, self.cor_def = "", "#ffb870"
            self.dpq_met = self.traj["T"] * 1.12 / 240                  

        def pausar(self):
            """Pausa / continua. Se o meteoro já terminou, limpa e volta ao normal."""
            if self.fim:
                self.traj, self.fim, self.play, self.msg_def = None, False, True, ""
                self.raio = float(self.esc_z.get())
            else:
                self.play = not self.play

        def disparar(self):
            """Dispara o método de defesa escolhido, usando o tempo que ainda resta."""
            tj = self.traj
            if not tj or self.fim:
                self.msg_def, self.cor_def = "Lance um meteoro primeiro.", "#ffb870"
                return
            if tj["defendeu"]:
                return                                                  # só uma tentativa por meteoro
            t = self.jd - tj["j0"]
            restante_s = max(1, (tj["T"] - t) * 86400)                  # tempo até o impacto (s)
            nome, dia, vel = self.dados
            r = calcular_impacto(dia, vel)
            metodo = self.v_met.get()
            tj["defendeu"] = True
            if not tj["vai_bater"]:                                     # já ia errar a Terra
                self.msg_def, self.cor_def = (f"Defesa desnecessária: ele já passa a "
                                              f"{tj['dist_min'] * UA_EM_DL:.1f} DL da Terra."), "#3ccf7a"
            elif metodo == EVACUAR:
                if r["nivel"] <= 3:
                    self.msg_def, self.cor_def = "Região evacuada: o impacto ocorre, mas as vidas foram salvas.", "#ffb870"
                else:
                    self.msg_def, self.cor_def = "Evacuação NÃO basta: o dano é grande demais.", "#ff3355"
            else:
                res = tentar_defesa(metodo, r["massa_kg"], dia, restante_s)
                km = res["desvio_m"] / 1000
                if res["sucesso"]:                                      # DEU CERTO: rota entorta
                    tj["desviar"](t, res["desvio_m"] / (UA_KM * 1000))
                    self.msg_def, self.cor_def = f"DEFESA FUNCIONOU! Desvio de {km:,.0f} km. A Terra está salva.", "#3ccf7a"
                else:                                                   # FALHOU
                    self.msg_def, self.cor_def = (f"DEFESA FALHOU: desvio de {km:,.0f} km, "
                                                  f"precisava de {res['necessario_m'] / 1000:,.0f} km."), "#ff3355"

        # ----- desenho -----
        def projetar(self, p, centro):
            """Converte posição 3D (UA) em ponto (x, y) da tela, com a Terra no centro."""
            x, y, z = p[0] - centro[0], p[1] - centro[1], p[2] - centro[2]
            cy, sy, cp, sp = math.cos(self.yaw), math.sin(self.yaw), math.cos(self.pitch), math.sin(self.pitch)
            x1, y1 = x * cy - y * sy, x * sy + y * cy
            esc = min(self.larg, self.alt) / 2 / self.raio
            return self.larg / 2 + x1 * esc, self.alt / 2 + (y1 * cp - z * sp) * esc

        def ponto(self, p, centro, raio_px, cor, texto="", cor_txt=None, fonte=("Arial", 8)):
            """Desenha uma bolinha com nome (só se estiver dentro da tela)."""
            x, y = self.projetar(p, centro)
            if -10 <= x <= self.larg + 10 and -10 <= y <= self.alt + 10:
                self.tela.create_oval(x - raio_px, y - raio_px, x + raio_px, y + raio_px, fill=cor, outline="")
                if texto:
                    self.tela.create_text(x + raio_px + 4, y - 6, text=texto, anchor="w",
                                          fill=cor_txt or cor, font=fonte)
            return x, y

        def linha(self, pontos, centro, cor, largura=1):
            """Desenha uma linha passando por vários pontos 3D."""
            coords = []
            for p in pontos:
                coords.extend(self.projetar(p, centro))
            self.tela.create_line(*coords, fill=cor, width=largura)

        def quadro(self):
            """Roda a cada ~30 ms: avança o tempo e redesenha tudo."""
            tj = self.traj
            if self.play:                        
                self.jd += self.dpq_met if tj else self.dpq
            c, W, H = self.tela, self.larg, self.alt
            c.delete("all")
            for ex, ey in self.estrelas:             
                c.create_rectangle(ex * W, ey * H, ex * W + 1, ey * H + 1, fill="#6b7aa8", outline="")
            terra = posicao_planeta(PLANETAS[INDICE_TERRA], self.jd)

            for orb in self.orb_p:                   
                self.linha(orb, terra, "#243556")
            for a, orb in zip(ASTEROIDES, self.orb_a):   
                if orb:
                    forte = a[0] == self.nome
                    self.linha(orb, terra, cor_asteroide(a) if forte else "#4a2a35", 2 if forte else 1)
            self.ponto([0, 0, 0], terra, 7, "#ffd95a", "Sol", "#ffd95a")       
            for p in PLANETAS:                    
                self.ponto(posicao_planeta(p, self.jd), terra, 5 if p[0] == "Terra" else 3, p[1], p[0], "#9fb3da")
            for a in ASTEROIDES:                    
                forte = a[0] == self.nome
                x, y = self.ponto(posicao_asteroide(a, self.jd), terra, 4 if forte else 2, cor_asteroide(a),
                                  a[0], None, ("Arial", 9, "bold") if forte else ("Arial", 7))
                if forte:
                    c.create_oval(x - 9, y - 9, x + 9, y + 9, outline=self.CIANO)

            if tj:
                self.desenhar_meteoro(tj, terra)
            else:
                self.cartao(["Escolha um asteroide, ajuste os valores", "e clique em 'Lançar contra a Terra'."], "#4de1ff")
            c.create_text(10, H - 10, anchor="sw", fill="#8ea0c8", font=("Arial", 8),
                          text=f"Data simulada: {jd_para_texto(self.jd)}   |   foco na Terra   |   arraste para girar")
            self.raiz.after(30, self.quadro)       

        def cartao(self, linhas, cor):
            """Cartão de texto no canto superior esquerdo da tela."""
            h = len(linhas) * 17 + 12
            self.tela.create_rectangle(10, 10, 300, 10 + h, fill="#0b1120", outline=cor, width=2)
            for i, tx in enumerate(linhas):
                self.tela.create_text(18, 20 + i * 17, text=tx, anchor="w", fill="white", font=("Arial", 9))

        def desenhar_meteoro(self, tj, terra):
            """Desenha o meteoro em voo, a rota, o cartão de informações e o resultado."""
            c, W, H = self.tela, self.larg, self.alt
            t = self.jd - tj["j0"]
            bateu = tj["vai_bater"] and t >= tj["T"]
            acabou = t >= tj["T"] * 1.12
            p = terra if bateu else tj["pos"](t)
            if not (bateu or acabou):                # zoom automático acompanhando o meteoro
                self.raio += (max(.3, math.dist(p, terra) * 1.2) - self.raio) * .08
            elif not self.fim:                       # terminou: pausa
                self.fim, self.play = True, False
            self.linha([tj["pos"](0), p], terra, "#ff9a3c", 2)                   # rota percorrida
            self.ponto(p, terra, 5, "#ff9a3c", self.dados[0], "#ffb870", ("Arial", 9, "bold"))
            nome, dia, vel = self.dados
            r = calcular_impacto(dia, vel)
            if bateu:
                status, cor = f"IMPACTO: {r['risco'].upper()}", r["cor"]
                self.fr_fim += 1
                x, y = self.projetar(terra, terra)
                raio_px = 10 + self.fr_fim * 5
                c.create_oval(x - raio_px, y - raio_px, x + raio_px, y + raio_px, outline=cor, width=3)
            elif acabou:
                status, cor = f"PASSOU A {tj['dist_min'] * UA_EM_DL:.1f} DL DA TERRA: SEM IMPACTO", "#3ccf7a"
            else:
                faltam = max(0, tj["T"] - t)
                status, cor = f"Impacto previsto em {faltam / 365.25:.2f} anos ({faltam:.0f} dias)", "#ffb870"
            passa = "impacto direto" if tj["vai_bater"] else f"{tj['dist_min'] * UA_EM_DL:.1f} DL da Terra"
            self.cartao([nome, f"Diâmetro: {dia:,.0f} m   Velocidade: {vel:.1f} km/s",
                         f"Massa: {r['massa_kg']:.2e} kg",
                         f"Energia: {r['energia_kt']:.2e} kt de TNT", f"Passa a: {passa}",
                         f"RISCO SE ATINGISSE: {r['risco'].upper()}"], cor)
            c.create_text(W / 2, H - 80, text=status, fill=cor, font=("Arial", 16, "bold"))
            if self.msg_def:                         # resultado da defesa
                c.create_text(W / 2, H - 50, text=self.msg_def, fill=self.cor_def, font=("Arial", 11, "bold"))


def abrir_painel(lancar_inicial=None):
    """Abre a janela do painel."""
    raiz = tk.Tk()
    Painel(raiz, lancar_inicial)
    raiz.mainloop()


# ---------- 12) PONTO DE ENTRADA ----------
if __name__ == "__main__":      # só roda se o arquivo for executado diretamente
    if "menu" in sys.argv or tk is None:    # modo texto (também se o Python não tiver tkinter)
        menu()
    else:                       # padrão: abre o painel completo direto
        abrir_painel()
