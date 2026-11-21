# Pannello "Assi A5ive": muove gantry Y, carrello X e asse Z del modello con tre cursori,
# e con "Anima" fa fare alla testa un ciclo di prova (vassoio -> telecamera dal basso -> area A5).
# Uso: con il modello aperto, Macro > Macro... > esegui questo file.
# Funziona cambiando carrello_x, carrello_y e z_nozzle nel foglio Parametri: il modello resta parametrico.
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui

try:
    from PySide import QtWidgets
except ImportError:
    QtWidgets = QtGui

TITOLO = 'Assi A5ive'


def _doc():
    d = App.ActiveDocument
    if d is None or d.getObject('Parametri') is None:
        for doc in App.listDocuments().values():
            if doc.getObject('Parametri') is not None:
                return doc
    return d


class PannelloAssi(QtWidgets.QWidget):
    ASSI = [('carrello_x', 'X (carrello)', 'corsa_x_min', 'corsa_x_max'),
            ('carrello_y', 'Y (gantry)', 'corsa_y_min', 'corsa_y_max'),
            ('z_nozzle', 'Z (0 = in alto)', None, 'corsa_z')]

    def __init__(self):
        super().__init__()
        self.d = _doc()
        self.s = self.d.getObject('Parametri')
        self.sliders, self.labels = {}, {}
        self.dirty = False
        lay = QtWidgets.QVBoxLayout(self)
        for alias, nome, amin, amax in self.ASSI:
            lo = 0.0 if amin is None else float(self.s.get(amin))
            hi = float(self.s.get(amax))
            lab = QtWidgets.QLabel()
            sl = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            sl.setRange(int(round(lo * 10)), int(round(hi * 10)))
            sl.setValue(int(round(float(self.s.get(alias)) * 10)))
            sl.valueChanged.connect(self._cambiato)
            lay.addWidget(lab)
            lay.addWidget(sl)
            self.sliders[alias], self.labels[alias] = sl, (lab, nome)
        self.cb_cavi = QtWidgets.QCheckBox('Nascondi la bozza dei cavi (non segue gli assi)')
        self.cb_cavi.toggled.connect(self._cavi)
        lay.addWidget(self.cb_cavi)
        riga = QtWidgets.QHBoxLayout()
        self.bt_anima = QtWidgets.QPushButton('Anima')
        self.bt_anima.setCheckable(True)
        self.bt_anima.toggled.connect(self._anima)
        bt_zero = QtWidgets.QPushButton('Zero')
        bt_zero.clicked.connect(self.zero)
        riga.addWidget(self.bt_anima)
        riga.addWidget(bt_zero)
        lay.addLayout(riga)
        lay.addStretch(1)
        self._aggiorna_etichette()
        # gruppi mobili: oggetti con un'espressione di posizione che usa carrello_x, carrello_y o z_nozzle.
        # Si spostano direttamente, senza ricalcolare tutto il modello (che richiede decine di secondi).
        self.legami = []
        for o in self.d.Objects:
            for path, expr in getattr(o, 'ExpressionEngine', []):
                if path.startswith('.Placement.Base.') and any(a in expr for a in self.sliders):
                    self.legami.append((o, path[-1], expr))
        # l'aggiornamento e' fatto al massimo ogni 40 ms, cosi' il cursore resta fluido
        self.t_ricalcolo = QtCore.QTimer(self)
        self.t_ricalcolo.timeout.connect(self._ricalcola)
        self.t_ricalcolo.start(40)
        self.t_anima = QtCore.QTimer(self)
        self.t_anima.timeout.connect(self._passo)
        self.percorso, self.i = [], 0

    def valore(self, alias):
        return self.sliders[alias].value() / 10.0

    def _aggiorna_etichette(self):
        for alias, (lab, nome) in self.labels.items():
            lab.setText('%s: %.1f mm' % (nome, self.valore(alias)))

    def _cambiato(self, _v):
        self._aggiorna_etichette()
        self.dirty = True

    def _ricalcola(self):
        if not self.dirty:
            return
        self.dirty = False
        for alias in self.sliders:
            self.s.set(alias, '%g' % self.valore(alias))
        self.s.recompute()                      # solo il foglio, non tutto il modello
        for o, comp, expr in self.legami:
            v = o.evalExpression(expr)
            v = float(getattr(v, 'Value', v))
            p = o.Placement
            b = p.Base
            setattr(b, comp, v)
            o.Placement = App.Placement(b, p.Rotation)
        Gui.updateGui()

    def _cavi(self, nascondi):
        for o in self.d.getObjectsByLabel('Proposta cavi (bozza)'):
            for c in o.Group:
                c.ViewObject.Visibility = not nascondi

    def imposta(self, x, y, z):
        for alias, v in (('carrello_x', x), ('carrello_y', y), ('z_nozzle', z)):
            sl = self.sliders[alias]
            sl.blockSignals(True)
            sl.setValue(int(round(v * 10)))
            sl.blockSignals(False)
        self._aggiorna_etichette()
        self.dirty = True

    def zero(self):
        self.bt_anima.setChecked(False)
        self.imposta(0, 0, 0)

    # ---- animazione: punti (x, y, z) del ciclo, interpolati a passi di circa 3 mm
    def _ciclo(self):
        g = lambda a: float(self.s.get(a))
        vx, vy = g('vassoio_x'), g('vassoio_y')
        cbx, cby = g('cam_basso_x'), g('cam_basso_y')
        a5y, yn = g('a5_y_centro'), g('y_noz')
        zc = g('corsa_z') - 2
        # il nozzle sta a y_noz dal gantry: per portarlo su un punto P serve carrello_y = P.y - y_noz
        tappe = [(0, 0, 0)]
        # due cicli: prendi dal vassoio, controlla sulla telecamera dal basso, appoggia sull'area A5
        for (px, py), (qx, qy) in [((vx - 60, vy), (-60, a5y + 30)), ((vx + 30, vy + 10), (60, a5y - 20))]:
            tappe += [(px, py - yn, 0), (px, py - yn, zc), (px, py - yn, 0),
                      (cbx, cby - yn, 0), (cbx, cby - yn, 8), (cbx, cby - yn, 0),
                      (qx, qy - yn, 0), (qx, qy - yn, zc), (qx, qy - yn, 0)]
        tappe.append((0, 0, 0))
        lim = {a: (float(self.sliders[a].minimum()) / 10, float(self.sliders[a].maximum()) / 10)
               for a in self.sliders}
        clamp = lambda v, a: max(lim[a][0], min(lim[a][1], v))
        tappe = [(clamp(x, 'carrello_x'), clamp(y, 'carrello_y'), clamp(z, 'z_nozzle')) for x, y, z in tappe]
        pts = []
        for a, b in zip(tappe[:-1], tappe[1:]):
            dist = max(abs(b[0] - a[0]), abs(b[1] - a[1]), abs(b[2] - a[2]))
            n = max(1, int(dist / 3.0))
            pts += [tuple(a[k] + (b[k] - a[k]) * j / n for k in range(3)) for j in range(n)]
        pts.append(tappe[-1])
        return pts

    def _anima(self, on):
        if on:
            self.percorso, self.i = self._ciclo(), 0
            self.bt_anima.setText('Ferma')
            self.t_anima.start(30)
        else:
            self.t_anima.stop()
            self.bt_anima.setText('Anima')

    def _passo(self):
        if self.i >= len(self.percorso):
            self.i = 0
        self.imposta(*self.percorso[self.i])
        self.i += 1


def mostra():
    mw = Gui.getMainWindow()
    for w in mw.findChildren(QtWidgets.QDockWidget):
        if w.windowTitle() == TITOLO:
            w.close()
            w.deleteLater()
    dock = QtWidgets.QDockWidget(TITOLO, mw)
    dock.setWidget(PannelloAssi())
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    dock.show()
    return dock


mostra()
