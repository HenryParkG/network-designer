import os
import json
from PyQt5 import QtWidgets, QtCore

def _serialize_for_json(obj):
    """
    재귀적으로 JSON-직렬화 가능 형태로 변환.
    - tuple, set -> list
    - objects with 'tolist' -> tolist()
    - dict/list -> 재귀 변환
    - 기타는 str()로 안전하게 변환 (가능하면 원래 타입 유지)
    """
    # 기본 타입
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    # dict
    if isinstance(obj, dict):
        return {str(k): _serialize_for_json(v) for k, v in obj.items()}
    # list/tuple/set
    if isinstance(obj, (list, tuple, set)):
        return [_serialize_for_json(v) for v in obj]
    # numpy / torch / pandas-like objects that have tolist()
    try:
        if hasattr(obj, "tolist"):
            return _serialize_for_json(obj.tolist())
    except Exception:
        pass
    # fallback: convertible to str
    try:
        return str(obj)
    except Exception:
        return None

def _coerce_loaded_value(val):
    """
    로드한 파라미터 값에 대해 간단한 정리:
    - "True"/"False" 문자열 -> bool
    - 리스트/딕셔너리는 재귀적으로 처리
    (숫자 문자열을 숫자로 바꾸는 자동 처리 등은 안전하지 않아 적용하지 않음)
    """
    if isinstance(val, str):
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        return val
    if isinstance(val, dict):
        return {k: _coerce_loaded_value(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_coerce_loaded_value(v) for v in val]
    return val

def save_design_json(layer_items, sequence_list, parent=None, default_filename="design.json"):
    """
    layer_items: {uid: LayerItem}
    sequence_list: QtWidgets.QListWidget
    parent: parent widget for dialogs (optional)
    """
    try:
        objs = []
        for uid, item in layer_items.items():
            # 안전한 pos 추출
            posf = [float(item.pos().x()), float(item.pos().y())] if hasattr(item, "pos") else [0.0, 0.0]
            # params 직렬화
            params_clean = _serialize_for_json(getattr(item, "params", {}) or {})
            # connections는 리스트화 + int 변환
            conns = []
            for c in getattr(item, "connections", []) or []:
                try:
                    conns.append(int(c))
                except Exception:
                    # 만약 연결값이 UID가 아니라면 무시하거나 str로 보관
                    try:
                        conns.append(int(str(c)))
                    except Exception:
                        pass
            objs.append({
                "uid": int(uid),
                "type": getattr(item, "layer_type", str(getattr(item, "type", ""))),
                "params": params_clean,
                "pos": posf,
                "connections": conns
            })

        seq = []
        for i in range(sequence_list.count()):
            data = sequence_list.item(i).data(QtCore.Qt.UserRole)
            try:
                seq.append(int(data))
            except Exception:
                # 만약 UserRole에 uid가 아닌 다른 형태가 들어있다면 str로 보관
                seq.append(data if data is not None else -1)

        doc = {"layers": objs, "sequence": seq}

        path, _ = QtWidgets.QFileDialog.getSaveFileName(parent, "Save Design", default_filename, "JSON files (*.json)")
        if not path:
            return

        # atomic write: tmp -> replace
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)

        QtWidgets.QMessageBox.information(parent, "Saved", f"Saved to {path}")

    except Exception as e:
        QtWidgets.QMessageBox.critical(parent, "Save Error", f"Failed to save design:\n{e}")


def auto_layout_layers(layer_items, start_x=50, start_y=50, x_gap=100, y_gap=100, per_row=5):
    """
    layer_items: uid -> LayerItem
    per_row: 한 행에 배치할 최대 레이어 수
    """
    i = 0
    for uid, item in sorted(layer_items.items()):
        row = i // per_row
        col = i % per_row
        x = start_x + col * x_gap
        y = start_y + row * y_gap
        item.setPos(x, y)
        i += 1



def load_design_json(designer_window, parent=None):
    """
    designer_window는 다음 메서드/속성을 가져야 함:
      - clear_canvas()
      - scene (QGraphicsScene)
      - layer_uid (int)
      - layer_items (dict)
      - sequence_list (QListWidget)
      - update_connections()
    """
    try:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(parent, "Load Design", "", "JSON files (*.json)")
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)

        # 기본 초기화
        designer_window.clear_canvas()

        # 1) 레이어들 먼저 생성 (UID 충돌 처리 포함)
        layers = doc.get("layers", [])
        # track existing uids to avoid accidental reuse
        max_uid = getattr(designer_window, "layer_uid", 0)

        from layers.layer_item import LayerItem  # 기존 사용하던 LayerItem 생성자 유지

        # create all items first
        for entry in layers:
            uid = int(entry.get("uid", 0))
            if uid <= 0:
                # skip invalid uid
                continue
            # ensure unique increasing uid in designer_window
            if uid <= max_uid:
                # 충돌 시 designer_window.layer_uid 뒤로 밀기
                max_uid += 1
                new_uid = max_uid
            else:
                new_uid = uid
                max_uid = max(max_uid, uid)

            t = entry.get("type")
            raw_params = entry.get("params", {}) or {}
            params = _coerce_loaded_value(raw_params)

            # instantiate LayerItem with (type, params, uid)
            try:
                item = LayerItem(t, params, new_uid)
            except TypeError:
                # fallback: LayerItem signature 다를 경우 최소한 생성
                item = LayerItem(t, params, new_uid)

            # setPos (pos가 문자열 등 이상하면 0,0으로)
            pos = entry.get("pos", [0, 0])
            try:
                item.setPos(QtCore.QPointF(float(pos[0]), float(pos[1])))
            except Exception:
                item.setPos(QtCore.QPointF(0.0, 0.0))

            # connections은 정수 리스트로 변환하여 임시 보관
            raw_conns = entry.get("connections", []) or []
            conns_clean = []
            for c in raw_conns:
                try:
                    conns_clean.append(int(c))
                except Exception:
                    # ignore non-int connections
                    pass
            item.connections = conns_clean

            # add to scene and registry
            designer_window.scene.addItem(item)
            designer_window.layer_items[new_uid] = item

            # store mapping if original uid changed (original_uid->new_uid)
            entry["_loaded_uid"] = new_uid

        # update global uid counter
        designer_window.layer_uid = max(max_uid, getattr(designer_window, "layer_uid", 0))

        # 2) sequence 복원 (entry 값이 원래 uid였을 때 매핑해서 사용)
        # Build a mapping from original uids in file to loaded uids
        file_to_loaded = { int(e.get("uid", -1)): e.get("_loaded_uid')", e.get("_loaded_uid")) for e in layers }  # defensive
        # The above line is defensive; we'll instead rebuild mapping properly:
        file_to_loaded = {}
        for e in layers:
            try:
                original = int(e.get("uid", -1))
            except Exception:
                original = -1
            if "_loaded_uid" in e:
                file_to_loaded[original] = int(e["_loaded_uid"])

        # now add sequence items (only those present in layer_items)
        for uid in doc.get("sequence", []):
            try:
                uid = int(uid)
            except Exception:
                continue
            mapped = file_to_loaded.get(uid, uid)  # if mapping exists use it
            if mapped in designer_window.layer_items:
                li = QtWidgets.QListWidgetItem(f"{designer_window.layer_items[mapped].layer_type} #{mapped}")
                li.setData(QtCore.Qt.UserRole, mapped)
                designer_window.sequence_list.addItem(li)

        # 3) update connections graphically (designer_window should implement it)
        auto_layout_layers(designer_window.layer_items)

        designer_window.update_connections()

    except Exception as e:
        QtWidgets.QMessageBox.critical(parent, "Load Error", f"Failed to load design:\n{e}")
