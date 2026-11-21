# Fase 7: motore X sotto il piano con due rinvii conici a 90 gradi.
# Il motore e' appeso alla linguetta della staffa Y destra e si muove in Y con il gantry.
# Rinvio basso: coppia conica mod. 0,8, 15 denti (Ø primitivo 12) -> albero verticale Ø5 nell'asola destra.
# Rinvio alto: coppia conica mod. 1, 20 denti (Ø primitivo 20) -> albero d'uscita -> giunto rigido -> vite X.
import FreeCAD as App

ROT = {'+X': App.Rotation(App.Vector(0, 1, 0), 90), '-X': App.Rotation(App.Vector(0, 1, 0), -90),
       '+Z': App.Rotation(), '-Z': App.Rotation(App.Vector(1, 0, 0), 180)}
VEC = {'+X': (1, 0, 0), '-X': (-1, 0, 0), '+Z': (0, 0, 1), '-Z': (0, 0, -1)}
# dimensioni ingranaggi (dentatura disegnata come cono primitivo a 45 gradi):
# raggio dietro, raggio in punta, altezza dentatura, raggio e lunghezza mozzo
GEAR = {'m08': (7.0, 3.0, 4.0, 5.0, 5.0), 'm1': (11.0, 7.0, 4.0, 7.0, 5.0)}


def _prim(L, body, kind, label, P, u, shift, **dims):
    f = body.newObject('PartDesign::' + kind, kind)
    f.Label = label
    for k, v in dims.items():
        setattr(f, k, v)
    f.Placement = App.Placement(App.Vector(), ROT[u])
    for comp, e, s in zip('xyz', P, VEC[u]):
        L.set_expr(f, '.Placement.Base.' + comp, '(%s) + (%g)' % (e, s * shift))
    return f


def conica(L, parent, label, size, P, u):
    """Ingranaggio conico: P = centro del cerchio primitivo (espressioni), u = verso l'apice."""
    r1, r2, h, rm, lm = GEAR[size]
    b = L.mkbody(parent, label, 'brass')
    _prim(L, b, 'AdditiveCone', 'Dentatura', P, u, -1, Radius1=r1, Radius2=r2, Height=h)
    _prim(L, b, 'AdditiveCylinder', 'Mozzo', P, u, -1 - lm, Radius=rm, Height=lm)
    _prim(L, b, 'SubtractiveCylinder', 'Foro 5', P, u, -1 - lm - 1, Radius=2.5, Height=lm + h + 2)
    return b


def f605(L, parent, label, C, u, flangia=True):
    """Cuscinetto F605ZZ 5x14x5 con flangia 16x1 (oppure 605ZZ senza flangia), appoggiato in C verso u."""
    b = L.mkbody(parent, label, 'steel')
    _prim(L, b, 'AdditiveCylinder', 'Anello', C, u, 0, Radius=7, Height=5)
    if flangia:
        _prim(L, b, 'AdditiveCylinder', 'Flangia', C, u, 0, Radius=8, Height=1)
    _prim(L, b, 'SubtractiveCylinder', 'Foro', C, u, 0, Radius=2.5, Height=5)
    return b


def build(L, root):
    d = App.ActiveDocument
    gantry = [o for o in d.Objects if o.TypeId == 'App::Part' and o.Label == 'Gantry X'][0]
    g = L.mkpart(gantry, 'Rinvio X (motore sotto il piano)')
    xr, yv, zr, zv = '{x_rv}', '{y_vx}', '{z_rv}', '{z_vx}'

    # --- motore NEMA17 sotto il piano, asse lungo X, corpo verso -X
    b = L.mkbody(g, 'Motore NEMA17 X (sotto il piano)', 'motor')
    sk = L.sketch(b, 'Corpo', 'YZ', off='{x_mx}')
    L.poly(sk, [('(%s) + (%g)' % (yv, u), '(%s) + (%g)' % (zr, v)) for u, v in L.NEMA])
    L.pad(b, sk, '40', 'Corpo', reversed=True)
    sk = L.sketch(b, 'Centraggio', 'YZ', off='{x_mx}'); L.circle(sk, yv, zr, '22'); L.pad(b, sk, '2', 'Centraggio')
    s = L.mkbody(g, 'Motore NEMA17 X albero', 'steel')
    sk = L.sketch(s, 'Albero', 'YZ', off='{x_mx} + 2'); L.circle(sk, yv, zr, '5')
    L.pad(s, sk, '{x_rv} - {x_mx} - 5', 'Albero')

    # --- staffa del motore, avvitata sotto la linguetta della staffa Y destra
    b = L.mkbody(g, 'Staffa motore X', 'blu')
    sk = L.sketch(b, 'Piastra', 'YZ', off='{x_mx}')
    L.rect(sk, yv + ' - 21', zr + ' - 21', yv + ' + 21', zr + ' + 21'); L.pad(b, sk, '3', 'Piastra')
    sk = L.sketch(b, 'Braccio', 'XY', off='{z_asta} - 13')
    L.rect(sk, '{x_mx}', '-10', '{tab_out}', yv + ' - 13'); L.pad(b, sk, '3', 'Braccio')
    sk = L.sketch(b, 'Fori motore', 'YZ')
    L.circle(sk, yv, zr, '22.4')
    for du in (-15.5, 15.5):
        for dv in (-15.5, 15.5):
            L.circle(sk, '%s + (%g)' % (yv, du), '%s + (%g)' % (zr, dv), '3.4')
    L.pocket(b, sk, 'Fori motore', sym=True)

    # --- rinvio basso: scatola, coppia conica mod. 0,8, cuscinetto
    b = L.mkbody(g, 'Scatola rinvio basso', 'alu')
    sk = L.sketch(b, 'Pianta', 'XY', off=zr + ' - 12')
    L.rect(sk, '{x_mx} + 3.5', yv + ' - 13', '{tx}/2 - {spessore} - 0.2', yv + ' + 13'); L.pad(b, sk, '25', 'Scatola')
    sk = L.sketch(b, 'Vano', 'XY', off=zr + ' + 11')
    L.rect(sk, '{x_mx} + 5.5', yv + ' - 11', '{tx}/2 - {spessore} - 2.2', yv + ' + 11'); L.pocket(b, sk, 'Vano', '21')
    sk = L.sketch(b, 'Foro motore', 'YZ'); L.circle(sk, yv, zr, '16'); L.pocket(b, sk, 'Foro motore', sym=True)
    sk = L.sketch(b, 'Foro albero', 'XY'); L.circle(sk, xr, yv, '14'); L.pocket(b, sk, 'Foro albero', sym=True)
    conica(L, g, 'Ingranaggio conico motore (m0,8 z15)', 'm08', (xr + ' - {rp_rv1}', yv, zr), '+X')
    conica(L, g, 'Ingranaggio conico verticale basso (m0,8 z15)', 'm08', (xr, yv, zr + ' + {rp_rv1}'), '-Z')
    f605(L, g, 'Cuscinetto F605 rinvio basso', (xr, yv, zr + ' + 13'), '+Z')

    # --- albero verticale Ø5 nell'asola destra, con supporto sulla staffa Y
    b = L.mkbody(g, 'Albero verticale Ø5', 'steel')
    sk = L.sketch(b, 'Sezione', 'XY', off=zr + ' + {rp_rv1} - 4'); L.circle(sk, xr, yv, '5')
    L.pad(b, sk, '{z_vx} - {rp_rv} + 1.5 - ({z_rv} + {rp_rv1} - 4)', 'Albero')     # finisce dentro l'ingranaggio alto
    b = L.mkbody(g, 'Supporto albero verticale (sulla staffa Y)', 'blu')
    sk = L.sketch(b, 'Piastra', 'XY', off='{z_pattino} - 7')
    L.rect(sk, xr + ' - 7', '23', xr + ' + 7', yv + ' + 7'); L.pad(b, sk, '4', 'Piastra')
    sk = L.sketch(b, 'Foro', 'XY'); L.circle(sk, xr, yv, '5.4'); L.pocket(b, sk, 'Foro', sym=True)
    f605(L, g, 'Cuscinetto F605 supporto', (xr, yv, '{z_pattino} - 3'), '+Z')

    # --- rinvio alto: scatola a gradino (lascia passare il giunto), coppia conica mod. 1, cuscinetti
    b = L.mkbody(g, 'Scatola rinvio alto', 'alu')
    sk = L.sketch(b, 'Parte bassa', 'XY', off=zv + ' - 19.5')
    L.rect(sk, xr + ' - 14', yv + ' - 13', xr + ' + 13', yv + ' + 13'); L.pad(b, sk, '13.5', 'Parte bassa')
    sk = L.sketch(b, 'Parte alta', 'XY', off=zv + ' - 6')
    L.rect(sk, '{x_cp1}', yv + ' - 13', xr + ' + {rp_rv} + 15', yv + ' + 13'); L.pad(b, sk, '20', 'Parte alta')
    sk = L.sketch(b, 'Vano', 'XY', off=zv + ' + 12')
    L.rect(sk, xr + ' - 12', yv + ' - 11', xr + ' + {rp_rv} + 13', yv + ' + 11'); L.pocket(b, sk, 'Vano', '29.5')
    sk = L.sketch(b, 'Foro uscita', 'YZ'); L.circle(sk, yv, zv, '14'); L.pocket(b, sk, 'Foro uscita', sym=True)
    sk = L.sketch(b, 'Foro albero', 'XY'); L.circle(sk, xr, yv, '14'); L.pocket(b, sk, 'Foro albero', sym=True)
    conica(L, g, 'Ingranaggio conico verticale alto (m1 z20)', 'm1', (xr, yv, zv + ' - {rp_rv}'), '+Z')
    conica(L, g, 'Ingranaggio conico uscita (m1 z20)', 'm1', (xr + ' + {rp_rv}', yv, zv), '-X')
    f605(L, g, 'Cuscinetto F605 rinvio alto', (xr, yv, zv + ' - 21'), '+Z')
    f605(L, g, 'Cuscinetto 605 uscita sinistro (senza flangia)', ('{x_cp1} + 0.5', yv, zv), '+X', flangia=False)
    f605(L, g, 'Cuscinetto F605 uscita destro', (xr + ' + {rp_rv} + 7', yv, zv), '+X')
    b = L.mkbody(g, 'Albero uscita Ø5', 'steel')
    sk = L.sketch(b, 'Sezione', 'YZ', off='{x_cp1} - 10'); L.circle(sk, yv, zv, '5')
    L.pad(b, sk, '{x_rv} + {rp_rv} + 13 - ({x_cp1} - 10)', 'Albero')

    d.recompute()
    for o in g.Group:
        if o.TypeId == 'PartDesign::Body' and o.Label.startswith('Scatola') and o.ViewObject:
            o.ViewObject.Transparency = 60
    return g
