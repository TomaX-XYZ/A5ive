# Fase 3: trascinamento Y (staffe con linguetta, asta, blocco chiocciola, vite, supporti, motore, giunto)
import FreeCAD as App


def coupler(L, parent, label, axis, a0, a1, cu, cv):
    """Giunto elastico 5x8 D19x25 fra a0 (lato vite) e a1 (lato motore) lungo l'asse 'X' o 'Y'."""
    b = L.mkbody(parent, label, 'alu')
    if axis == 'Y':           # XZ, normale -Y: pad verso -Y
        pl, off, rev_in = 'XZ', lambda y: '-(%s)' % y, False
        sk = L.sketch(b, 'Cilindro', pl, off=off(a1)); L.circle(sk, cu, cv, '19'); L.pad(b, sk, '25', 'Giunto')
        sk = L.sketch(b, 'Foro 8', pl, off=off(a0)); L.circle(sk, cu, cv, '8.1'); L.pocket(b, sk, 'Foro vite 8', '12.5')
        sk = L.sketch(b, 'Foro 5', pl, off=off(a1)); L.circle(sk, cu, cv, '5.1'); L.pocket(b, sk, 'Foro albero 5', '12.5', reversed=True)
        sk = L.sketch(b, 'Gola', pl, off=off('(%s) + 8' % a0))
    else:                     # YZ, normale +X
        pl, off = 'YZ', lambda x: '(%s)' % x
        sk = L.sketch(b, 'Cilindro', pl, off=off(a0)); L.circle(sk, cu, cv, '19'); L.pad(b, sk, '25', 'Giunto')
        sk = L.sketch(b, 'Foro 8', pl, off=off(a0)); L.circle(sk, cu, cv, '8.1'); L.pocket(b, sk, 'Foro vite 8', '12.5', reversed=True)
        sk = L.sketch(b, 'Foro 5', pl, off=off(a1)); L.circle(sk, cu, cv, '5.1'); L.pocket(b, sk, 'Foro albero 5', '12.5')
        sk = L.sketch(b, 'Gola', pl, off=off('(%s) + 8' % a0))
    L.circle(sk, cu, cv, '21'); L.circle(sk, cu, cv, '10')
    g = L.pocket(b, sk, 'Gola', '1.2', reversed=(axis == 'X'))
    L.pattern(b, [g], axis, '9', '4', 'Gole elastiche')
    return b


def motor(L, parent, label, axis, face, cu, cv, shaft_to):
    """NEMA17 42x42x40 con centraggio D22 e albero D5. face = flangia; corpo verso l'esterno (+Y o +X)."""
    b = L.mkbody(parent, label, 'motor')
    if axis == 'Y':
        pl, off = 'XZ', lambda y: '-(%s)' % y
        sk = L.sketch(b, 'Corpo', pl, off=off(face))
        L.poly(sk, [('(%s) + (%g)' % (cu, u), '(%s) + (%g)' % (cv, v)) for u, v in L.NEMA])
        L.pad(b, sk, '40', 'Corpo', reversed=True)
        sk = L.sketch(b, 'Centraggio', pl, off=off(face)); L.circle(sk, cu, cv, '22'); L.pad(b, sk, '2', 'Centraggio')
        s = L.mkbody(parent, label + ' albero', 'steel')
        sk = L.sketch(s, 'Albero', pl, off=off('(%s) - 2' % face)); L.circle(sk, cu, cv, '5')
        L.pad(s, sk, '((%s) - 2) - (%s)' % (face, shaft_to), 'Albero')
    else:
        pl, off = 'YZ', lambda x: '(%s)' % x
        sk = L.sketch(b, 'Corpo', pl, off=off(face))
        L.poly(sk, [('(%s) + (%g)' % (cu, u), '(%s) + (%g)' % (cv, v)) for u, v in L.NEMA])
        L.pad(b, sk, '40', 'Corpo')
        sk = L.sketch(b, 'Centraggio', pl, off=off(face)); L.circle(sk, cu, cv, '22'); L.pad(b, sk, '2', 'Centraggio', reversed=True)
        s = L.mkbody(parent, label + ' albero', 'steel')
        sk = L.sketch(s, 'Albero', pl, off=off('(%s) - 2' % face)); L.circle(sk, cu, cv, '5')
        L.pad(s, sk, '((%s) - 2) - (%s)' % (face, shaft_to), 'Albero', reversed=True)
    return b


def build(L, root):
    d = App.ActiveDocument
    g = L.mkpart(root, 'Trascinamento Y')
    m = L.mkpart(g, 'Carrello Y', py='{carrello_y}')
    zu = '({altezza_bordo} - {spessore})'

    # --- staffe con linguetta
    for lato, s in (('sinistra', '-'), ('destra', '')):
        b = L.mkbody(m, 'Staffa pattino ' + lato, 'blu')
        sk = L.sketch(b, 'Piastra', 'XY', off='{z_pattino}')
        L.rect(sk, s + '({rx} - 13.5)', '-22.5', s + '{tab_out}', '22.5')
        L.pad(b, sk, '{staffa_sp}', 'Piastra')
        sk = L.sketch(b, 'Linguetta', 'XY', off='{z_asta} - 10')
        L.rect(sk, s + '{tab_in}', '-10', s + '{tab_out}', '10')
        L.pad(b, sk, '{z_st} - ({z_asta} - 10)', 'Linguetta')
        sk = L.sketch(b, 'Lamature', 'XY', off='{z_st}')
        for du in (-10, 10):
            for dv in (-10, 10):
                L.circle(sk, s + '({rx} + (%g))' % du, '%g' % dv, '6')
        L.pocket(b, sk, 'Lamature', '3')
        sk = L.sketch(b, 'Fori pattino', 'XY', off='{z_st}')
        for du in (-10, 10):
            for dv in (-10, 10):
                L.circle(sk, s + '({rx} + (%g))' % du, '%g' % dv, '3.4')
        L.circle(sk, s + '{rx}', '10', '5.2')
        L.pocket(b, sk, 'Fori pattino e profilo', sym=True)
        sk = L.sketch(b, 'Foro asta', 'YZ')
        L.circle(sk, '0', '{z_asta}', '10.1')
        L.pocket(b, sk, 'Foro asta', sym=True)

    # --- asta di collegamento
    b = L.mkbody(m, 'Asta di collegamento D10', 'steel')
    sk = L.sketch(b, 'Sezione', 'YZ'); L.circle(sk, '0', '{z_asta}', '10')
    L.pad(b, sk, '2*{tab_out}', 'Asta', sym=True)

    # --- blocco chiocciola e chiocciola
    b = L.mkbody(m, 'Blocco chiocciola Y', 'alu')
    sk = L.sketch(b, 'Pianta', 'XY', off='{z_vite_y} - 13')
    L.rect(sk, '-18', '-12', '18', '12')
    L.pad(b, sk, '%s - 1 - ({z_vite_y} - 13)' % zu, 'Blocco')
    sk = L.sketch(b, 'Foro asta', 'YZ'); L.circle(sk, '0', '{z_asta}', '10.1'); L.pocket(b, sk, 'Foro asta', sym=True)
    sk = L.sketch(b, 'Foro vite', 'XZ'); L.circle(sk, '0', '{z_vite_y}', '10.4'); L.pocket(b, sk, 'Foro vite', sym=True)
    b = L.mkbody(m, 'Chiocciola T8 Y', 'brass')
    sk = L.sketch(b, 'Flangia', 'XZ', off='12'); L.circle(sk, '0', '{z_vite_y}', '22'); L.pad(b, sk, '3.5', 'Flangia')
    sk = L.sketch(b, 'Corpo', 'XZ', off='12'); L.circle(sk, '0', '{z_vite_y}', '10.2'); L.pad(b, sk, '15', 'Corpo', reversed=True)
    sk = L.sketch(b, 'Filetto', 'XZ'); L.circle(sk, '0', '{z_vite_y}', '8'); L.pocket(b, sk, 'Foro filettato', sym=True)

    # --- vite T8x8
    b = L.mkbody(g, 'Vite T8x8 Y', 'steel')
    sk = L.sketch(b, 'Sezione', 'XZ', off='-(({y_front} - 8 + {y_cp0} + 12)/2)')
    L.circle(sk, '0', '{z_vite_y}', '8')
    L.pad(b, sk, '{y_cp0} + 12 - ({y_front} - 8)', 'Vite', sym=True)

    # --- supporto anteriore
    b = L.mkbody(g, 'Supporto anteriore vite Y', 'blu')
    sk = L.sketch(b, 'Piastra', 'XZ', off='-{y_front}')
    L.rect(sk, '-22', '3', '22', zu); L.pad(b, sk, '5', 'Piastra')
    sk = L.sketch(b, 'Flangia', 'XY', off='%s - 4' % zu)
    L.rect(sk, '-22', '{y_front} - 10', '22', '{y_front}'); L.pad(b, sk, '4', 'Flangia')   # verso la parete: non ruba corsa
    sk = L.sketch(b, 'Sede cuscinetto', 'XZ', off='-({y_front} - 5)')
    L.circle(sk, '0', '{z_vite_y}', '22'); L.pad(b, sk, '4', 'Sede cuscinetto 608')
    sk = L.sketch(b, 'Foro vite', 'XZ'); L.circle(sk, '0', '{z_vite_y}', '8.4'); L.pocket(b, sk, 'Foro vite', sym=True)

    # --- piastra motore
    b = L.mkbody(g, 'Piastra motore Y', 'blu')
    sk = L.sketch(b, 'Piastra', 'XZ', off='-{y_mf}')
    L.rect(sk, '-25', '3', '25', zu); L.pad(b, sk, '5', 'Piastra')
    sk = L.sketch(b, 'Flangia', 'XY', off='%s - 4' % zu)
    L.rect(sk, '-25', '{y_pl} - 12', '25', '{y_mf}'); L.pad(b, sk, '4', 'Flangia')
    sk = L.sketch(b, 'Fori motore', 'XZ')
    L.circle(sk, '0', '{z_vite_y}', '22.4')
    for du in (-15.5, 15.5):
        for dv in (-15.5, 15.5):
            L.circle(sk, '%g' % du, '{z_vite_y} + (%g)' % dv, '3.4')
    L.pocket(b, sk, 'Fori motore', sym=True)

    motor(L, g, 'Motore NEMA17 Y', 'Y', '{y_mf}', '0', '{z_vite_y}', '{y_cp1} - 12.5')
    coupler(L, g, 'Giunto elastico 5x8 Y', 'Y', '{y_cp0}', '{y_cp1}', '0', '{z_vite_y}')
    d.recompute()
