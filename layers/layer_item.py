from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainterPath, QFontMetricsF, QFont
import os
import json

class LayerItem(QtWidgets.QGraphicsRectItem):
    WIDTH, HEIGHT = 180, 60
    COLOR_MAP_PATH = "data/color_map.json"

    if os.path.exists(COLOR_MAP_PATH):
        with open(COLOR_MAP_PATH, "r", encoding="utf-8") as f:
            COLOR_MAP = json.load(f)
    else:
        COLOR_MAP = {}
    # COLOR_MAP = {
    #     "Linear": "#FFD966",
    #     "Conv2d": "#6FA8DC",
    #     "ReLU": "#93C47D",
    #     "Flatten": "#B4A7D6",
    #     "Dropout": "#F4CCCC",
    #     "BatchNorm2d": "#D9D2E9",
    #     "MaxPool2d": "#FFE599",
    #     "AvgPool2d": "#9FC5E8",
    #     "LSTM": "#EA9999",
    #     "Inception": "#F6B26B",
    #     "ResidualBlock": "#B6D7A8",
    # }

    PLACEHOLDERS = ("Inception", "ResidualBlock", "ResBlock")

    def __init__(self, layer_type, params, uid):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.layer_type = layer_type
        self.params = dict(params) if params is not None else {}
        self.uid = uid
        self.connections = []
        self.expanded = False  # UI/logic에서 확장상태 관리용 플래그

        # 기본 flags
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)

        # appearance
        color = self.COLOR_MAP.get(layer_type, "#CCCCCC")
        self.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        self.setPen(QtGui.QPen(QtGui.QColor("#555555"), 2))

        # text item (we still use a QGraphicsSimpleTextItem for accessibility)
        self.text_item = QtWidgets.QGraphicsSimpleTextItem(self._display_text(), self)
        self.text_item.setBrush(QtGui.QBrush(QtGui.QColor("#222222")))
        font = self.text_item.font()
        font.setPointSize(9)
        font.setBold(False)
        self.text_item.setFont(font)
        self._position_text()

    # ---------- Display helpers ----------
    def _display_text(self):
        """메인에 표시할 텍스트: 'LayerType\\n요약'"""
        short = self._params_short()
        if short:
            return f"{self.layer_type}\n{short}"
        return f"{self.layer_type}"

    def _params_short(self):
        """한두 줄로 요약할 문자열 생성 (플레이스홀더 포함)"""
        # ResidualBlock 요약
        if self.layer_type in ("ResidualBlock", "ResBlock"):
            in_ch = self.params.get("in_channels", "?")
            out_ch = self.params.get("out_channels", "?")
            repeats = self.params.get("repeats", self.params.get("r", 1))
            stride = self.params.get("stride", 1)
            return f"{in_ch}→{out_ch} ×{repeats} s={stride}"

        # Inception 요약
        if self.layer_type == "Inception":
            parts = []
            if "out_1x1" in self.params:
                parts.append(f"1x1:{self.params['out_1x1']}")
            if "out_3x3" in self.params:
                parts.append(f"3x3:{self.params['out_3x3']}")
            if "out_5x5" in self.params:
                parts.append(f"5x5:{self.params['out_5x5']}")
            if "out_pool_proj" in self.params:
                parts.append(f"pool:{self.params['out_pool_proj']}")
            return " ".join(parts) if parts else ", ".join([f"{k}={v}" for k, v in list(self.params.items())[:3]])

        # 일반적인 conv/linear 요약
        if "out_features" in self.params and "in_features" in self.params:
            return f"{self.params['in_features']}→{self.params['out_features']}"
        if "out_channels" in self.params and "in_channels" in self.params:
            k = self.params.get("kernel_size", 3)
            return f"{self.params['in_channels']}→{self.params['out_channels']} k={k}"
        if "p" in self.params:
            return f"p={self.params['p']}"
        if "num_features" in self.params and self.layer_type.startswith("BatchNorm"):
            return f"num={self.params['num_features']}"
        if self.params:
            # show up to two params
            return ", ".join([f"{k}={v}" for k, v in list(self.params.items())[:2]])
        return ""

    def _position_text(self):
        """텍스트 위치 보정 - 제목/요약이 잘 보이도록"""
        # 상단 왼쪽에 위치시키되, 플레이스홀더면 중앙에 크게 표시
        if self.layer_type in self.PLACEHOLDERS:
            # center the label vertically & horizontally
            font = self.text_item.font()
            font.setPointSize(10)
            font.setBold(True)
            self.text_item.setFont(font)
            fm = QFontMetricsF(font)
            text = self.layer_type
            w = fm.width(text)
            h = fm.height()
            rect = self.rect()
            x = rect.left() + (rect.width() - w) / 2
            y = rect.top() + (rect.height() - h) / 2 - 6  # lift slightly
            self.text_item.setPos(x, y)
            # if we also want params under it, create/update a second text (not now)
        else:
            # default small text top-left
            font = self.text_item.font()
            font.setPointSize(9)
            font.setBold(False)
            self.text_item.setFont(font)
            self.text_item.setPos(8, 8)

    # ---------- Context menu & parameter editing ----------
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        edit_action = menu.addAction("Edit Parameters")
        # expand/collapse if module placeholder
        expand_action = None
        collapse_action = None
        if self.layer_type in self.PLACEHOLDERS:
            expand_action = menu.addAction("Expand Module")
            collapse_action = menu.addAction("Collapse Module")
        remove_action = menu.addAction("Remove Layer")

        action = menu.exec_(event.screenPos())
        if action == edit_action:
            self.edit_parameters()
        elif action == expand_action:
            self._request_expand()
        elif action == collapse_action:
            self._request_collapse()
        elif action == remove_action:
            if hasattr(self.scene(), "parent_tab"):
                parent = self.scene().parent_tab
                try:
                    parent.scene.removeItem(self)
                except Exception:
                    pass
                if self.uid in parent.layer_items:
                    del parent.layer_items[self.uid]
                parent.update_sequence_from_positions()

    def edit_parameters(self):
        """파라미터 편집 다이얼로그"""
        from PyQt5.QtWidgets import QInputDialog

        new_params = {}
        for k, v in self.params.items():
            val, ok = QInputDialog.getText(None, f"Edit {self.layer_type}", f"{k}:", text=str(v))
            if ok:
                # 숫자형 변환 시도
                try:
                    if isinstance(v, bool):
                        # keep booleans as-is unless user types True/False
                        if val.lower() in ("true", "false"):
                            new_params[k] = val.lower() == "true"
                            continue
                    if "." not in val:
                        val_cast = int(val)
                    else:
                        val_cast = float(val)
                    new_params[k] = val_cast
                except Exception:
                    new_params[k] = val
            else:
                new_params[k] = v

        # 간단한 key=value 추가 허용
        add_more, ok2 = QInputDialog.getText(None, f"Add param to {self.layer_type}",
                                             "추가 파라미터 (key=value) 또는 빈칸:", text="")
        if ok2 and add_more.strip():
            try:
                k, v = add_more.split("=", 1)
                try:
                    if "." not in v:
                        val_cast = int(v)
                    else:
                        val_cast = float(v)
                    new_params[k.strip()] = val_cast
                except Exception:
                    new_params[k.strip()] = v.strip()
            except Exception:
                pass

        self.params = new_params
        self._refresh_display()

    def _refresh_display(self):
        """텍스트 갱신 및 시각 업데이트"""
        self.text_item.setText(self._display_text())
        self._position_text()
        self.update()

    # ---------- Expand / Collapse request (delegate to parent tab) ----------
    def _request_expand(self):
        """부모(DesignTab)에 확장 동작 요청"""
        parent = getattr(self.scene(), "parent_tab", None)
        if parent is None:
            return
        # try multiple possible method names for compatibility
        for meth in ("expand_module_layer", "expand_layer", "expand_predefined_module", "expand_module"):
            fn = getattr(parent, meth, None)
            if callable(fn):
                try:
                    fn(self)
                    return
                except Exception:
                    pass
        # fallback: show information
        QtWidgets.QMessageBox.information(None, "Expand", "Expand not implemented in parent tab.")

    def _request_collapse(self):
        parent = getattr(self.scene(), "parent_tab", None)
        if parent is None:
            return
        for meth in ("collapse_module_layer", "collapse_layer", "collapse_predefined_module", "collapse_module"):
            fn = getattr(parent, meth, None)
            if callable(fn):
                try:
                    fn(self)
                    return
                except Exception:
                    pass
        QtWidgets.QMessageBox.information(None, "Collapse", "Collapse not implemented in parent tab.")

    def mouseDoubleClickEvent(self, event):
        """더블클릭: 플레이스홀더면 expand/collapse 시도, 아니면 파라미터 편집"""
        if self.layer_type in self.PLACEHOLDERS:
            # toggle: if parent supports inquiry for expanded state, try collapse/expand
            # We try collapse first if it's expanded
            parent = getattr(self.scene(), "parent_tab", None)
            is_expanded = getattr(self, "expanded", False)
            if is_expanded:
                self._request_collapse()
            else:
                self._request_expand()
            # don't swallow entirely — allow default selection behavior
        else:
            # default: open param editor
            self.edit_parameters()
        super().mouseDoubleClickEvent(event)

    # ---------- Painting ----------
    def paint(self, painter, option, widget):
        # base rect
        QGraphicsRectItem.paint(self, painter, option, widget)

        # selection border
        if self.isSelected():
            pen = QtGui.QPen(QtGui.QColor("#333333"), 3)
            painter.setPen(pen)
            painter.drawRect(self.rect())

        rect = self.rect()
        lw = rect.width(); lh = rect.height()
        left = rect.left(); top = rect.top()

        # Placeholder visuals (Inception / Residual) - keep as recognizable iconography
        if self.layer_type == "Inception":
            branch_w = lw * 0.22
            gap = lw * 0.04
            bx = left + lw * 0.06
            by = top + lh * 0.28
            h = lh * 0.4

            base_color = QtGui.QColor(self.COLOR_MAP.get("Inception", "#F6B26B"))
            branch_brush = QtGui.QBrush(base_color.darker(110))
            pen = QtGui.QPen(base_color.darker(140), 1)
            painter.setPen(pen)
            painter.setBrush(branch_brush)

            # draw branches
            r1 = QRectF(bx, by, branch_w, h)
            r2 = QRectF(bx + (branch_w + gap), by, branch_w, h)
            r3 = QRectF(bx + 2*(branch_w + gap), by, branch_w, h)
            r4 = QRectF(bx + 3*(branch_w + gap), by + h*0.15, branch_w*0.9, h*0.7)
            painter.drawRoundedRect(r1, 3, 3)
            painter.drawRoundedRect(r2, 3, 3)
            painter.drawRoundedRect(r3, 3, 3)
            painter.drawRoundedRect(r4, 3, 3)

            # merge arrow
            arrow_pen = QtGui.QPen(QtGui.QColor("#555555"), 1)
            painter.setPen(arrow_pen)
            center_x = left + lw * 0.92
            center_y = top + lh / 2
            #painter.drawLine(r1.right(), center_y, center_x - 8, center_y)
            painter.drawLine(int(r2.right()), int(center_y), int(center_x - 8), int(center_y))

            path = QPainterPath()
            path.moveTo(center_x - 8, center_y - 6)
            path.lineTo(center_x, center_y)
            path.lineTo(center_x - 8, center_y + 6)
            painter.drawPath(path)

            # overlay large label (center)
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            fm = QFontMetricsF(font)
            label = self.layer_type
            tw = fm.width(label)
            th = fm.height()
            painter.setPen(QtGui.QPen(QtGui.QColor("#222222")))
            painter.drawText(int(left + (lw - tw) / 2), int(top + th + 2), label)

        elif self.layer_type in ("ResidualBlock", "ResBlock"):
            block_w = lw * 0.36
            block_h = lh * 0.28
            bx = left + lw * 0.08
            by1 = top + lh * 0.18
            by2 = by1 + block_h + lh * 0.06

            base_color = QtGui.QColor(self.COLOR_MAP.get("ResidualBlock", "#B6D7A8"))
            block_brush = QtGui.QBrush(base_color.darker(105))
            pen = QtGui.QPen(base_color.darker(140), 1)
            painter.setPen(pen)
            painter.setBrush(block_brush)

            r1 = QRectF(bx, by1, block_w, block_h)
            r2 = QRectF(bx, by2, block_w, block_h)
            painter.drawRoundedRect(r1, 3, 3)
            painter.drawRoundedRect(r2, 3, 3)

            # skip connection lines
            arrow_pen = QtGui.QPen(QtGui.QColor("#555555"), 1.5)
            painter.setPen(arrow_pen)
            start_x = bx + block_w + 6
            mid_x = left + lw * 0.9
            y_mid = top + lh * 0.5
            #painter.drawLine(start_x, by1 + block_h/2, mid_x, y_mid)
            painter.drawLine(int(start_x), int(by1 + block_h/2), int(mid_x), int(y_mid))
            #painter.drawLine(start_x, by2 + block_h/2, mid_x, y_mid)
            painter.drawLine(int(start_x), int(by2 + block_h/2), int(mid_x), int(y_mid))
            path = QPainterPath()
            path.moveTo(mid_x - 6, y_mid - 6)
            path.lineTo(mid_x, y_mid)
            path.lineTo(mid_x - 6, y_mid + 6)
            painter.drawPath(path)

            # overlay large label
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            fm = QFontMetricsF(font)
            label = self.layer_type
            tw = fm.width(label)
            painter.setPen(QtGui.QPen(QtGui.QColor("#222222")))
            #painter.drawText(left + (lw - tw) / 2, top + 14, label)
            painter.drawText(int(left + (lw - tw) / 2), int(top + 14), label)


        else:
            # default layers: nothing extra, text_item already handles label
            pass

    # ---------- Position change handling ----------
    def itemChange(self, change, value):
        try:
            pos_change = QtWidgets.QGraphicsItem.ItemPositionChange
            pos_changed = QtWidgets.QGraphicsItem.ItemPositionHasChanged
        except Exception:
            pos_change = QGraphicsRectItem.ItemPositionChange
            pos_changed = QGraphicsRectItem.ItemPositionHasChanged

        if change == pos_change:
            if hasattr(self.scene(), "parent_tab"):
                try:
                    # update edges live while dragging
                    self.scene().parent_tab.update_connections()
                except Exception:
                    pass
        elif change == pos_changed:
            if hasattr(self.scene(), "parent_tab"):
                try:
                    # after moved, refresh sequence
                    self.scene().parent_tab.update_sequence_from_positions()
                except Exception:
                    pass
        return super().itemChange(change, value)
