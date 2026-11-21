# Libreria per costruire il pick and place A5 in FreeCAD in modo parametrico.
# Ogni quota e' un'espressione collegata al foglio "Parametri": {nome} -> Parametri.nome
import re
import FreeCAD as App, Part, Sketcher

V = App.Vector
SHEET = 'Parametri'
COL = {'alu': (0.76, 0.77, 0.79), 'blu': (0.18, 0.36, 0.62), 'rail': (0.63, 0.65, 0.67), 'carr': (0.42, 0.43, 0.45),
       'green': (0.15, 0.55, 0.25), 'red': (0.72, 0.16, 0.12), 'motor': (0.12, 0.12, 0.13), 'brass': (0.82, 0.63, 0.25),
       'steel': (0.70, 0.72, 0.74), 'a5': (0.16, 0.32, 0.58), 'led': (0.94, 0.94, 0.88),
       'glass': (0.08, 0.12, 0.18), 'tray': (0.17, 0.17, 0.18), 'pcb': (0.10, 0.36, 0.16)}


def doc():
    return App.ActiveDocument


def E(s):
    """'{tx}/2 + 3' -> 'Parametri.tx/2 + 3'"""
    return re.sub(r'\{(\w+)\}', SHEET + r'.\1', str(s))


def ev(s):
    v = doc().getObject(SHEET).evalExpression(E(s))
    return float(getattr(v, 'Value', v))


def set_expr(obj, prop, expr):
    obj.setExpression(prop, E(expr))


# ---------------------------------------------------------------- contenitori
def mkpart(parent, label, px=None, py=None, pz=None):
    p = doc().addObject('App::Part', 'Part')
    p.Label = label
    if parent is not None:
        parent.addObject(p)
    for k, e in (('x', px), ('y', py), ('z', pz)):
        if e is not None:
            set_expr(p, '.Placement.Base.' + k, e)
    return p


def mkbody(parent, label, color, compound=False):
    b = doc().addObject('PartDesign::Body', 'Body')
    b.Label = label
    if parent is not None:
        parent.addObject(b)
    if compound and 'AllowCompound' in b.PropertiesList:
        b.AllowCompound = True
    paint(b, color)
    return b


def paint(obj, color):
    rgb = COL[color]
    vo = obj.ViewObject
    if 'ShapeAppearance' in vo.PropertiesList:
        m = App.Material()
        m.DiffuseColor = rgb + (1.0,)
        m.AmbientColor = tuple(c * 0.3 for c in rgb) + (1.0,)
        m.SpecularColor = (0.35, 0.35, 0.35, 1.0)
        m.Shininess = 0.35 if color in ('alu', 'rail', 'carr', 'steel', 'brass') else 0.15
        vo.ShapeAppearance = [m]
    else:
        vo.ShapeColor = rgb


def plane(body, role):
    for f in body.Origin.OriginFeatures:
        if f.Role == role:
            return f
    raise KeyError(role)


# ---------------------------------------------------------------- schizzi
def sketch(body, label, pl='XY', off=None):
    """pl: 'XY' (u=X v=Y, normale +Z), 'XZ' (u=X v=Z, normale -Y), 'YZ' (u=Y v=Z, normale +X).
    off: spostamento lungo la normale (espressione)."""
    sk = body.newObject('Sketcher::SketchObject', 'Sketch')
    sk.Label = label
    sk.AttachmentSupport = [(plane(body, pl + '_Plane'), '')]
    sk.MapMode = 'FlatFace'
    if off is not None:
        set_expr(sk, '.AttachmentOffset.Base.z', off)
    return sk


def _fix_point(sk, g, pos, ex, ey):
    for kind, e in (('DistanceX', ex), ('DistanceY', ey)):
        i = sk.addConstraint(Sketcher.Constraint(kind, -1, 1, g, pos, ev(e)))
        sk.setExpression('Constraints[%d]' % i, E(e))


def poly(sk, pts):
    """Poligono chiuso completamente vincolato: pts = [(espr_u, espr_v), ...]."""
    n = len(pts)
    xy = [(ev(a), ev(b)) for a, b in pts]
    first = None
    gs = []
    for i in range(n):
        a, b = xy[i], xy[(i + 1) % n]
        gs.append(sk.addGeometry(Part.LineSegment(V(a[0], a[1], 0), V(b[0], b[1], 0)), False))
    for i in range(n):
        sk.addConstraint(Sketcher.Constraint('Coincident', gs[i], 2, gs[(i + 1) % n], 1))
    for i in range(n):
        _fix_point(sk, gs[i], 1, pts[i][0], pts[i][1])
    return gs


def rect(sk, u0, v0, u1, v1):
    return poly(sk, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])


def circle(sk, cu, cv, dia):
    g = sk.addGeometry(Part.Circle(V(ev(cu), ev(cv), 0), V(0, 0, 1), ev(dia) / 2.0), False)
    _fix_point(sk, g, 3, cu, cv)
    i = sk.addConstraint(Sketcher.Constraint('Diameter', g, ev(dia)))
    sk.setExpression('Constraints[%d]' % i, E(dia))
    return g


def rel(pts, cu, cv, su=1, sv=1):
    """Converte punti relativi numerici in espressioni: (cu + su*u, cv + sv*v)."""
    return [('(%s) + (%g)' % (cu, su * u), '(%s) + (%g)' % (cv, sv * v)) for u, v in pts]


# ---------------------------------------------------------------- feature
def _symmetric(f):
    if 'SideType' in f.PropertiesList:
        f.SideType = 'Symmetric'
    else:
        f.Midplane = True


def pad(body, sk, length, label, reversed=False, sym=False):
    f = body.newObject('PartDesign::Pad', 'Pad')
    f.Label = label
    f.Profile = sk
    set_expr(f, 'Length', length)
    if sym:
        _symmetric(f)
    f.Reversed = reversed
    sk.Visibility = False
    return f


def pocket(body, sk, label, length=None, reversed=False, sym=False):
    f = body.newObject('PartDesign::Pocket', 'Pocket')
    f.Label = label
    f.Profile = sk
    if length is None:
        f.Type = 'ThroughAll'
    else:
        set_expr(f, 'Length', length)
    if sym:
        _symmetric(f)
    f.Reversed = reversed
    sk.Visibility = False
    return f


def pattern(body, feats, axis, length, occ, label):
    f = body.newObject('PartDesign::LinearPattern', 'LinearPattern')
    f.Label = label
    f.Originals = feats
    f.Direction = (plane(body, axis + '_Axis'), [''])
    set_expr(f, 'Length', length)
    set_expr(f, 'Occurrences', occ)
    for x in feats:
        x.Visibility = False
    return f


# ---------------------------------------------------------------- profili standard
RAIL = [(-6, 0), (6, 0), (6, 4.8), (5.2, 5.6), (6, 6.4), (6, 7.5), (5.5, 8),
        (-5.5, 8), (-6, 7.5), (-6, 6.4), (-5.2, 5.6), (-6, 4.8)]           # MGN12 (u trasversale, w altezza)


def car_sec(top):                                                          # pattino MGN12 (luce 3, gola 12,6)
    return [(-13.5, 3), (-6.3, 3), (-6.3, 8.2), (6.3, 8.2), (6.3, 3), (13.5, 3),
            (13.5, top - 0.5), (13, top), (-13, top), (-13.5, top - 0.5)]


NEMA = [(-21, -16.5), (-16.5, -21), (16.5, -21), (21, -16.5), (21, 16.5), (16.5, 21), (-16.5, 21), (-21, 16.5)]


def slot2040():
    """Contorno 2040 (u = profondita' 0..20, v = altezza 0..40) con cave 6 a gradino."""
    def cava(axis_pos, face, inward, along):
        # restituisce i punti della cava lungo il bordo, nel verso di percorrenza 'along' (+1/-1)
        w = [(-3.1, 0), (-3.1, 1.8), (-5.5, 1.8), (-5.5, 4.2), (-3.1, 4.2), (-3.1, 6.1),
             (3.1, 6.1), (3.1, 4.2), (5.5, 4.2), (5.5, 1.8), (3.1, 1.8), (3.1, 0)]
        if along < 0:
            w = [(-a, d) for a, d in w]
        return [(axis_pos + a, face + inward * d) for a, d in w]
    pts = [(0, 0)]
    # fondo (v=0) da u=0 a u=20, cava centrata u=10, verso +u, profondita' verso +v
    pts += [(u, v) for u, v in cava(10, 0, 1, 1)]
    pts += [(20, 0)]
    # retro (u=20) da v=0 a v=40, cave a v=10 e v=30, profondita' verso -u
    for c in (10, 30):
        pts += [(20 - d, c + a) for a, d in [(p[0] - 10, p[1]) for p in cava(10, 0, 1, 1)]]
    pts += [(20, 40)]
    # cima (v=40) da u=20 a u=0
    pts += [(10 + a, 40 - d) for a, d in [(p[0] - 10, p[1]) for p in cava(10, 0, 1, -1)]]
    pts += [(0, 40)]
    # fronte (u=0) da v=40 a v=0
    for c in (30, 10):
        pts += [(d, c + a) for a, d in [(p[0] - 10, p[1]) for p in cava(10, 0, 1, -1)]]
    return pts


# ---------------------------------------------------------------- colori finali
RULES = [('Supporto albero', 'blu'), ('Ingranaggio', 'brass'), ('Cuscinetto', 'steel'), ('Albero', 'steel'),
         ('albero cavo', 'motor'), ('Anello LED', 'led'), ('Obiettivo', 'glass'), ('Vassoio', 'tray'), ('Scheda', 'pcb'),
         ('Ugello', 'steel'), ('Adattatore', 'steel'), ('Giunto rotante', 'brass'), ('Pattino MGN7', 'carr'),
         ('Braccio', 'blu'), ('Zona', 'a5'), ('Rotaia', 'rail'), ('Corpo acciaio', 'carr'), ('Testate', 'green'), ('Tenute', 'red'),
         ('albero', 'steel'), ('Motore', 'motor'), ('Chiocciola', 'brass'), ('Asta', 'steel'), ('Vite', 'steel'),
         ('Staffa', 'blu'), ('Supporto', 'blu'), ('Piastra', 'blu'), ('Ponte', 'blu'), ('Testata', 'blu')]


def colorize(d):
    """In PartDesign si vede la feature finale del Body: il colore va dato anche alle feature."""
    for b in d.Objects:
        if b.TypeId != 'PartDesign::Body':
            continue
        c = next((col for k, col in RULES if k in b.Label), 'alu')
        paint(b, c)
        for f in b.Group:
            if f.TypeId.startswith('PartDesign::') and hasattr(f, 'Shape'):
                try:
                    paint(f, c)
                except Exception:
                    pass


def cone(body, label, cx, cy, z0, r_bottom, r_top, h):
    """Cono additivo verticale con base a quota z0 (espressioni)."""
    f = body.newObject('PartDesign::AdditiveCone', 'Cone')
    f.Label = label
    f.Radius1 = ev(r_bottom); f.Radius2 = ev(r_top); f.Height = ev(h)
    set_expr(f, 'Radius1', r_bottom); set_expr(f, 'Radius2', r_top); set_expr(f, 'Height', h)
    set_expr(f, '.Placement.Base.x', cx); set_expr(f, '.Placement.Base.y', cy); set_expr(f, '.Placement.Base.z', z0)
    return f
