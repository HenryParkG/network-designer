from PyQt5 import QtCore

def validate_network(layer_items, sequence_list):
    items = [sequence_list.item(i) for i in range(sequence_list.count())]
    uids = [it.data(QtCore.Qt.UserRole) for it in items]

    if len(uids) < 2:
        return False, "레이어가 2개 이상이어야 합니다."

    prev_type = None
    prev_out = None
    for uid in uids:
        layer = layer_items[uid]

        if layer.layer_type == "Linear":
            in_f = layer.params.get("in_features")
            out_f = layer.params.get("out_features")

            if prev_type == "Conv2d":
                return False, f"Conv2d → Linear 연결 전에 Flatten이 필요합니다 (Layer#{layer.uid})"

            if prev_type == "Linear" and prev_out is not None:
                if prev_out != in_f:
                    return False, f"Linear 연결 오류: 이전 out_features({prev_out}) != 현재 in_features({in_f})"

            prev_out = out_f
            prev_type = "Linear"

        elif layer.layer_type == "Conv2d":
            in_ch = layer.params.get("in_channels")
            out_ch = layer.params.get("out_channels")

            if prev_type == "Conv2d" and prev_out is not None:
                if prev_out != in_ch:
                    return False, f"Conv2d 연결 오류: 이전 out_channels({prev_out}) != 현재 in_channels({in_ch})"

            prev_out = out_ch
            prev_type = "Conv2d"

        elif layer.layer_type == "Flatten":
            prev_type = "Flatten"
            prev_out = None

        else:
            # ReLU, Dropout, Pool 등은 차원 변화 없음
            prev_type = layer.layer_type

    return True, "연결이 정상입니다."
