# Fase 6: parte frontale - vassoio 2x8 per componenti sfusi e telecamera dal basso con anello LED
import FreeCAD as App


def build(L, root):
    d = App.ActiveDocument
    g = L.mkpart(root, 'Parte frontale')
    H = '{altezza_bordo}'
    W = '(8*{cella} + 9*{parete_vassoio})'
    D = '(2*{cella} + 3*{parete_vassoio})'

    # --- vassoio 16 scomparti
    b = L.mkbody(g, 'Vassoio 16 scomparti', 'tray')
    sk = L.sketch(b, 'Ingombro', 'XY', off=H)
    L.rect(sk, '{vassoio_x} - %s/2' % W, '{vassoio_y} - %s/2' % D, '{vassoio_x} + %s/2' % W, '{vassoio_y} + %s/2' % D)
    L.pad(b, sk, '{vassoio_h}', 'Vassoio')
    sk = L.sketch(b, 'Scomparti', 'XY', off=H + ' + {vassoio_h}')
    for i in range(8):
        for j in range(2):
            x0 = '{vassoio_x} - %s/2 + {parete_vassoio} + %d*({cella} + {parete_vassoio})' % (W, i)
            y0 = '{vassoio_y} - %s/2 + {parete_vassoio} + %d*({cella} + {parete_vassoio})' % (D, j)
            L.rect(sk, x0, y0, '(%s) + {cella}' % x0, '(%s) + {cella}' % y0)
    L.pocket(b, sk, 'Scomparti', '{vassoio_h} - 2')

    # --- telecamera dal basso
    c = L.mkpart(g, 'Telecamera dal basso')
    cx, cy = '{cam_basso_x}', '{cam_basso_y}'
    b = L.mkbody(c, 'Supporto telecamera bassa', 'blu')
    sk = L.sketch(b, 'Base', 'XY', off=H)
    L.rect(sk, cx + ' - 17', cy + ' - 17', cx + ' + 17', cy + ' + 17')
    L.pad(b, sk, '10', 'Supporto')   # tutto sotto la traversa X (fondo a z_st)
    sk = L.sketch(b, 'Sede obiettivo', 'XY', off=H + ' + 10')
    L.circle(sk, cx, cy, '14.4')
    L.pocket(b, sk, 'Sede obiettivo', '6')
    b = L.mkbody(c, 'Obiettivo M12 telecamera bassa', 'glass')
    sk = L.sketch(b, 'Obiettivo', 'XY', off=H + ' + 4')
    L.circle(sk, cx, cy, '14')
    L.pad(b, sk, '12', 'Obiettivo')
    b = L.mkbody(c, 'Anello LED telecamera bassa', 'led')
    sk = L.sketch(b, 'Anello', 'XY', off=H + ' + 10')
    L.circle(sk, cx, cy, '32'); L.circle(sk, cx, cy, '18')
    L.pad(b, sk, '3', 'Anello LED')
    d.recompute()
