# Bluetooth proxy 공통 설정과 추천 기기

blesession을 사용해 HA에서 BLE 장치에 연결하는 통합의 사용자 안내입니다. 로컬 Bluetooth 어댑터와 원격 Bluetooth proxy를 구분하며, 프록시를 쓸 때는 아래 설정을 확인합니다. `blesession`을 설치하는 것만으로 프록시가 설정되지는 않습니다.

설정 안내의 출발점은 [BLE ESL 설치 안내](https://github.com/eigger/hass-ble-esl/blob/main/README.ko.md#설치)이며, 세부 동작은 ESPHome·HA 공식 문서를 기준으로 정리했습니다. 확인일은 **2026-10-17**입니다. 기기·펌웨어 지원은 바뀔 수 있으므로 구매·설정 전 아래 공식 링크에서 다시 확인합니다.

## 추천 기기

기본 추천은 **Seeed Studio XIAO W5500 Ethernet Adapter V1.2**입니다. 유선 Ethernet·PoE·외장 안테나 구성을 우선 사용합니다. **USB-A 커넥터가 달린 동글 형태의 기기**를 원한다면 **M5Stack AtomS3U**를 추천합니다.

ESPHome은 Wi-Fi와 Bluetooth의 무선 자원 경쟁을 줄이는 방법으로 Ethernet 사용을 안내합니다. [수신 성능 안내](https://esphome.io/components/bluetooth_proxy/#improving-reception-performance)

| 추천 용도 | 기기 | 특징·설정 기준 | 구매 페이지 |
|---|---|---|---|
| **기본 추천 — 유선·PoE·외장 안테나** | **Seeed Studio XIAO W5500 Ethernet Adapter V1.2** | Ethernet 연결과 PoE 전원, 외장 안테나. 해당 제품의 V1.2 리비전 확인 | [AliExpress 구매](https://ko.aliexpress.com/item/1005009310322353.html) |
| **USB-A 동글 형태** | **M5Stack AtomS3U** | USB-A 커넥터가 달린 소형 기기. AtomS3U용 ESPHome 보드 설정에 Bluetooth proxy 구성 적용 | [AliExpress 구매](https://ko.aliexpress.com/item/1005005643544014.html) |

XIAO W5500은 [ESPHome 공식 설치 목록](https://esphome.io/projects/?type=bluetooth)에서 **V1.2만 지원**한다고 명시합니다. 구형 보드는 인터럽트 배선·RF 관련 차이가 있으므로 구매 옵션과 리비전을 확인합니다. [Seeed 공식 설정 안내](https://wiki.seeedstudio.com/esphome_xiao_w5500_ethernet_adapter/)

AtomS3U는 **USB-A 커넥터가 달린 동글 형태**의 제품입니다. 이 문서에서는 ESPHome Bluetooth proxy로 사용하는 구성을 안내합니다. [M5Stack 제품 문서](https://docs.m5stack.com/en/core/AtomS3U)를 참고하고, Generic ESP32용 펌웨어를 그대로 사용하지 않습니다. 이 기기는 ESPHome 공식 Bluetooth proxy 설치 목록의 대상이 아니라 사용자 구성입니다. 기존 AtomS3U 설정에 `wifi.on_connect`의 `ble.disable` 동작이나 `esp32_improv`가 있으면 삭제한 뒤 `bluetooth_proxy`를 합칩니다. 남겨 두면 Wi-Fi 연결 뒤 BLE가 꺼져 프록시로 동작하지 않습니다.

이 추천은 모든 통합·장치 조합을 실물 검증했다는 의미는 아닙니다. 기존에 안정적으로 동작하는 로컬 어댑터가 있으면 교체가 필수는 아닙니다. 가격·재고나 판매 링크를 리포마다 복제하지 않고 이 공통 문서로 연결합니다.

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

README에는 먼저 기기 깨우기·전원과 상세 문제 해결 링크를 짧게 안내합니다. 통합의 `docs/troubleshooting.md`에는 아래 공통 순서와 실제 모델·펌웨어의 고유 조건을 연결합니다. [BLE ESL 문제 해결 문서](https://github.com/eigger/hass-ble-esl/blob/main/docs/troubleshooting.md)의 **실패 단계 찾기 → 실제 진단 경로 → 제보할 증거** 순서를 참고하되, ESL 전용 센서·액션·Retry Count·Debounce·timeout은 다른 통합에 복사하지 않습니다.

**광고를 발견하거나 스캔에 성공해도 GATT 연결·인증·읽기·쓰기 성공을 의미하지 않습니다.** `esp32_ble_tracker.scan_parameters.active`는 scan response를 요청하는 스캔 방식이며 `bluetooth_proxy.active`는 GATT 연결 지원입니다. passive scan 자체를 연결 불가 원인으로 단정하지 않습니다.

| 증상 / 단계 | 먼저 확인할 내용과 다음 조치 |
|---|---|
| 기기가 발견되지 않음 / `unreachable` | proxy가 HA에서 온라인인지, 기기가 전원·배터리·깨우기 조건을 만족하고 광고하는지 확인합니다. 가까이 이동해 재확인하고 해당 모델에 필요한 scan response·광고 주기를 확인합니다. |
| 발견되지만 연결 실패 / `connect` | 실제 연결 가능한 경로와 `bluetooth_proxy.active`, 타 앱·게이트웨이의 연결 점유를 확인합니다. 모델 안내에 따라 다른 앱 연결을 종료하고 다시 시도합니다. 페어링·본딩·인증 조건은 기기별 문서를 따릅니다. |
| 슬롯 부족 / `connect.no_slot` | 동시 전송과 오래 유지하는 연결을 확인합니다. 불필요한 연결을 종료하거나 부하를 나누고 필요하면 proxy를 추가합니다. 슬롯 수·재시도를 무조건 늘리지 않습니다. |
| 연결 직후 세션·인증 실패 | 실제 서비스/characteristic·모델·펌웨어가 통합의 지원 대상인지 확인합니다. 깨우기·본딩·인증키·다른 앱 연결 조건을 따릅니다. 인증 거부나 잘못된 모델을 반복 재시도로 해결하려 하지 않습니다. |
| 전송 중 끊김 / `link_lost` | 실패 당시 실제 사용한 proxy·거리·기기 배터리·proxy 전원·네트워크/재시작 여부를 확인합니다. 연결이 복구되고 기기가 준비된 뒤 통합이 지원하는 재시도/재연결 방법을 사용합니다. 반복 전송은 기기 부작용을 확인한 뒤 수행합니다. |
| 쓰기가 반환되지 않음 / `write_timeout` | adapter/proxy의 응답·연결 부하·전원·네트워크를 확인합니다. 계속 응답하지 않으면 해당 경로를 복구한 뒤 재시도합니다. 단순 장치 응답 대기 timeout과 같은 원인으로 단정하지 않습니다. |
| 전송 후 완료 확인 실패 | 기기의 실제 상태와 통합의 완료/응답 규칙을 확인합니다. 전체 작업을 다시 보내기 전에 기기가 이미 명령을 수행했는지 확인하고 중복 동작의 영향을 고려합니다. |
| 간헐적 실패 후 성공 | 최근 성공만 보지 말고 실패 당시 기록과 실제 경로를 확인합니다. 특정 proxy·시간·부하에 집중되는지 비교합니다. |

재시도 횟수·backoff·연결 유지·본딩·전송 간격은 **각 통합의 정책**입니다. blesession 설치만으로 자동 재연결이나 모든 오류의 재시도를 보장하지 않습니다. 해당 통합에서 실제 사용하는 blesession 버전과 오류 매핑을 기준으로 안내하며 고정된 공통 timeout이나 RSSI 임계값을 강제하지 않습니다.

### 실제 진단 경로와 제보 정보

- 기기/통합 페이지에서 제공하는 진단 다운로드·상태 속성·최근 오류·자동화 trace를 **실제로 제공할 때만** 안내합니다. 없던 진단 센서나 통합 옵션을 문서 때문에 있다고 쓰지 않습니다.
- 노출되는 경우 `failed_stage`, `failed_detail`, `likely_cause_key`, `error`, 작업 시각, `via`, `via_type`, `rssi`, `paths`, `via_unconfirmed`를 확인합니다. 단계와 기기별 오류 이름의 매핑을 해당 통합 문서에 적습니다. 특정 단계/센서가 모든 통합에 존재한다고 가정하지 않습니다.
- 광고를 가장 잘 수신한 proxy와 실제 연결 경로를 구분합니다. 실제 경로가 확인되지 않았으면 추정값임을 명시합니다. RSSI·경로 개수만으로 원인을 확정하지 않습니다.
- HA·통합·ESPHome·blesession 버전(확인 가능한 경우), proxy 모델·리비전과 연결 방식, 기기 모델·펌웨어, 실패 시각/단계와 재현 절차를 제보합니다. 여러 번 시도했다면 마지막 성공과 실패를 구분합니다.
- 진단 파일도 공개 전에 확인하고 MAC/Bluetooth 주소·계정·인증키·토큰·내부 주소·개인 데이터 등 민감 값을 제거합니다. 디버그 로그는 통합이 안내하는 실제 logger 이름으로 필요한 재현 구간만 수집하고 수집 후 끕니다. 예시의 다른 domain logger를 그대로 복사하지 않습니다.

위 오류 용어와 재시도·진단 경계는 [blesession 사용 계약](https://github.com/eigger/blesession/blob/main/docs/contract.md)과 [통합 채택 안내](https://github.com/eigger/blesession/blob/main/docs/adopting.md)를 기준으로 합니다. HA가 지원하는 어댑터·remote adapter 동작은 [HA Bluetooth 문서](https://www.home-assistant.io/integrations/bluetooth/)를 참고합니다.

## 각 README에서 연결하는 예시

```markdown
## Bluetooth 연결

이 통합은 BLE 장치에 연결해 데이터를 읽거나 씁니다.
[Bluetooth proxy 설정과 추천 기기](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md)를 먼저 확인하세요.

기기를 깨우고 다른 앱의 연결을 종료하는 등 해당 모델의 준비 조건을 확인하세요.
문제가 계속되면 이 통합에서 제공하는 상세 문제 해결 문서를 확인하고, 별도 문서가 없으면
[공통 연결 문제 확인 순서](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md#연결-문제-확인-순서)와 해당 통합의 기기별 조건을 함께 확인하세요.
```

개별 README에 공통 설정을 직접 적는 경우도 이 문서의 원본 링크와 확인일을 함께 적고 내용이 달라지지 않도록 관리합니다. 기존 통합의 README 수정은 해당 리포를 이관할 때 진행합니다.
