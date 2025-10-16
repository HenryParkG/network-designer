from PyQt5 import QtCore

def validate_network(layer_items, sequence_list):
    """
    Neural Network 구조 검증
    - layer_items: {uid: LayerItem, ...}
    - sequence_list: QListWidget (DesignerWindow에서)
    
    반환: (True/False, 메시지)
    """

    if sequence_list.count() == 0:
        return False, "레이어가 하나도 없습니다."

    # Sequence 순서대로 UID 리스트
    uids = [sequence_list.item(i).data(QtCore.Qt.UserRole) for i in range(sequence_list.count())]

    # -------------------------------
    # 1️⃣ 연결 존재 확인
    # -------------------------------
    for uid in uids:
        item = layer_items.get(uid)
        if not item:
            return False, f"레이어 UID {uid}가 존재하지 않습니다."
        # 연결된 레이어가 layer_items 안에 존재하는지
        for tgt_uid in item.connections:
            if tgt_uid not in layer_items:
                return False, f"{item.layer_type} #{uid} 연결 대상 UID {tgt_uid}가 존재하지 않습니다."

    # -------------------------------
    # 2️⃣ 논리적 연결 검증 (Linear, Conv2d → Flatten 등)
    # -------------------------------
    for i in range(len(uids)-1):
        src = layer_items[uids[i]]
        tgt = layer_items[uids[i+1]]

        if src.layer_type == "Linear" and (src.params.get("out_features") is None or tgt.params.get("in_features") is None):
            return False, f"{src.layer_type} #{src.uid} 또는 {tgt.layer_type} #{tgt.uid} 파라미터 미설정"

        # Linear 연결 검증
        if src.layer_type == "Linear" and tgt.layer_type == "Linear":
            if src.params.get("out_features") != tgt.params.get("in_features"):
                return False, f"{src.layer_type} #{src.uid} → {tgt.layer_type} #{tgt.uid} features 불일치."

        # Conv2d → Flatten 검증
        if src.layer_type.startswith("Conv") and tgt.layer_type == "Flatten":
            out_channels = src.params.get("out_channels")
            if out_channels is None:
                return False, f"{src.layer_type} #{src.uid} out_channels 정보 없음."

        # Flatten → Linear 검증
        if src.layer_type == "Flatten" and tgt.layer_type == "Linear":
            in_features = tgt.params.get("in_features")
            if in_features is None:
                return False, f"{tgt.layer_type} #{tgt.uid} in_features 정보 없음."

    # -------------------------------
    # 3️⃣ 순환 구조(Cycle) 검증
    # -------------------------------
    visited = set()
    rec_stack = set()

    def dfs(uid):
        visited.add(uid)
        rec_stack.add(uid)
        for tgt_uid in layer_items[uid].connections:
            if tgt_uid not in visited:
                if not dfs(tgt_uid):
                    return False
            elif tgt_uid in rec_stack:
                return False
        rec_stack.remove(uid)
        return True

    for uid in uids:
        if uid not in visited:
            if not dfs(uid):
                return False, "순환 구조(Cycle) 발견"

    # -------------------------------
    # 4️⃣ 연결 없는 레이어 검증
    # -------------------------------
    for uid in uids:
        item = layer_items[uid]
        if not item.connections and uid != uids[-1]:
            return False, f"{item.layer_type} #{uid} 연결이 없습니다."

    return True, "검증 통과"
