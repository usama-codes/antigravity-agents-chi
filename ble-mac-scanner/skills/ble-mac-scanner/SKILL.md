---
name: ble-mac-scanner
description: >
  Use this skill when the user provides a Bluetooth MAC address and asks
  to scan for it, track a device, connect to a watch, read health data
  (heart rate, blood oxygen, blood pressure), or render readings in the Flutter app.
  Activates whenever the prompt contains a MAC address or refers to watch connectivity.
---

# BLE MAC & Watch Scanner Skill

## Goal
Accept a target MAC address, persist it in the ViewModel, scan/connect to the device, and:
1. For generic BLE devices: render its details (RSSI, MAC) in a match card.
2. For BPW1 watches: establish a connection, send measurement requests using the custom BPW1 protocol, decode incoming notifications, and render real-time heart rate, blood oxygen, and blood pressure metrics in the health dashboard.

## Context and Architecture
- **Target MAC address**: Provided in format `AA:BB:CC:DD:EE:FF`.
- **Flutter project**: MVVM architecture.
- **Relevant files**:
  - `lib/features/bluetooth_scanner/viewmodel/bluetooth_scanner_viewmodel.dart`
  - `lib/features/bluetooth_scanner/view/bluetooth_scanner_view.dart`
  - `lib/features/watch_scanner/services/ble_service.dart`

## BPW1 BLE Protocol Specification

### 1. Packet Layout (Big-Endian)
| Byte Index | Field | Description |
|---|---|---|
| 0 | Protocol Identifier | Always `0xE0` |
| 1-2 | Length | 2 Bytes: 7 bits reserved (0x0), 9 bits length (value is total packet size - 4) |
| 3 | Sumcheck | 1 Byte: Last 8 bits of the sum of all bytes in the packet except this sumcheck byte |
| 4 | CMD | 1 Byte: Command identifier |
| 5 | Version | 1 Byte: Protocol version (normally `0x00`) |
| 6 | KEY | 1 Byte: Subcommand identifier |
| 7-8 | KeyValueLen | 2 Bytes: 7 bits reserved (0x0), 9 bits length of KeyValue |
| 9+ | KeyValue | N Bytes: Command/response payload |

### 2. Output commands to write (to Characteristic `81eea003-e735-49ec-8a11-7e32cae1e14e`)
- **Request Heart Rate (CMD: 0x06, KEY: 0x04)**:
  `E0 00 0A F0 06 00 04 00 01 01`
- **Request Blood Pressure (CMD: 0x06, KEY: 0x05)**:
  `E0 00 0A F1 06 00 05 00 01 01`
- **Request Blood Oxygen (CMD: 0x06, KEY: 0x06)**:
  `E0 00 0A F2 06 00 06 00 01 01`

### 3. Incoming notifications to decode (from Characteristic `81eea002-e735-49ec-8a11-7e32cae1e14e`)
- **Heart Rate (CMD: 0x03, KEY: 0x00)**:
  - Header (4 Bytes): `Timestamp (2 Bytes)`, `Reserved (1 Byte)`, `Count N (1 Byte)`.
  - Data item (8 Bytes each): `Seconds from midnight (4 Bytes)`, `Type (1 Byte)`, `Reserved (2 Bytes)`, `Heart rate value (1 Byte, bpm)`.
- **Blood Pressure (CMD: 0x03, KEY: 0x01)**:
  - Header (4 Bytes): `Timestamp (2 Bytes)`, `Reserved (1 Byte)`, `Count N (1 Byte)`.
  - Data item (8 Bytes each): `Seconds from midnight (4 Bytes)`, `Type (1 Byte)`, `Reserved (1 Byte)`, `Systolic/High value (1 Byte, mmHg)`, `Diastolic/Low value (1 Byte, mmHg)`.
- **Blood Oxygen (CMD: 0x03, KEY: 0x02)**:
  - Header (4 Bytes): `Timestamp (2 Bytes)`, `Reserved (1 Byte)`, `Count N (1 Byte)`.
  - Data item (8 Bytes each): `Seconds from midnight (4 Bytes)`, `Type (1 Byte)`, `Reserved (2 Bytes)`, `Blood oxygen value (1 Byte, %)`.

## Instructions

### Step 1 — Validate the MAC address
- Extract the MAC address using pattern `([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}`.
- Normalise to uppercase with colons.

### Step 2 — Update state and trigger scan/connect
- Pass the MAC to the ViewModel via `setTargetMac()`.
- Call `startScan()` or `connectToDevice()`.

### Step 3 — Send measurements (Watch mode)
- Once connected, call `requestMeasurement(measurementType)` which sends the appropriate command packet to characteristic `A003`.
- Read notification bytes on characteristic `A002` and decode using the parser.

### Step 4 — Render the results
- Bind UI components to the ViewModel:
  - Show RSSI/Generic match card for general beacons.
  - Show glassmorphic gauges, history graphs, and trigger buttons for watches.
