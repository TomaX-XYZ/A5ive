# Fase 1: documento, foglio Parametri, telaio in lamiera, zona A5
import FreeCAD as App

PARAMS = [
    # (alias, valore o formula, descrizione)
    ('--', '', 'AREA DI LAVORO E TELAIO'),
    ('area_x', '210', 'Area di lavoro A5 - lato lungo (X)'),
    ('area_y', '148', 'Area di lavoro A5 - lato corto (Y)'),
    ('margine_x', '50', 'Margine laterale, dal bordo A5 al bordo esterno'),
    ('margine_y', '100', 'Margine anteriore e posteriore'),
    ('spessore', '1.5', 'Spessore lamiera'),
    ('raggio_piega', '1.5', 'Raggio interno di piega'),
    ('altezza_bordo', '60', 'Altezza bordo piegato = quota del piano'),
    ('risvolto', '12', 'Risvolto verso l interno, misurato dall esterno'),
    ('tx', '=area_x + 2*margine_x', 'Ingombro telaio X'),
    ('ty', '=area_y + 2*margine_y', 'Ingombro telaio Y'),
    ('--', '', 'GUIDE MGN12 (dimensioni standard)'),
    ('dist_guida_A5', '20', 'Asse rotaia Y dal bordo area A5'),
    ('rx', '=area_x/2 + dist_guida_A5', 'Vecchio asse rotaie Y sul piano (usato ancora da asole e asta Y)'),
    ('passo', '25', 'Passo fori rotaia MGN12'),
    ('car_w', '27', 'Larghezza pattino MGN12H'),
    ('car_l', '45.4', 'Lunghezza totale pattino MGN12H'),
    ('car_body', '32.4', 'Lunghezza corpo acciaio pattino'),
    ('lunghezza_rotaia', '270', 'Rotaie asse Y sulle ali'),
    ('rotaia_y_centro', '-10', 'Centro rotaie Y'),
    ('n_fori_y', '=floor((lunghezza_rotaia - 10)/passo) + 1', 'Numero fori rotaia Y'),
    ('testa_y', '=(lunghezza_rotaia - (n_fori_y - 1)*passo)/2', 'Primo foro rotaia Y dalla testa'),
    ('lunghezza_rotaia_x', '=2*x_e', 'Rotaia asse X (tagliata a misura, lunga quanto il profilo)'),
    ('n_fori_x', '=floor((lunghezza_rotaia_x - 10)/passo) + 1', 'Numero fori rotaia X'),
    ('testa_x', '=(lunghezza_rotaia_x - (n_fori_x - 1)*passo)/2', 'Primo foro rotaia X dalla testa'),
    ('--', '', 'ASOLE E TRASCINAMENTO Y'),
    ('asola_larghezza', '7', 'Larghezza asole linguette'),
    ('asola_lunghezza', '296', 'Lunghezza asole (da rivedere: le rotaie Y ora sono sulle ali)'),
    ('asola_y_centro', '-8', 'Centro asole Y'),
    ('asola_x', '=rx + car_w/2 + asola_larghezza/2', 'Asse asole (+/-)'),
    ('z_pattino', '=altezza_bordo + 13', 'Sopra dei pattini MGN12H'),
    ('staffa_sp', '6', 'Spessore staffe sui pattini Y'),
    ('z_st', '=z_pattino + staffa_sp', 'Sopra delle staffe = fondo profilo X'),
    ('tab_in', '=rx + car_w/2 + 1.5', 'Faccia interna linguetta'),
    ('tab_sp', '4', 'Spessore linguetta'),
    ('tab_out', '=tab_in + tab_sp', 'Faccia esterna linguetta'),
    ('z_asta', '51', 'Quota asse asta di collegamento D10'),
    ('z_vite_y', '23', 'Quota asse vite e motore Y'),
    ('y_front', '-160', 'Faccia posteriore supporto anteriore vite Y'),
    ('parete_y', '=ty/2 - spessore', 'Faccia interna parete posteriore'),
    ('y_mb', '=parete_y - 1.5', 'Retro motore Y'),
    ('y_mf', '=y_mb - 40', 'Flangia motore Y'),
    ('y_pl', '=y_mf - 5', 'Faccia anteriore piastra motore Y'),
    ('y_cp1', '=y_pl - 1', 'Retro giunto Y'),
    ('y_cp0', '=y_cp1 - 25', 'Fronte giunto Y'),
    ('--', '', 'ALI LATERALI E ROTAIE Y'),
    ('ala_sp', '6', 'Spessore ali laterali (piastra in alluminio)'),
    ('x_ala', '=tx/2 - ala_sp', 'Faccia interna ali = appoggio rotaie Y (+/-)'),
    ('z_ry', '=z_prof + 20', 'Asse rotaie Y sulle ali (centro del profilo X)'),
    ('x_cy', '=x_ala - 13', 'Faccia di montaggio pattini Y (+/-)'),
    ('y_cy', '10', 'Centro pattini Y rispetto al gantry (sotto il centro del 2040)'),
    ('ala_top', '=z_ry + 21', 'Bordo superiore ali'),
    ('ala_z_fronte', '=altezza_bordo + 20', 'Altezza ali sul davanti (smusso)'),
    ('ala_smusso_y', '=rotaia_y_centro - lunghezza_rotaia/2', 'Inizio smusso ali (davanti alle rotaie)'),
    ('--', '', 'GANTRY X'),
    ('x_e', '=x_cy - staffa_sp', 'Testate profilo X = faccia interna staffe del gantry (+/-)'),
    ('z_prof', '=z_st', 'Fondo profilo 2040'),
    ('z_rot', '=z_st + 30', 'Asse rotaia X (cava alta)'),
    ('z_vx', '=z_st + 20', 'Asse vite X'),
    ('y_vx', '33', 'Asse vite X (dietro al profilo)'),
    ('z_ponte', '=z_st + 46', 'Fondo piastra superiore ponte'),
    ('--', '', 'TESTA DI PIAZZAMENTO'),
    ('corsa_z', '25', 'Corsa asse Z'),
    ('z_punta', '=altezza_bordo + corsa_z + 2', 'Quota punta ugello a riposo (Z in alto)'),
    ('y_ponte_fronte', '-19', 'Faccia anteriore del ponte X'),
    ('sp_piastra_testa', '5', 'Spessore piastra testa'),
    ('y_rot_z', '=y_ponte_fronte - sp_piastra_testa', 'Faccia di appoggio rotaia MGN7 Z'),
    ('y_pz', '=y_rot_z - 8', 'Faccia anteriore pattino MGN7H Z'),
    ('y_noz', '=y_pz - 4 - 10', 'Asse ugello rispetto al gantry (Y)'),
    ('cam_dx', '-28', 'Telecamera verso il basso: scostamento X dall ugello'),
    ('nema8_l', '30', 'Lunghezza NEMA8 albero cavo (da verificare sul pezzo)'),
    ('--', '', 'PARTE FRONTALE'),
    ('a5_y_centro', '-35', 'Centro area A5 (spostata in avanti)'),
    ('cella', '19', 'Scomparto vassoio (lato)'),
    ('parete_vassoio', '1.5', 'Parete tra gli scomparti'),
    ('vassoio_h', '10', 'Altezza vassoio'),
    ('vassoio_x', '-20', 'Centro vassoio X'),
    ('vassoio_y', '-140', 'Centro vassoio Y'),
    ('cam_basso_x', '90', 'Telecamera dal basso: centro X (lontana dal pattino Y destro)'),
    ('cam_basso_y', '-140', 'Telecamera dal basso: centro Y'),
    ('--', '', 'CORSE E POSIZIONE ATTUALE'),
    ('corsa_y_min', '=(y_front + 16.5) > (rotaia_y_centro - (lunghezza_rotaia - car_l)/2 - y_cy) ? (y_front + 16.5) : (rotaia_y_centro - (lunghezza_rotaia - car_l)/2 - y_cy)', 'Minimo centro carrello Y'),
    ('corsa_y_max', '=(y_cp0 - 13) < (rotaia_y_centro + (lunghezza_rotaia - car_l)/2 - y_cy) ? (y_cp0 - 13) : (rotaia_y_centro + (lunghezza_rotaia - car_l)/2 - y_cy)', 'Massimo centro carrello Y'),
    ('corsa_x_min', '=-(lunghezza_rotaia_x - car_l)/2 > -(x_ala - 8) + 46 ? -(lunghezza_rotaia_x - car_l)/2 : -(x_ala - 8) + 46', 'Minimo centro pattino X (a sinistra comanda la testa: sporge 45 mm verso la rotaia Y)'),
    ('corsa_x_max', '=(lunghezza_rotaia_x - car_l)/2', 'Massimo centro pattino X'),
    ('carrello_y', '0', 'POSIZIONE gantry Y (cambiala per muoverlo)'),
    ('carrello_x', '0', 'POSIZIONE pattino X (cambiala per muoverlo)'),
    ('z_nozzle', '0', 'POSIZIONE asse Z: 0 = in alto, fino a corsa_z'),
]


def build_sheet(d):
    s = d.addObject('Spreadsheet::Sheet', 'Parametri')
    s.Label = 'Parametri'
    s.set('A1', 'Parametro'); s.set('B1', 'Valore [mm]'); s.set('C1', 'Descrizione')
    s.setStyle('A1:C1', 'bold')
    r = 2
    for alias, val, desc in PARAMS:
        if alias == '--':
            s.set('A%d' % r, desc); s.setStyle('A%d' % r, 'bold')
        else:
            s.set('A%d' % r, alias); s.set('B%d' % r, val); s.set('C%d' % r, desc)
            s.setAlias('B%d' % r, alias)
        r += 1
    s.setColumnWidth('A', 160); s.setColumnWidth('C', 360)
    d.recompute()
    return s


def fillets(L, d, b):
    """Raggi di piega: esterni = raggio_piega + spessore, interni = raggio_piega."""
    d.recompute()
    s = d.getObject('Parametri')
    tx, ty, H, t = s.tx, s.ty, s.altezza_bordo, s.spessore
    near = lambda a, c: abs(a - c) < 1e-6

    def perim(p1, p2, z, hx, hy):
        if not (near(p1.z, z) and near(p2.z, z)):
            return False
        return ((near(abs(p1.x), hx) and near(p1.x, p2.x)) or (near(abs(p1.y), hy) and near(p1.y, p2.y)))

    def pick(shape, test):
        out = []
        for i, e in enumerate(shape.Edges, 1):
            if e.Curve.__class__.__name__ == 'Line' and test(e.Vertexes[0].Point, e.Vertexes[-1].Point):
                out.append('Edge%d' % i)
        return out
    tip = b.Tip
    f1 = b.newObject('PartDesign::Fillet', 'Fillet')
    f1.Label = 'Pieghe esterne'
    f1.Base = (tip, pick(tip.Shape, lambda a, c: perim(a, c, H, tx / 2, ty / 2) or perim(a, c, 0, tx / 2, ty / 2)))
    L.set_expr(f1, 'Radius', '{raggio_piega} + {spessore}')
    d.recompute()
    f2 = b.newObject('PartDesign::Fillet', 'Fillet')
    f2.Label = 'Pieghe interne'
    f2.Base = (f1, pick(f1.Shape, lambda a, c: perim(a, c, H - t, tx / 2 - t, ty / 2 - t) or perim(a, c, t, tx / 2 - t, ty / 2 - t)))
    L.set_expr(f2, 'Radius', '{raggio_piega}')
    d.recompute()


def build(L):
    d = App.ActiveDocument
    build_sheet(d)
    root = L.mkpart(None, 'Pick and Place A5')

    # ---------------- Telaio in lamiera piegata due volte
    b = L.mkbody(root, 'Telaio A5', 'alu')
    sk = L.sketch(b, 'Contorno', 'XY')
    L.rect(sk, '-{tx}/2', '-{ty}/2', '{tx}/2', '{ty}/2')
    L.pad(b, sk, '{altezza_bordo}', 'Ingombro')
    sk = L.sketch(b, 'Vano interno', 'XY')
    L.rect(sk, '-{tx}/2 + {spessore}', '-{ty}/2 + {spessore}', '{tx}/2 - {spessore}', '{ty}/2 - {spessore}')
    L.pocket(b, sk, 'Svuota sotto il piano', '{altezza_bordo} - {spessore}', reversed=True)
    sk = L.sketch(b, 'Risvolti', 'XY')
    xw, yw = '{tx}/2 - {spessore}', '{ty}/2 - {spessore}'
    xi, yi = '{tx}/2 - {risvolto}', '{ty}/2 - {risvolto}'
    for s in (1, -1):
        S = '' if s > 0 else '-'
        L.poly(sk, [(S + '(%s)' % xw, '(%s) - 0.25' % yw), (S + '(%s)' % xw, '-(%s) + 0.25' % yw),
                    (S + '(%s)' % xi, '-(%s) + 0.25' % yi), (S + '(%s)' % xi, '(%s) - 0.25' % yi)])
        L.poly(sk, [('(%s) - 0.25' % xw, S + '(%s)' % yw), ('-(%s) + 0.25' % xw, S + '(%s)' % yw),
                    ('-(%s) + 0.25' % xi, S + '(%s)' % yi), ('(%s) - 0.25' % xi, S + '(%s)' % yi)])
    L.pad(b, sk, '{spessore}', 'Risvolti')
    sk = L.sketch(b, 'Scarichi angoli', 'XY')
    c = '({raggio_piega} + {spessore})'
    for sx in ('', '-'):
        for sy in ('', '-'):
            L.rect(sk, sx + '({tx}/2 - %s)' % c, sy + '({ty}/2 - %s)' % c, sx + '({tx}/2 + 1)', sy + '({ty}/2 + 1)')
    L.pocket(b, sk, 'Scarichi angoli', sym=True)
    sk = L.sketch(b, 'Asole', 'XY', off='{altezza_bordo}')
    hl = '({asola_lunghezza}/2 - {asola_larghezza}/2)'
    for sx in ('', '-'):
        L.rect(sk, sx + '({asola_x} - {asola_larghezza}/2)', '{asola_y_centro} - %s' % hl,
               sx + '({asola_x} + {asola_larghezza}/2)', '{asola_y_centro} + %s' % hl)
    L.pocket(b, sk, 'Asole', '2*{spessore}')
    sk = L.sketch(b, 'Estremita asole', 'XY', off='{altezza_bordo}')
    for sx in ('', '-'):
        for sy in ('+', '-'):
            L.circle(sk, sx + '{asola_x}', '{asola_y_centro} %s %s' % (sy, hl), '{asola_larghezza}')
    L.pocket(b, sk, 'Estremita asole', '2*{spessore}')
    fillets(L, d, b)

    # ---------------- Zona di lavoro A5 (segno colorato 0,1 mm sul piano)
    b = L.mkbody(root, 'Zona di lavoro A5', 'a5')
    sk = L.sketch(b, 'Area A5', 'XY', off='{altezza_bordo}')
    L.rect(sk, '-{area_x}/2', '{a5_y_centro} - {area_y}/2', '{area_x}/2', '{a5_y_centro} + {area_y}/2')
    L.pad(b, sk, '0.1', 'Segno A5')
    d.recompute()
    return root
