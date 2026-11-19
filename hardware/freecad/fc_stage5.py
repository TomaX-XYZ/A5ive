# Fase 5: testa di piazzamento sul ponte X
# - piastra testa, guida MGN7 verticale, NEMA8 lineare (vite) per lo Z
# - sul pattino Z: supporto, NEMA8 ad albero cavo (kit testina SMT), raccordo girevole KSH04-M5,
#   adattatore e ugello Juki
# - telecamera verso il basso fissa alla piastra (non segue lo Z) con anello LED
import FreeCAD as App

ZP = '{z_punta}'          # punta ugello a riposo
YN = '{y_noz}'            # asse ugello (Y)


def z(off):
    return '%s + (%g)' % (ZP, off)


def build(L, root):
    d = App.ActiveDocument
    carr = [o for o in d.Objects if o.TypeId == 'App::Part' and o.Label == 'Carrello X'][0]
    t = L.mkpart(carr, 'Testa di piazzamento')

    # --- piastra testa (sul fronte del ponte)
    b = L.mkbody(t, 'Piastra testa', 'blu')
    sk = L.sketch(b, 'Piastra', 'XZ', off='-({y_ponte_fronte})')
    L.rect(sk, '{cam_dx} - 17', z(-7), '25', z(73))
    L.pad(b, sk, '{sp_piastra_testa}', 'Piastra')
    sk = L.sketch(b, 'Fori ponte', 'XZ')
    for x in (-15, 15):
        for dz in (13, 38):
            L.circle(sk, '%g' % x, z(dz), '3.4')
    L.pocket(b, sk, 'Fori ponte', sym=True)

    # --- supporto motore Z (mensola in cima alla piastra)
    b = L.mkbody(t, 'Supporto motore Z', 'blu')
    sk = L.sketch(b, 'Mensola', 'XY', off=z(73))
    L.rect(sk, '7', YN, '27', '{y_ponte_fronte}')
    L.pad(b, sk, '4', 'Mensola')
    sk = L.sketch(b, 'Foro vite', 'XY')
    L.circle(sk, '17', '{y_pz} - 4', '5')
    L.pocket(b, sk, 'Foro vite', sym=True)

    # --- guida MGN7 verticale (70 mm, standard HIWIN)
    b = L.mkbody(t, 'Rotaia MGN7 Z', 'rail')
    sk = L.sketch(b, 'Sezione MGN7', 'XY', off=z(-5))
    L.rect(sk, '-3.5', '{y_rot_z} - 4.8', '3.5', '{y_rot_z}')
    L.pad(b, sk, '70', 'Rotaia')

    # --- motore Z: NEMA8 lineare con vite T4 che scende alla chiocciola
    b = L.mkbody(t, 'Motore NEMA8 lineare Z', 'motor')
    sk = L.sketch(b, 'Corpo', 'XY', off=z(77))
    L.rect(sk, '7', '{y_pz} - 14', '27', '{y_pz} + 6')
    L.pad(b, sk, '30', 'Corpo')
    b = L.mkbody(t, 'Vite T4 asse Z', 'steel')
    sk = L.sketch(b, 'Vite', 'XY', off=z(77))
    L.circle(sk, '17', '{y_pz} - 4', '4')
    L.pad(b, sk, '60', 'Vite', reversed=True)

    # --- telecamera verso il basso (fissa)
    c = L.mkpart(t, 'Telecamera verso il basso')
    b = L.mkbody(c, 'Braccio telecamera', 'blu')
    sk = L.sketch(b, 'Braccio', 'XY', off=z(36))
    L.rect(sk, '{cam_dx} - 13', YN + ' - 13', '{cam_dx} + 13', '{y_rot_z}')
    L.pad(b, sk, '4', 'Braccio')
    b = L.mkbody(c, 'Scheda telecamera 25x25', 'pcb')
    sk = L.sketch(b, 'Scheda', 'XY', off=z(34))
    L.rect(sk, '{cam_dx} - 12.5', YN + ' - 12.5', '{cam_dx} + 12.5', YN + ' + 12.5')
    L.pad(b, sk, '2', 'Scheda')
    b = L.mkbody(c, 'Obiettivo M12 telecamera alta', 'glass')
    sk = L.sketch(b, 'Obiettivo', 'XY', off=z(34))
    L.circle(sk, '{cam_dx}', YN, '14')
    L.pad(b, sk, '24', 'Obiettivo', reversed=True)
    b = L.mkbody(c, 'Anello LED telecamera alta', 'led')
    sk = L.sketch(b, 'Anello', 'XY', off=z(10))
    L.circle(sk, '{cam_dx}', YN, '30'); L.circle(sk, '{cam_dx}', YN, '16')
    L.pad(b, sk, '3', 'Anello LED', reversed=True)

    # --- parti che salgono e scendono (asse Z)
    zg = L.mkpart(t, 'Asse Z', pz='-{z_nozzle}')
    b = L.mkbody(zg, 'Pattino MGN7H Z', 'carr')
    sk = L.sketch(b, 'Sezione pattino', 'XY', off=z(27.6))
    yr = '{y_rot_z}'
    L.poly(sk, [('-8.5', yr + ' - 1.5'), ('-3.8', yr + ' - 1.5'), ('-3.8', yr + ' - 5'), ('3.8', yr + ' - 5'),
                ('3.8', yr + ' - 1.5'), ('8.5', yr + ' - 1.5'), ('8.5', '{y_pz}'), ('-8.5', '{y_pz}')])
    L.pad(b, sk, '30.8', 'Pattino')

    b = L.mkbody(zg, 'Supporto Z', 'blu')
    sk = L.sketch(b, 'Piastra', 'XZ', off='-({y_pz})')
    L.rect(sk, '-12', z(28), '12', z(58))
    L.pad(b, sk, '4', 'Piastra')
    sk = L.sketch(b, 'Mensola motore', 'XY', off=z(28))
    L.rect(sk, '-12', YN + ' - 10', '12', '{y_pz} - 4')
    L.pad(b, sk, '4', 'Mensola motore')
    sk = L.sketch(b, 'Orecchio chiocciola', 'XY', off=z(53))
    L.rect(sk, '11', YN + ' + 4', '23', '{y_pz}')
    L.pad(b, sk, '6', 'Orecchio chiocciola')
    sk = L.sketch(b, 'Fori', 'XY')
    L.circle(sk, '0', YN, '16')
    L.circle(sk, '17', '{y_pz} - 4', '4.6')
    L.pocket(b, sk, 'Fori', sym=True)

    b = L.mkbody(zg, 'Chiocciola T4 Z', 'brass')
    sk = L.sketch(b, 'Chiocciola', 'XY', off=z(59))
    L.circle(sk, '17', '{y_pz} - 4', '9')
    L.pad(b, sk, '4', 'Chiocciola')
    sk = L.sketch(b, 'Filetto', 'XY')
    L.circle(sk, '17', '{y_pz} - 4', '4.1')
    L.pocket(b, sk, 'Filetto', sym=True)

    b = L.mkbody(zg, 'Motore NEMA8 albero cavo', 'motor')
    sk = L.sketch(b, 'Corpo', 'XY', off=z(32))
    L.poly(sk, [('-10', YN + ' - 7.5'), ('-7.5', YN + ' - 10'), ('7.5', YN + ' - 10'), ('10', YN + ' - 7.5'),
                ('10', YN + ' + 7.5'), ('7.5', YN + ' + 10'), ('-7.5', YN + ' + 10'), ('-10', YN + ' + 7.5')])
    L.pad(b, sk, '{nema8_l}', 'Corpo')
    sk = L.sketch(b, 'Albero cavo', 'XY')
    L.circle(sk, '0', YN, '3')
    L.pocket(b, sk, 'Albero cavo', sym=True)

    b = L.mkbody(zg, 'Giunto rotante KSH04-M5', 'brass')
    zt = z(32) + ' + {nema8_l}'
    sk = L.sketch(b, 'Esagono', 'XY', off=zt)
    import math
    L.poly(sk, [('%.4f' % (5.774 * math.cos(math.radians(30 + 60 * i))),
                 YN + ' + (%.4f)' % (5.774 * math.sin(math.radians(30 + 60 * i)))) for i in range(6)])
    L.pad(b, sk, '6', 'Esagono 10')
    sk = L.sketch(b, 'Corpo girevole', 'XY', off=zt + ' + 6')
    L.circle(sk, '0', YN, '10')
    L.pad(b, sk, '12', 'Corpo girevole')
    sk = L.sketch(b, 'Innesto tubo', 'XY', off=zt + ' + 18')
    L.circle(sk, '0', YN, '4')
    L.pad(b, sk, '10', 'Tubo 4 mm')

    b = L.mkbody(zg, 'Adattatore ugello Juki', 'steel')
    sk = L.sketch(b, 'Adattatore', 'XY', off=z(20))
    L.circle(sk, '0', YN, '8')
    L.pad(b, sk, '8', 'Adattatore')
    b = L.mkbody(zg, 'Ugello Juki', 'steel')
    sk = L.sketch(b, 'Gambo', 'XY', off=z(10))
    L.circle(sk, '0', YN, '5')
    L.pad(b, sk, '10', 'Gambo')
    L.cone(b, 'Punta', '0', YN, ZP, '0.5', '2.5', '10')
    d.recompute()
