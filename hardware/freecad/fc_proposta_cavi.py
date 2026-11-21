# Bozza del percorso di cavi e tubo del vuoto (gruppo "Proposta cavi (bozza)").
# Nessuna scheda sulla testa: ogni cavo esce cosi' com'e' dal suo componente.
# Geometria statica, disegnata con carrello_x = 0, carrello_y = 0, z_nozzle = 0.
# Si lancia con il modello A5ive_pick_and_place aperto (Macro -> Macro...):
# cancella e ricrea il gruppo.
import FreeCAD as App, Part
V = App.Vector
d = App.ActiveDocument
for nome in ('A5ive_0_2', 'A5ive_pick_and_place'):
    if nome in App.listDocuments():
        d = App.getDocument(nome)
        break

GNAME = 'Proposta cavi (bozza)'
for o in d.getObjectsByLabel(GNAME):
    for c in list(o.Group):
        d.removeObject(c.Name)
    d.removeObject(o.Name)
grp = d.addObject('App::DocumentObjectGroup', 'PropostaCavi')
grp.Label = GNAME

COL = {
    'tubo': (0.2, 0.75, 1.0), 'nero': (0.1, 0.1, 0.1), 'nero2': (0.35, 0.2, 0.1),
    'usb': (0.55, 0.55, 0.6), 'led': (0.95, 0.95, 0.95), 'pcb': (0.05, 0.45, 0.15),
    'lamiera': (0.75, 0.77, 0.8), 'carter': (0.55, 0.6, 0.65), 'pompa': (0.25, 0.25, 0.28),
    'valv': (0.9, 0.75, 0.1), 'clip': (0.85, 0.1, 0.1), 'lamina': (0.85, 0.85, 0.88),
}


def add(label, shape, col, transp=0):
    o = d.addObject('Part::Feature', 'PC')
    o.Label = label
    o.Shape = shape
    grp.addObject(o)
    vo = o.ViewObject
    if vo:
        vo.ShapeColor = COL[col]
        vo.Transparency = transp
        vo.LineColor = (0.2, 0.2, 0.2)
    return o


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def spline(pts, r):
    c = Part.BSplineCurve()
    c.interpolate([V(*p) for p in pts])
    e = c.toShape()
    circ = Part.Wire(Part.makeCircle(r, e.valueAt(e.FirstParameter), e.tangentAt(e.FirstParameter)))
    try:
        return Part.Wire(e).makePipeShell([circ], True, True)
    except Exception:
        print('spline fallita', pts[0], pts[-1])
        raise


def seg(a, b, r):
    a, b = V(*a), V(*b)
    return Part.makeCylinder(r, (b - a).Length, a, b - a)


def arc_h(cx, cy, z, R, r, ang0):
    """mezzo toro orizzontale (curva di un'ansa a U)"""
    t = Part.makeTorus(R, r, V(cx, cy, z), V(0, 0, 1), -180, 180, 180)
    t.rotate(V(cx, cy, z), V(0, 0, 1), ang0)
    return t


def half_ring(cx, cy, z0, h, R, t, ang0):
    s = Part.makeCylinder(R + t / 2, h, V(cx, cy, z0), V(0, 0, 1), 180).cut(
        Part.makeCylinder(R - t / 2, h, V(cx, cy, z0), V(0, 0, 1), 180))
    s.rotate(V(cx, cy, z0), V(0, 0, 1), ang0)
    return s

def ok(sh):
    sols = []
    for so in sh.Solids:
        if so.Volume < 0:
            so.reverse()
        sols.append(so)
    return Part.makeCompound(sols) if sols else sh


def cat(a, b):
    return Part.makeCompound([ok(a), ok(b)])


# ------------------------------------------------ cavi (ordine = posizione da sinistra a destra sulla testa)
CAVI = [  # etichetta, colore, raggio
    ('USB telecamera', 'usb', 2.0),
    ('Cavo anello LED (2 fili)', 'led', 1.6),
    ('Cavo motore rotazione NEMA8 (4 fili)', 'nero2', 2.2),
    ('Tubo vuoto PU 4x2,5', 'tubo', 2.0),
    ('Cavo motore Z NEMA8 (4 fili)', 'nero', 2.2),
]
N = len(CAVI)

# ---- ansa a U asse X (nel canale sopra il gantry)
off = -31.0                               # attacco medio del fascio rispetto al carrello X
xr = (-112.3 + off, 107 + off)
x_f = (xr[0] + xr[1]) / 2
Lh = (xr[1] - xr[0]) / 4
x_m = off
x_b = (x_m + x_f) / 2 + Lh
yF, yR = -10.75, 45.0
R = (yR - yF) / 2
yc = (yF + yR) / 2
zt = [136.5 + 4.5 * i for i in range(N)]
xh = [-40 + 4.5 * i for i in range(N)]    # posizione di ogni cavo dove scavalca la piastra

# ---- discesa dietro il gantry e passaggio nell'asola sinistra
xD = -141.8                                         # piano verticale della discesa (= asse dell'asola)
yd = [39.5 + 5 * i for i in range(N + 1)]            # fila lungo Y dietro la vite X (+ cavo motore X)
ys = [25.5 + 5 * i for i in range(N + 1)]            # fila lungo Y dentro l'asola
zy = [16 + 4.5 * (N - i) for i in range(N + 1)]       # pila sotto il piano (cavo 0 in alto)

# ---- ansa a U asse Y (sotto il piano), curva verso il davanti
Y0 = 6.0
yr = (Y0 - 143.5, Y0 + 87)
y_f = (yr[0] + yr[1]) / 2
LhY = (yr[1] - yr[0]) / 4
y_b = (Y0 + y_f) / 2 - LhY
xO, xI = xD, -92.0
RY = (xI - xO) / 2
xc = (xO + xI) / 2

def rpath(pts, r, rad=6.0):
    """spezzata con angoli raccordati (curva di Bezier campionata), poi tubo"""
    P = [V(*p) for p in pts]
    out = [P[0]]
    for k in range(1, len(P) - 1):
        a, p, b = P[k - 1], P[k], P[k + 1]
        u1 = (p - a); l1 = u1.Length; u1.normalize()
        u2 = (b - p); l2 = u2.Length; u2.normalize()
        dd = min(rad, l1 * 0.5, l2 * 0.5)
        q0 = p - u1 * dd
        q2 = p + u2 * dd
        for t in [j / 6.0 for j in range(7)]:
            out.append(q0 * (1 - t) ** 2 + p * (2 * t * (1 - t)) + q2 * (t * t))
    out.append(P[-1])
    clean = [out[0]]
    for q in out[1:]:
        if (q - clean[-1]).Length > 0.3:
            clean.append(q)
    c = Part.BSplineCurve()
    c.interpolate(clean)
    e = c.toShape()
    circ = Part.Wire(Part.makeCircle(r, e.valueAt(e.FirstParameter), e.tangentAt(e.FirstParameter)))
    try:
        return Part.Wire(e).makePipeShell([circ], True, True)
    except Exception:
        print('rpath: ripiego a segmenti', pts[0], pts[-1])
        sh = [Part.makeSphere(r, q) for q in clean]
        sh += [Part.makeCylinder(r, (b - a).Length, a, b - a) for a, b in zip(clean[:-1], clean[1:])]
        return sh[0].fuse(sh[1:]).removeSplitter()


def DISCESA(i):
    return [(xD, yd[i], 92), (xD, ys[i], 66), (xD, ys[i], zy[i] + 9), (xD, ys[i] - 9, zy[i]), (xO, Y0, zy[i])]


# percorsi sulla testa, fino al punto in cui scavalcano la piastra
TESTA = [
    [(-40, -46, 121.5), (-44.5, -42, 123), (-44, -33, 130), (-42, -31, 143), (-40, -30, 153)],
    [(-43, -46, 96), (-47, -43, 101), (-48, -34, 112), (-48, -27, 128), (-41, -26.5, 147), (-36.5, -27, 154)],
    # motore rotazione: sale dal motore, ansa a "n" sopra il KSH04, fermacavo, poi alla piastra
    [(0, -54, 149), (0, -54, 177), (0, -54, 186), (-3.8, -54, 195.2), (-13, -54, 199), (-22.2, -54, 195.2), (-26, -54, 186),
     (-26, -54, 168), (-30, -52, 162), (-32, -44, 160), (-31.5, -34, 158)],
    # tubo: dal KSH04, ansa a "n", fermacavo, poi alla piastra
    [(0, -46, 177), (0, -46, 186), (-3.8, -46, 195.2), (-13, -46, 199), (-22.2, -46, 195.2), (-26, -46, 186), (-26, -46, 168),
     (-26.3, -40, 161), (-26.5, -32, 158.5)],
    [(7, -31, 176), (0, -31, 170), (-12, -30, 164), (-20, -29.5, 160)],
]

for i, (lab, col, r) in enumerate(CAVI):
    x0, z = xh[i], zt[i]
    head = TESTA[i] + [(x0, -28, 158), (x0, -26.5, 163.5), (x0, -21.5, 166.5), (x0, -15, 165), (x0, -11.5, max(160, z + 9.5)),
                       (x0, yF, z + 8)]
    s = spline(head, r)
    s = cat(s, rpath([(x0, yF, z + 8), (x0, yF, z), (x0 + 10, yF, z)], r, 4))
    s = cat(s, seg((x0 + 10, yF, z), (x_b, yF, z), r))
    s = cat(s, arc_h(x_b, yc, z, R, r, -90))
    s = cat(s, seg((x_b, yR, z), (-110, yR, z), r))
    s = cat(s, rpath([(-110, yR, z), (-124, yR, z), (-131, yd[i], z), (xD, yd[i], z)] + DISCESA(i), r, 5))
    s = cat(s, seg((xO, Y0, zy[i]), (xO, y_b, zy[i]), r))
    s = cat(s, arc_h(xc, y_b, zy[i], RY, r, 180))
    s = cat(s, seg((xI, y_b, zy[i]), (xI, y_f, zy[i]), r))
    # tratto fisso nella base: si allontana dall'ansa e prosegue verso il retro, ognuno alla sua quota
    if col == 'tubo':
        s = cat(s, rpath([(xI, y_f, zy[i]), (-84, y_f + 8, zy[i]), (-84, 14, zy[i]), (-89, 30, zy[i]), (-89, 104, zy[i]),
                          (-80, 113, 16), (-70, 117, 14)], r, 6))
        s = cat(s, spline([(-57, 122, 12), (-57, 124, 13), (-57, 127, 15)], r))
    else:
        s = cat(s, rpath([(xI, y_f, zy[i]), (-84, y_f + 8, zy[i]), (-84, 14, zy[i]), (-84, 22, zy[i])], r, 6))
    add(lab, s, col, 30 if col == 'tubo' else 0)

# cavo motore X: il motore e' sotto il piano sul carrello Y (fase 7). Il cavo corre lungo l'asta
# di collegamento fino a sinistra, passa sopra la pila degli altri cavi e si infila sotto, dal lato esterno.
i = N
s = rpath([(86, 40, 30), (80, 40, 36), (70, 16, 43), (-125, 16, 43), (-138, 14, 43), (-147, 12, 40),
           (-147, 10, 22), (-147, 8, zy[i]), (-145, 6, zy[i]), (xO, 3, zy[i])], 1.5, 5)
s = cat(s, seg((xO, 3, zy[i]), (xO, y_b, zy[i]), 1.5))
s = cat(s, arc_h(xc, y_b, zy[i], RY, 1.5, 180))
s = cat(s, seg((xI, y_b, zy[i]), (xI, y_f, zy[i]), 1.5))
s = cat(s, rpath([(xI, y_f, zy[i]), (-84, y_f + 8, zy[i]), (-84, 14, zy[i]), (-84, 22, zy[i])], 1.5, 6))
add('Cavo motore X NEMA17 (4 fili)', s, 'nero')

# ------------------------------------------------ lamine d'acciaio armonico (tengono in forma le anse)
lamZ = spline([(0, -50, 177), (0, -50, 186), (-3.8, -50, 195.2), (-13, -50, 199), (-22.2, -50, 195.2), (-26, -50, 186), (-26, -50, 170)], 0.5)
add('Lamina ansa Z', lamZ, 'lamina')
hX = (134.0, 157.0)
lam = box(x_m + 8, x_b, yF + 2.45, yF + 2.75, hX[0], hX[1]).fuse(box(x_f, x_b, yR - 2.75, yR - 2.45, hX[0], hX[1]))
lam = lam.fuse(half_ring(x_b, yc, hX[0], hX[1] - hX[0], R - 2.6, 0.3, -90))
add('Lamina ansa X', lam, 'lamina')
hY = (13.5, 41.0)
lam = box(xO + 2.45, xO + 2.75, y_b, 14, hY[0], hY[1]).fuse(box(xI - 2.75, xI - 2.45, y_b, y_f, hY[0], hY[1]))
lam = lam.fuse(half_ring(xc, y_b, hY[0], hY[1] - hY[0], RY - 2.6, 0.3, 180))
add('Lamina ansa Y', lam, 'lamina')

# ------------------------------------------------ fermacavi
add('Fermacavo ansa Z (sul carter)', box(-30, -22, -62, -42, 164, 168), 'clip')
add('Fermacavo uscita testa', box(-44, -18, -24, -19, 160, 164), 'clip')
add('Fermacavo punto fisso X', box(x_f - 4, x_f + 4, 47.3, 51, hX[0], hX[1]), 'clip')
add('Fermacavo punto fisso Y', box(xI + 2.3, xI + 8, y_f - 4, y_f + 4, hY[0], hY[1]), 'clip')

# ------------------------------------------------ carter e canali
hood = box(-52, 33, -62, -24, 128, 214.5).cut(box(-50.5, 31.5, -60.5, -24, 128, 213))
hood = hood.fuse(box(-52, 33, -24, -8, 161, 214.5).cut(box(-50.5, 31.5, -24, -8, 161, 213)))
add('Carter testa (trasparente)', hood, 'carter', 80)
can = box(-153, 149, -17, 58, 132, 133.5).cut(box(-146, -136.5, 36, 58, 131, 134))
can = can.fuse(box(-130, 149, 56.5, 58, 132, 158))
can = can.fuse(box(-153, -151.5, 0, 58, 121, 158)).fuse(box(147.5, 149, 0, 58, 121, 158))
add('Canale cavi sul gantry (lamiera)', can, 'lamiera')
add('Coperchio canale (trasparente)', box(-153, 149, -6, 58, 158, 159.5), 'carter', 75)
dc = box(-153, -130, 68, 69.5, 80, 159.5).fuse(box(-153, -151.5, 58, 69.5, 121, 159.5))
dc = dc.fuse(box(-146, -144.5, 56, 69.5, 80, 121)).fuse(box(-137.5, -136, 38, 69.5, 80, 132)).fuse(box(-136, -130, 56.5, 69.5, 132, 159.5).cut(box(-134.5, -130, 56.5, 68, 132, 158)))
dc = dc.fuse(box(-153, -130, 58, 69.5, 158, 159.5))
add('Carter discesa cavi (trasparente)', dc, 'carter', 75)

# ------------------------------------------------ base: pompa, valvola, scheda di controllo
add('Scheda di controllo + driver + alimentatore', box(-86, -30, 20, 110, 3, 42), 'pcb')
add('Elettrovalvola + sensore vuoto', box(-70, -45, 112, 122, 3, 25), 'valv')
add('Pompa del vuoto 12 V', box(-85, -35, 126, 160, 3, 38), 'pompa')

d.recompute()
print('ok', len(grp.Group), 'x_f=%.1f x_b=%.1f R=%.1f | y_f=%.1f y_b=%.1f RY=%.1f' % (x_f, x_b, R, y_f, y_b, RY))
