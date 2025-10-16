from PyQt5 import QtWidgets
import json

def save_design_json(layer_items, sequence_list):
    objs=[]
    for uid, item in layer_items.items():
        objs.append({"uid": uid, "type": item.layer_type, "params": item.params,
                     "pos": [item.pos().x(), item.pos().y()], "connections": item.connections})
    seq=[sequence_list.item(i).data(QtCore.Qt.UserRole) for i in range(sequence_list.count())]
    doc = {"layers": objs, "sequence": seq}
    path,_ = QtWidgets.QFileDialog.getSaveFileName(None,"Save Design","design.json","JSON files (*.json)")
    if path:
        with open(path,"w",encoding="utf-8") as f:
            json.dump(doc,f,indent=2)
        QtWidgets.QMessageBox.information(None,"Saved",f"Saved to {path}")

def load_design_json(designer_window):
    path,_ = QtWidgets.QFileDialog.getOpenFileName(None,"Load Design","","JSON files (*.json)")
    if path:
        with open(path,"r",encoding="utf-8") as f:
            doc = json.load(f)
        designer_window.clear_canvas()
        for entry in doc.get("layers",[]):
            uid=entry["uid"]
            designer_window.layer_uid = max(designer_window.layer_uid, uid)
            t=entry["type"]
            params=entry["params"]
            from layers.layer_item import LayerItem
            item=LayerItem(t,params,uid)
            from Py
