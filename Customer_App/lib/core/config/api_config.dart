/// Single source of truth for the backend base URL.
///
/// Override at build/run time with:
///   flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000/api/v1
///
/// Without an override, every platform — including Android — targets
/// `localhost:8000`. On a real Android device (not the emulator) this
/// requires forwarding the device's own localhost:8000 to the host machine
/// over the USB cable, once per `adb` session:
///   adb reverse tcp:8000 tcp:8000
/// The Android emulator needs the same forward — plain `adb reverse` also
/// works against it, it just isn't done automatically here anymore (it
/// used to default to the emulator-only 10.0.2.2 alias, which only exists
/// inside the emulator's own virtual network and is unreachable from real
/// hardware).
class ApiConfig {
  ApiConfig._();

  static const String _override = String.fromEnvironment('API_BASE_URL');

  static String get baseUrl {
    if (_override.isNotEmpty) return _override;
    return 'http://localhost:8000/api/v1';
  }

  static const Duration requestTimeout = Duration(seconds: 15);
}

/// PRESENTATION-ONLY, hardcoded on for every build: the real OTP/phone
/// login path is unreachable until this is reverted to a build-time flag.
/// The backend independently re-checks its own DEMO_MODE (404s the demo
/// endpoint otherwise), so this flag alone can never grant access on a
/// backend that isn't also configured for demo mode.
class DemoConfig {
  DemoConfig._();

  static const bool enabled = true;
}
