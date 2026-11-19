# Fase 4: gantry X (profilo 2040, rotaia e pattino X, ponte, chiocciola, testate, motore, giunto, vite)
import FreeCAD as App


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
    for lato, s in (('sinistra', '-'), ('destra', '')):
        b = L.mkbody(g, 'Testata %s X' % lato, 'blu')
        sk = L.sketch(b, 'Piastra', 'YZ', off=s + '{x_e}')
        L.rect(sk, '0', '{z_prof} - 2', yv + ' + 23', '{z_prof} + 42')
        L.pad(b, sk, '5', 'Piastra', reversed=(s == '-'))
        sk = L.sketch(b, 'Fori', 'YZ')
        for v in (10, 30):
            L.circle(sk, '10', '{z_prof} + %d' % v, '5.2')
        if s == '-':
            L.circle(sk, yv, zv, '8.4')
        else:
            L.circle(sk, yv, zv, '22.4')
            for du in (-15.5, 15.5):
                for dv in (-15.5, 15.5):
                    L.circle(sk, '%s + (%g)' % (yv, du), '%s + (%g)' % (zv, dv), '3.4')
        L.pocket(b, sk, 'Fori', sym=True)
        if s == '-':
            sk = L.sketch(b, 'Sede cuscinetto', 'YZ', off='-{x_e} - 5')
            L.circle(sk, yv, zv, '22'); L.pad(b, sk, '4', 'Sede cuscinetto 608', reversed=True)
            sk = L.sketch(b, 'Foro sede', 'YZ'); L.circle(sk, yv, zv, '8.4'); L.pocket(b, sk, 'Foro sede', sym=True)

    S3.motor(L, g, 'Motore NEMA17 X', 'X', '{x_e} + 5', yv, zv, '{x_cp1} - 12.5')
    S3.coupler(L, g, 'Giunto elastico 5x8 X', 'X', '{x_cp0}', '{x_cp1}', yv, zv)

    b = L.mkbody(g, 'Vite T8x8 X', 'steel')
    sk = L.sketch(b, 'Sezione', 'YZ', off='(-{x_e} - 8 + {x_cp0} + 12)/2')
    L.circle(sk, yv, zv, '8')
    L.pad(b, sk, '{x_cp0} + 12 + {x_e} + 8', 'Vite', sym=True)
    d.recompute()
