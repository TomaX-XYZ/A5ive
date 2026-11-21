# Fase 4: gantry X (profilo 2040, rotaia e pattino X, ponte, chiocciola, testate, motore, giunto, vite)
import FreeCAD as App


def testata(L, g, lato):
    """Testata del profilo X. Sinistra: sede del cuscinetto 608 della vite.
    Destra: finestra per la scatola del rinvio alto (il motore X sta sotto il piano, fase 7)."""
    yv, zv = '{y_vx}', '{z_vx}'
    s = '-' if lato == 'sinistra' else ''
    b = L.mkbody(g, 'Testata %s X' % lato, 'blu')
    sk = L.sketch(b, 'Piastra', 'YZ', off=s + '{x_e}')
    L.rect(sk, '0', '{z_prof} - 2', yv + ' + 23', '{z_prof} + 42')
    L.pad(b, sk, '5', 'Piastra', reversed=(s == '-'))
    sk = L.sketch(b, 'Fori', 'YZ')
    for v in (10, 30):
        L.circle(sk, '10', '{z_prof} + %d' % v, '5.2')
    if s == '-':
        L.circle(sk, yv, zv, '8.4')
    L.pocket(b, sk, 'Fori', sym=True)
    if s == '-':
        sk = L.sketch(b, 'Sede cuscinetto', 'YZ', off='-{x_e} - 5')
        L.circle(sk, yv, zv, '22'); L.pad(b, sk, '4', 'Sede cuscinetto 608', reversed=True)
        sk = L.sketch(b, 'Foro sede', 'YZ'); L.circle(sk, yv, zv, '8.4'); L.pocket(b, sk, 'Foro sede', sym=True)
    else:
        sk = L.sketch(b, 'Finestra rinvio', 'YZ')
        L.rect(sk, yv + ' - 13', '{z_prof} - 3', yv + ' + 13', zv + ' + 14')     # aperta in basso: passa l'albero verticale
        L.pocket(b, sk, 'Finestra scatola rinvio', sym=True)
    return b


def giunto_rigido(L, g):
    """Giunto rigido 5->8 D14 L22 fra vite X (lato x_cp0) e albero d'uscita del rinvio."""
    yv, zv = '{y_vx}', '{z_vx}'
    b = L.mkbody(g, 'Giunto rigido 5x8 X', 'alu')
    sk = L.sketch(b, 'Cilindro', 'YZ', off='{x_cp0}'); L.circle(sk, yv, zv, '14'); L.pad(b, sk, '{x_cp1} - {x_cp0}', 'Giunto')
    sk = L.sketch(b, 'Foro 8', 'YZ', off='{x_cp0}'); L.circle(sk, yv, zv, '8.1')
    L.pocket(b, sk, 'Foro vite 8', '({x_cp1} - {x_cp0})/2', reversed=True)
    sk = L.sketch(b, 'Foro 5', 'YZ', off='{x_cp1}'); L.circle(sk, yv, zv, '5.1')
    L.pocket(b, sk, 'Foro albero 5', '({x_cp1} - {x_cp0})/2')
    return b


def build(L, S2, S3, root):
    d = App.ActiveDocument
    g = L.mkpart(root, 'Gantry X', py='{carrello_y}')
    yv, zv = '{y_vx}', '{z_vx}'

    # --- profilo 2040 in piedi
    b = L.mkbody(g, 'Profilo 2040 X', 'alu')
    sk = L.sketch(b, 'Sezione 2040', 'YZ')
    L.poly(sk, [('%g' % u, '{z_prof} + (%g)' % v) for u, v in L.slot2040()])
    for v in (10, 30):
        L.circle(sk, '10', '{z_prof} + %d' % v, '4.2')
    L.pad(b, sk, '2*{x_e}', 'Profilo', sym=True)

    S2.rail(L, g, 'Rotaia MGN12 X', 'X', '{lunghezza_rotaia_x}', '0', None, '{z_rot}')

    # --- parti mobili in X
    c = L.mkpart(g, 'Carrello X', px='{carrello_x}')
    S2.carriage(L, c, 'Pattino MGN12H X', 'X', None, '{z_rot}')

    b = L.mkbody(c, 'Ponte pattino-chiocciola X', 'blu')
    sk = L.sketch(b, 'Piastra anteriore', 'XZ', off='13')
    L.rect(sk, '-22.7', '{z_rot} - 13.5', '22.7', '{z_ponte} + 6'); L.pad(b, sk, '6', 'Piastra anteriore')
    sk = L.sketch(b, 'Piastra superiore', 'XY', off='{z_ponte}')
    L.rect(sk, '-12', '-19', '12', yv + ' + 11'); L.pad(b, sk, '6', 'Piastra superiore')
    sk = L.sketch(b, 'Blocco', 'XY', off=zv + ' - 13')
    L.rect(sk, '-10', yv + ' - 11', '10', yv + ' + 11'); L.pad(b, sk, '{z_ponte} - (%s - 13)' % zv, 'Blocco chiocciola')
    sk = L.sketch(b, 'Fori pattino', 'XZ', off='19')
    for du in (-10, 10):
        for dv in (-10, 10):
            L.circle(sk, '%g' % du, '{z_rot} + (%g)' % dv, '3.4')
    L.pocket(b, sk, 'Fori pattino', '6.5')
    sk = L.sketch(b, 'Foro vite', 'YZ'); L.circle(sk, yv, zv, '10.4'); L.pocket(b, sk, 'Foro vite', sym=True)

    b = L.mkbody(c, 'Chiocciola T8 X', 'brass')
    sk = L.sketch(b, 'Flangia', 'YZ', off='-10'); L.circle(sk, yv, zv, '22'); L.pad(b, sk, '3.5', 'Flangia', reversed=True)
    sk = L.sketch(b, 'Corpo', 'YZ', off='-10'); L.circle(sk, yv, zv, '10.2'); L.pad(b, sk, '15', 'Corpo')
    sk = L.sketch(b, 'Filetto', 'YZ'); L.circle(sk, yv, zv, '8'); L.pocket(b, sk, 'Foro filettato', sym=True)

    # --- testate profilo
    testata(L, g, 'sinistra')
    testata(L, g, 'destra')
    giunto_rigido(L, g)

    b = L.mkbody(g, 'Vite T8x8 X', 'steel')
    sk = L.sketch(b, 'Sezione', 'YZ', off='(-{x_e} - 8 + {x_cp0} + 12)/2')
    L.circle(sk, yv, zv, '8')
    L.pad(b, sk, '{x_cp0} + 12 + {x_e} + 8', 'Vite', sym=True)
    d.recompute()
