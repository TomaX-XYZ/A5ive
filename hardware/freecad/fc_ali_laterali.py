# Ali laterali (versione 0.3): le rotaie Y non stanno piu' sul piano ma sulla faccia interna di due ali,
# una a destra e una a sinistra. I pattini Y lavorano di fianco e reggono le staffe di testa del gantry X.
import FreeCAD as App

ROT_Y = {'destra': App.Rotation(App.Vector(0, 1, 0), -90), 'sinistra': App.Rotation(App.Vector(0, 1, 0), 90)}


def ala(L, root, lato):
    s = '' if lato == 'destra' else '-'
    b = L.mkbody(root, 'Ala %s' % lato, 'alu')
    sk = L.sketch(b, 'Profilo ala', 'YZ', off=s + '{x_ala}')
    L.poly(sk, [('-{ty}/2', '{altezza_bordo}'), ('{ty}/2', '{altezza_bordo}'), ('{ty}/2', '{ala_top}'),
                ('{ala_smusso_y}', '{ala_top}'), ('-{ty}/2', '{ala_z_fronte}')])
    L.pad(b, sk, '{ala_sp}', 'Ala', reversed=(s == '-'))
    sk = L.sketch(b, 'Fori rotaia', 'YZ')
    L.circle(sk, '{rotaia_y_centro} - {lunghezza_rotaia}/2 + {testa_y}', '{z_ry}', '3.4')
    p = L.pocket(b, sk, 'Fori rotaia', sym=True)
    L.pattern(b, [p], 'Y', '({n_fori_y} - 1)*{passo}', '{n_fori_y}', 'Serie fori rotaia')
    return b


def guida(L, S2, root, lato):
    """Rotaia MGN12 sulla faccia interna dell'ala, pattino rivolto verso il centro della macchina."""
    s = '' if lato == 'destra' else '-'
    g = L.mkpart(root, 'Guida Y ' + lato)
    g.Placement = App.Placement(App.Vector(), ROT_Y[lato])
    L.set_expr(g, '.Placement.Base.x', s + '{x_ala}')
    L.set_expr(g, '.Placement.Base.z', '{z_ry}')
    S2.rail(L, g, 'Rotaia MGN12 Y ' + lato, 'Y', '{lunghezza_rotaia}', '{rotaia_y_centro}', '0', '0')
    S2.carriage(L, g, 'Pattino MGN12H Y ' + lato, 'Y', '0', '0', py='{carrello_y} + {y_cy}')
    return g


def staffa_gantry(L, gantry, lato):
    """Piastra fra pattino Y e testata del profilo X: regge anche il cuscinetto 608 della vite X."""
    s = '' if lato == 'destra' else '-'
    yv, zv = '{y_vx}', '{z_vx}'
    b = L.mkbody(gantry, 'Staffa gantry %s' % lato, 'blu')
    sk = L.sketch(b, 'Piastra', 'YZ', off=s + '{x_e}')
    L.rect(sk, '{y_cy} - 25', '{z_prof} - 2', yv + ' + 12', '{z_prof} + 42')
    L.pad(b, sk, '{staffa_sp}', 'Piastra', reversed=(s == '-'))
    sk = L.sketch(b, 'Sede cuscinetto', 'YZ', off=s + '{x_e}')
    L.circle(sk, yv, zv, '22')
    L.pad(b, sk, '4', 'Sede cuscinetto 608', reversed=(s == ''))       # verso l'interno, lontano dalla rotaia
    sk = L.sketch(b, 'Fori', 'YZ')
    L.circle(sk, yv, zv, '8.4')
    for v in (10, 30):
        L.circle(sk, '10', '{z_prof} + %d' % v, '5.2')                   # viti M5 nelle testate del 2040
    for du in (-10, 10):
        for dv in (-10, 10):
            L.circle(sk, '{y_cy} + (%g)' % du, '{z_ry} + (%g)' % dv, '3.4')   # viti M3 del pattino
    L.pocket(b, sk, 'Fori', sym=True)
    return b


def build(L, S2, root):
    d = App.ActiveDocument
    gantry = [o for o in d.Objects if o.TypeId == 'App::Part' and o.Label == 'Gantry X'][0]
    for lato in ('sinistra', 'destra'):
        ala(L, root, lato)
        guida(L, S2, root, lato)
        staffa_gantry(L, gantry, lato)
    d.recompute()
