# Bluetooth proxy 공통 설정과 추천 기기

blesession을 사용해 HA에서 BLE 장치에 연결하는 통합의 사용자 안내입니다. 로컬 Bluetooth 어댑터와 원격 Bluetooth proxy를 구분하며, 프록시를 쓸 때는 아래 설정을 확인합니다. `blesession`을 설치하는 것만으로 프록시가 설정되지는 않습니다.

설정 안내의 출발점은 [BLE ESL 설치 안내](https://github.com/eigger/hass-ble-esl/blob/main/README.ko.md#설치)이며, 세부 동작은 ESPHome·HA 공식 문서를 기준으로 정리했습니다. 확인일은 **2026-10-17**입니다. 기기·펌웨어 지원은 바뀔 수 있으므로 구매·설정 전 아래 공식 링크에서 다시 확인합니다.

## 추천 기기

유선망을 사용할 수 있다면 Ethernet proxy를 우선 검토합니다. ESPHome은 Wi-Fi와 Bluetooth의 무선 자원 경쟁을 줄이는 방법으로 Ethernet 사용을 안내합니다. 기존에 안정적으로 동작하는 로컬 어댑터가 있으면 교체를 필수로 요구하지 않습니다. [수신 성능 안내](https://esphome.io/components/bluetooth_proxy/#improving-reception-performance)

| 용도 | 추천 후보 | 선택할 때 확인할 점 |
|---|---|---|
| 소형 유선·PoE proxy | Seeed Studio XIAO W5500 Ethernet Adapter **V1.2** | ESP32-S3 기반 해당 제품·리비전인지 확인. 이름이 비슷한 W5500 모듈이나 구형 보드를 같은 제품으로 취급하지 않음 |
| 유선 배치가 어려운 곳 | 공식 Generic ESP32 proxy 대상 보드 | 설치기의 Generic 대상과 실제 칩 일치 확인. C3/S3 등 변형에 Generic 펌웨어를 그대로 사용하지 않음 |

위 후보는 [ESPHome 공식 설치 목록](https://esphome.io/projects/?type=bluetooth)에 있는 구성을 기준으로 선택했습니다. 모든 통합·장치 조합을 실물 검증했다는 의미는 아닙니다. ESPHome 설치 목록은 XIAO W5500 **V1.2만 지원**한다고 명시하며, 구형 보드에는 인터럽트 배선·RF 관련 차이가 있습니다. 판매 사진·리비전과 [Seeed 공식 설정 안내](https://wiki.seeedstudio.com/esphome_xiao_w5500_ethernet_adapter/)를 확인합니다. 가격·재고나 판매 링크를 리포마다 복제하지 않습니다.

### 구매 페이지

- [Seeed Studio XIAO W5500 Ethernet Adapter 구매](https://ko.aliexpress.com/item/1005009310322353.html)
- [추가 구매 페이지 — AliExpress](https://ko.aliexpress.com/item/1005005643544014.html)

XIAO W5500은 위 추천 기준의 V1.2를 선택합니다. 추가 구매 페이지의 제품명·보드 변형은 판매 페이지에서 확인합니다.

## 프록시 준비

1. 정확한 보드에 맞는 공식 proxy 펌웨어를 설치하거나 해당 보드의 ESPHome 설정을 사용합니다. Ethernet 핀·전원·보드 리비전 설정은 제조사/공식 예제를 따릅니다.
2. 장치를 네트워크에 연결하고 HA의 ESPHome 통합에 등록합니다. 프록시가 온라인이며 HA Bluetooth에서 사용할 수 있는 상태인지 확인합니다.
3. 프록시를 BLE 장치 가까이에 배치하고, 장치를 깨우거나 연결 가능한 상태로 만듭니다. 그 뒤 사용하려는 커스텀 통합을 추가합니다.

ESPHome proxy가 HA에 연결되는 절차와 기기별 통합 추가는 별개입니다. 보드 설정 전체는 [공식 설치기](https://esphome.io/projects/?type=bluetooth), HA 연결은 [ESPHome 통합 안내](https://www.home-assistant.io/integrations/esphome/)를 참고합니다.

## ESP32 설정 기준

아래는 BLE ESL 안내와 같은 ESP32용 Bluetooth 설정 **일부분**입니다. 보드·Ethernet/Wi-Fi·API·인증 설정을 포함한 전체 펌웨어 파일이 아닙니다. 기존 설정의 동일 키와 합쳐 사용하고 보드별 GPIO 예제를 섞지 않습니다.

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true
```

두 `active`는 역할이 다릅니다.

- `bluetooth_proxy.active`: HA가 프록시를 통해 **GATT 연결**을 할 수 있게 합니다. blesession으로 읽기·쓰기를 수행할 경로에는 연결 지원이 필요합니다. 광고 수신만 가능한 프록시로 대체하지 않습니다. [ESPHome proxy 설정](https://esphome.io/components/bluetooth_proxy/#configuration)
- `esp32_ble_tracker.scan_parameters.active`: 광고를 받은 뒤 추가 scan response를 요청하는 **스캔 방식**입니다. 발견에 필요한 데이터가 있는지에 따라 정합니다. passive scanning이라는 이유만으로 GATT 연결을 할 수 없다고 설명하지 않습니다. BLE ESL의 시작 설정은 위와 같지만, 다른 기기의 요구까지 같다고 가정하지 않습니다. [Tracker 설정](https://esphome.io/components/esp32_ble_tracker/)

스캔 interval/window는 우선 기본값으로 둡니다. 동시 연결 슬롯은 유한하므로 기기 수와 연결 유지 방식에 맞게 배치하며, 문제가 생겼을 때 무조건 슬롯 수나 재시도를 늘리지 않습니다. [ESPHome 연결·스캔 설명](https://esphome.io/components/bluetooth_proxy/#how-active-connections-work)

## 통합별로 남겨야 하는 안내

공통 문서 링크와 함께 각 README에는 다음 기기 고유 조건을 적습니다.

- 지원 모델·펌웨어, 장치를 깨우는 방법, 페어링/본딩·인증 필요 여부.
- 다른 앱·게이트웨이의 연결을 종료해야 하는 조건과 연결 유지 동작.
- 검증한 로컬 어댑터/proxy 경로, 미검증 환경과 제한사항.
- 통합에 실제로 제공되는 재시도·전송 간격·중복 전송 억제 등의 옵션과 기본값.

BLE ESL의 Retry Count, Debounce, 이미지 전송 규칙을 체중계·프린터 등 모든 기기의 공통 기본값으로 복사하지 않습니다. 이 설정은 프록시 펌웨어 설정과도 구분합니다.

## 연결 문제 확인 순서

| 증상 | 먼저 확인할 내용 |
|---|---|
| 기기가 발견되지 않음 | proxy 온라인 상태, 광고·기기 준비 상태, 거리, 발견에 필요한 스캔 응답 |
| 발견되지만 연결 실패 | 실제 GATT 연결 지원, `bluetooth_proxy.active`, 다른 연결 점유, 인증·본딩 조건 |
| 슬롯 부족·대기 | 장시간 연결을 유지하는 장치와 동시 전송, proxy 배치와 연결 용량 |
| 전송 중 끊김·timeout | 실제 사용한 proxy, 거리·전원·네트워크, 장치 상태, 통합별 전송 조건 |

문제 제보에는 HA·ESPHome·통합 버전, proxy 모델·리비전, 연결 방식, 기기 모델·펌웨어와 오류 단계를 적습니다. 통합이 노출할 때만 blesession의 `failed_stage`, `via`, `via_type`, `rssi`, `paths`, `via_unconfirmed` 등을 함께 확인합니다. 광고를 가장 잘 수신한 proxy와 실제 연결 경로를 혼동하지 않고, 공개 로그에서 주소·계정 등 민감 값은 제거합니다. [blesession 사용 계약](https://github.com/eigger/blesession/blob/main/docs/contract.md)

HA가 지원하는 어댑터·remote adapter 동작은 [HA Bluetooth 문서](https://www.home-assistant.io/integrations/bluetooth/)를 참고합니다.

## 각 README에서 연결하는 예시

```markdown
## Bluetooth 연결

이 통합은 BLE 장치에 연결해 데이터를 읽거나 씁니다.
[Bluetooth proxy 설정과 추천 기기](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md)를 먼저 확인하세요.

기기별 준비·페어링 방법과 확인된 제한사항은 이 통합의 설정 절을 따르세요.
```

개별 README에 공통 설정을 직접 적는 경우도 이 문서의 원본 링크와 확인일을 함께 적고 내용이 달라지지 않도록 관리합니다. 기존 통합의 README 수정은 해당 리포를 이관할 때 진행합니다.
