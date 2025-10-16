from PyQt5 import QtCore

def validate_network(layer_items, sequence_list):
    """
    레이어 연결 + 순서 + 크기 검증
    """
    if sequence_list.count() == 0:
        return False, "레이어가 없습니다."

    uids = [sequence_list.item(i).data(QtCore.Qt.UserRole) for i in range(sequence_list.count())]

    # 1. 연결 존재 여부
    for uid in uids:
        item = layer_items.get(uid)
        if not item:
            return False, f"레이어 UID {uid}가 없습니다."
        for tgt_uid in item.connections:
            if tgt_uid not in layer_items:
                return False, f"{item.layer_type} #{uid} 연결 대상 UID {tgt_uid}가 존재하지 않습니다."

    # 2. 논리적 연결 검증 (간단 예)
    for uid in uids[:-1]:
        src = layer_items[uid]
        tgt_uid = src.connections[0] if src.connections else None
        if tgt_uid is None:
            return False, f"{src.layer_type} #{src.uid} 연결이 없습니다."
        tgt = layer_items[tgt_uid]

        # 예: Linear층 앞뒤 in/out features 체크
        if src.layer_type == "Linear" and tgt.layer_type == "Linear":
            if src.params.get("out_features") != tgt.params.get("in_features"):
                return False, f"{src.layer_type} #{src.uid} → {tgt.layer_type} #{tgt.uid} features 불일치."

    # 3. 순환 체크 (DAG)
    visited = set()
    def dfs(uid, path):
        if uid in path:
            return False
        path.add(uid)
        item = layer_items[uid]
        for tgt_uid in item.connections:
            if not dfs(tgt_uid, path):
                return False
        path.remove(uid)
        return True

    for uid in uids:
        if not dfs(uid, set()):
            return False, "순환 구조 발견"

    return True, "검증 통과"
