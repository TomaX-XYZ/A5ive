# Rigenera da zero il modello parametrico del pick and place A5 in FreeCAD 1.x.
# Uso: in FreeCAD, Macro > Macro... > esegui questo file (gli altri fc_*.py devono stare nella stessa cartella).
import os, types
import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    m = types.ModuleType(name)
    m.__file__ = os.path.join(HERE, name + '.py')
    exec(open(m.__file__, encoding='utf-8').read(), m.__dict__)
    return m


def main(doc_name='A5ive_pick_and_place'):
    d = App.newDocument(doc_name)
    d.Label = 'Pick and Place A5'
    L = load('fc_lib')
    S1, S2, S3, S4 = load('fc_stage1'), load('fc_stage2'), load('fc_stage3'), load('fc_stage4')
    S5, S6, S7 = load('fc_stage5'), load('fc_stage6'), load('fc_stage7')
    root = S1.build(L)
    S2.build(L, root)
    S3.build(L, root)
    S4.build(L, S2, S3, root)
    S5.build(L, root)
    S6.build(L, root)
    S7.build(L, root)
    for o in d.Objects:
        if o.TypeId == 'Sketcher::SketchObject':
            o.Visibility = False
    d.recompute()
    L.colorize(d)
    return d


if __name__ == '__main__':
    main()
