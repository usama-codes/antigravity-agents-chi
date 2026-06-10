// scan_result_injector.dart
// PostToolUse hook — runs after every run_command tool call.
// Reads the tool output JSON from stdin. If it detects a BLE scan result
// containing a matched MAC address, it writes structured feedback to stdout
// so the agent knows to update the UI state in the ViewModel.

import 'dart:convert';
import 'dart:io';

void main() async {
  // ── Read tool output JSON from stdin ──────────────────────────────────────
  final raw = await stdin.transform(utf8.decoder).join();

  Map<String, dynamic> input;
  try {
    input = jsonDecode(raw) as Map<String, dynamic>;
  } catch (_) {
    // Not JSON — pass through silently.
    stdout.write(jsonEncode({'continue': true}));
    return;
  }

  final toolOutput = input['toolCall']?['output']?.toString() ?? '';

  // ── Detect a BLE scan result payload ─────────────────────────────────────
  // The ViewModel prints a structured line when a match is found:
  //   BLE_MATCH: {"found":true,"mac":"AA:BB:CC:DD:EE:FF","rssi":-72,"localName":"MyDevice"}
  final matchLine = RegExp(r'BLE_MATCH:\s*(\{.*\})').firstMatch(toolOutput);

  if (matchLine != null) {
    Map<String, dynamic> result;
    try {
      result = jsonDecode(matchLine.group(1)!) as Map<String, dynamic>;
    } catch (_) {
      stdout.write(jsonEncode({'continue': true}));
      return;
    }

    if (result['found'] == true) {
      final mac = result['mac'] ?? 'Unknown';
      final rssi = result['rssi'] ?? 'N/A';
      final name = result['localName'] ?? 'Unnamed device';

      // Inject a context message back to the agent so it can confirm to the user.
      stdout.write(jsonEncode({
        'continue': true,
        'systemMessage':
            'BLE scan completed. Device found — MAC: $mac, Name: $name, RSSI: $rssi dBm. '
            'The match card has been rendered on BluetoothScannerView. '
            'Inform the user that the device was detected successfully.',
      }));
      return;
    }
  }

  // ── Detect a not-found timeout ────────────────────────────────────────────
  if (toolOutput.contains('BLE_TIMEOUT')) {
    stdout.write(jsonEncode({
      'continue': true,
      'systemMessage':
          'BLE scan timed out. The target device was not found within 15 seconds. '
          'Inform the user and suggest verifying the MAC address or moving closer to the device.',
    }));
    return;
  }

  // Default — no action needed.
  stdout.write(jsonEncode({'continue': true}));
}