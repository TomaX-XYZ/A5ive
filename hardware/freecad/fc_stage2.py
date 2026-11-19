# Fase 2: rotaie MGN12 e pattini MGN12H (costruttori usati per asse Y e asse X)
import FreeCAD as App


def _sec(L, sk, pts, mu, mv):
    L.poly(sk, [(mu(u, w), mv(u, w)) for u, w in pts])


def rail(L, parent, label, axis, lengthE, centerE, cuE, cvE):
    """axis 'Y': sezione su XZ (u=X, v=Z), rotaia lungo Y con base a quota cvE, asse in X = cuE, sopra verso +Z.
    axis 'X': sezione su YZ (u=Y, v=Z), rotaia lungo X montata su faccia y=0 rivolta verso -Y, asse a Z = cvE."""
    b = L.mkbody(parent, label, 'rail')
    if axis == 'Y':
        sk = L.sketch(b, 'Sezione MGN12', 'XZ', off='-(%s)' % centerE)
        _sec(L, sk, L.RAIL, lambda u, w: '(%s) + (%g)' % (cuE, u), lambda u, w: '(%s) + (%g)' % (cvE, w))
        L.pad(b, sk, lengthE, 'Rotaia', sym=True)
        first = '(%s) - (%s)/2 + {testa_y}' % (centerE, lengthE)
        top = L.sketch(b, 'Lamature', 'XY', off='(%s) + 8' % cvE)
        L.circle(top, cuE, first, '6')
        p1 = L.pocket(b, top, 'Lamature', '4.5')
        thr = L.sketch(b, 'Fori M3', 'XY', off='(%s) + 8' % cvE)
        L.circle(thr, cuE, first, '3.5')
        p2 = L.pocket(b, thr, 'Fori M3', sym=True)
        L.pattern(b, [p1, p2], 'Y', '({n_fori_y} - 1)*{passo}', '{n_fori_y}', 'Serie fori')
    else:
        sk = L.sketch(b, 'Sezione MGN12', 'YZ', off=centerE)
        _sec(L, sk, L.RAIL, lambda u, w: '-(%g)' % w, lambda u, w: '(%s) + (%g)' % (cvE, u))
        L.pad(b, sk, lengthE, 'Rotaia', sym=True)
        first = '(%s) - (%s)/2 + {testa_x}' % (centerE, lengthE)
        top = L.sketch(b, 'Lamature', 'XZ', off='8')
        L.circle(top, first, cvE, '6')
        p1 = L.pocket(b, top, 'Lamature', '4.5')
        thr = L.sketch(b, 'Fori M3', 'XZ', off='8')
        L.circle(thr, first, cvE, '3.5')
        p2 = L.pocket(b, thr, 'Fori M3', sym=True)
        L.pattern(b, [p1, p2], 'X', '({n_fori_x} - 1)*{passo}', '{n_fori_x}', 'Serie fori')
    return b


def carriage(L, parent, label, axis, cuE, cvE, px=None, py=None):
    """Pattino MGN12H: App::Part con corpo acciaio, testate verdi e tenute rosse."""
    g = L.mkpart(parent, label, px=px, py=py)
    if axis == 'Y':
        pl = 'XZ'
        mu = lambda u, w: '(%s) + (%g)' % (cuE, u)
        mv = lambda u, w: '(%s) + (%g)' % (cvE, w)
        off = lambda pos: '-(%s)' % pos
    else:
        pl = 'YZ'
        mu = lambda u, w: '-(%g)' % w
        mv = lambda u, w: '(%s) + (%g)' % (cvE, u)
        off = lambda pos: '(%s)' % pos
    b = L.mkbody(g, 'Corpo acciaio', 'carr')
    sk = L.sketch(b, 'Sezione corpo', pl, off=off('0'))
    _sec(L, sk, L.car_sec(13), mu, mv)
    L.pad(b, sk, '{car_body}', 'Corpo', sym=True)
    if axis == 'Y':
        h = L.sketch(b, 'Fori M3', 'XY', off='(%s) + 13' % cvE)
        for du in (-10, 10):
            for dv in (-10, 10):
                L.circle(h, '(%s) + (%g)' % (cuE, du), '%g' % dv, '2.5')
    else:
        h = L.sketch(b, 'Fori M3', 'XZ', off='13')
        for du in (-10, 10):
            for dv in (-10, 10):
                L.circle(h, '%g' % du, '(%s) + (%g)' % (cvE, dv), '2.5')
    L.pocket(b, h, 'Fori M3', '3.5')
    for nome, col, d0, ln in (('Testate ricircolo', 'green', '{car_body}/2 + 2.25', '4.5'),
                              ('Tenute', 'red', '{car_body}/2 + 5.5', '2')):
        bb = L.mkbody(g, nome, col, compound=True)
        for sgn, lato in (('', 'a'), ('-', 'b')):
            sk = L.sketch(bb, 'Sezione %s %s' % (nome.lower(), lato), pl, off=off(sgn + '(%s)' % d0))
            _sec(L, sk, L.car_sec(12.6), mu, mv)
            L.pad(bb, sk, ln, '%s %s' % (nome, lato), sym=True)
    return g


def build(L, root):
    for lato, s in (('sinistra', '-'), ('destra', '')):
        g = L.mkpart(root, 'Guida Y ' + lato)
        rail(L, g, 'Rotaia MGN12 Y ' + lato, 'Y', '{lunghezza_rotaia}', '{rotaia_y_centro}', s + '{rx}', '{altezza_bordo}')
        carriage(L, g, 'Pattino MGN12H Y ' + lato, 'Y', s + '{rx}', '{altezza_bordo}', py='{carrello_y}')
    App.ActiveDocument.recompute()
