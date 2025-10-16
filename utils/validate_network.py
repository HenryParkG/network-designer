
from PyQt5 import QtCore

def validate_network(layer_items, sequence_list):
    """
    True/False 반환. 잘못된 경우 메시지 포함
    """
    if sequence_list.count() == 0:
        return False, "레이어가 없습니다."

    uids = [sequence_list.item(i).data(QtCore.Qt.UserRole) for i in range(sequence_list.count())]
    
    # 연결 검증
    for uid in uids:
        item = layer_items.get(uid)
        if not item:
            return False, f"레이어 UID {uid}가 없습니다."
        for tgt_uid in item.connections:
            if tgt_uid not in layer_items:
                return False, f"{item.layer_type} #{uid} 연결 대상 UID {tgt_uid}가 존재하지 않습니다."
    
    # 순서 검증 (간단하게)
    for i in range(len(uids)-1):
        src = layer_items[uids[i]]
        tgt = layer_items[uids[i+1]]
        if tgt.uid not in src.connections:
            return False, f"{src.layer_type} #{src.uid}와 {tgt.layer_type} #{tgt.uid}가 연결되지 않았습니다."
    
    return True, "검증 통과"
