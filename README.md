# network-designer


Network Designer는 그래픽 기반으로 신경망 구조를 설계하고, PyTorch 코드로 바로 변환할 수 있는 데스크톱 애플리케이션입니다.  
사용자는 드래그 앤 드롭 방식으로 레이어를 캔버스에 배치하고, 레이어 간 연결을 시각적으로 구성할 수 있습니다.  
<img width="1396" height="827" alt="image" src="https://github.com/user-attachments/assets/9ba67c87-a915-4ab9-ae3c-3fcc5a192914" />


이 프로젝트의 주요 목적은 다음과 같습니다:

- **직관적인 신경망 설계**: GUI를 통해 레이어 추가, 삭제, 연결을 시각적으로 처리
- **자동 코드 생성**: 구성한 신경망 구조를 기반으로 PyTorch 코드 자동 생성
- **구조 검증**: 레이어 연결 논리를 검사하여 오류를 사전에 방지
- **저장 및 불러오기**: JSON 파일로 설계 상태 저장 및 불러오기 지원


# network-designer 프로젝트 구조

## 📁 layers

신경망 레이어 관련 UI 및 로직을 담당

* **layer_item.py**

  * 그래픽에서 보여지는 레이어 박스(`QGraphicsRectItem`) 정의
  * Layer 타입, 파라미터, UID 관리
  * 드래그 이동, 선택, 우클릭 파라미터 편집 구현
  * `itemChange()`에서 박스 이동 시 Sequence 및 Edge 갱신

* **edge_item.py**

  * 레이어 간 연결선(`QGraphicsLineItem`) 정의
  * source/target LayerItem 참조
  * `update_position()`로 Edge 위치 자동 갱신
  * Z값 설정으로 선이 LayerItem 뒤로 표시

* **layers_config.py**

  * 레이어 타입별 기본 파라미터 템플릿 정의
  * 예: Linear, Conv2d, ReLU, Flatten 등

---

## 📁 canvas

그래픽 캔버스 관련 UI

* **canvas_view.py**

  * `QGraphicsView` 상속
  * Canvas에 레이어 박스 표시, 드래그 앤 드롭 처리
  * Palette에서 레이어 드래그 → 캔버스에 생성

---

## 📁 palette

레이어 선택 UI

* **palette_widget.py**

  * 사용자가 추가할 레이어를 목록으로 보여주는 위젯(`QListWidget`)
  * 드래그 앤 드롭 지원

---

## 📁 utils

도움 기능 및 데이터 관리

* **export_utils.py**

  * 현재 DesignerWindow 상태를 기반으로 **PyTorch 코드 생성 및 파일 저장**
  * Linear, Conv2d 등 레이어별 코드를 순서대로 작성

* **save_load_utils.py**

  * JSON 파일로 DesignerWindow 상태 저장 및 불러오기
  * 레이어 종류, 파라미터, 위치, 연결 정보 포함

* **validate_network.py**

  * 신경망 연결 구조 논리 검사
  * 체크 항목:

    * Linear 연결 시 in/out features 일치 여부
    * Conv2d → Linear 시 Flatten 존재 여부
    * Conv2d → Conv2d 시 채널 일치 여부
    * 최소 2개 레이어 존재 여부
  * 오류 시 메시지 반환 → Connect Layers 버튼에서 팝업 표시

---

## 🏠 DesignerWindow

메인 UI 및 로직

* **designer_window.py**

  * 전체 UI 구성 (Palette, Canvas, Sequence 리스트, 버튼)
  * 레이어 추가/삭제, 박스 자동 배치
  * Sequence 리스트와 Canvas 동기화
  * Connect Layers 기능 + Validation 호출
  * Save / Load / Export 버튼 처리

---

### ✅ 핵심 동작 흐름

1. Palette에서 레이어 드래그 → Canvas에 박스 생성
2. 박스 이동 → Sequence 리스트 자동 갱신 → Edge 자동 갱신
3. Connect Layers 버튼 → connections 생성 + validate_network 호출
4. 논리 오류 시 팝업, 정상 시 Edge 생성 및 Save/Export 버튼 활성화
5. Save → JSON 저장, Load → JSON 불러오기, Export → PyTorch 코드 생성
