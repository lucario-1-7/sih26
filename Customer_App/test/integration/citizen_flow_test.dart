// Real end-to-end integration test: exercises the app's actual
// AuthRepository / UserRepository / ChallengeRepository /
// AdministrativeAreaRepository code against the REAL, running Docker backend
// (docker compose up) at http://localhost:8000/api/v1 — no mocked HTTP
// responses anywhere in this file. Requires the backend stack to be up; skip
// (or expect failures) if it is not.
//
// The only thing mocked is the flutter_secure_storage platform channel,
// which has no implementation in the plain Dart test VM — an in-memory map
// stands in for the OS keychain so TokenStorage (real, unmodified) still
// runs exactly as it does in the shipped app.
import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:customer_app/core/networking/api_exception.dart';
import 'package:customer_app/data/repositories/administrative_area_repository.dart';
import 'package:customer_app/data/repositories/auth_repository.dart';
import 'package:customer_app/data/repositories/challenge_repository.dart';
import 'package:customer_app/data/repositories/user_repository.dart';

const _secureStorageChannel = MethodChannel('plugins.it_nomads.com/flutter_secure_storage');

void _mockSecureStorage() {
  final storage = <String, String>{};
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(
    _secureStorageChannel,
    (call) async {
      switch (call.method) {
        case 'write':
          storage[call.arguments['key'] as String] = call.arguments['value'] as String;
          return null;
        case 'read':
          return storage[call.arguments['key'] as String];
        case 'readAll':
          return storage;
        case 'containsKey':
          return storage.containsKey(call.arguments['key'] as String);
        case 'delete':
          storage.remove(call.arguments['key'] as String);
          return null;
        case 'deleteAll':
          storage.clear();
          return null;
        default:
          return null;
      }
    },
  );
}

/// Development-only helper — retrieves the OTP the backend generated, via
/// the dev-only endpoint. This bypasses SMS delivery for the test the same
/// way a developer would manually during local testing; it is never called
/// from any production app code path.
Future<String> _fetchDevOtp(String phone) async {
  final uri = Uri.parse('http://localhost:8000/api/v1/auth/dev/otp').replace(queryParameters: {'phone': phone});
  final response = await HttpClient().getUrl(uri).then((r) => r.close());
  final body = await response.transform(utf8.decoder).join();
  if (response.statusCode != 200) {
    throw StateError('dev OTP endpoint returned ${response.statusCode}: $body');
  }
  return (jsonDecode(body) as Map<String, dynamic>)['code'] as String;
}

Future<bool> _backendIsUp() async {
  try {
    final response = await HttpClient().getUrl(Uri.parse('http://localhost:8000/api/v1/health')).then((r) => r.close());
    return response.statusCode == 200;
  } catch (_) {
    return false;
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  // TestWidgetsFlutterBinding installs an HttpOverrides that fakes every
  // HttpClient to return 400 with no real request — deliberate hermeticity
  // for widget tests. This suite is explicitly NOT hermetic: it exists to
  // prove the real network path against the real Docker backend, so that
  // fake is removed here.
  HttpOverrides.global = null;
  _mockSecureStorage();

  final phone = '+9198765${DateTime.now().millisecondsSinceEpoch.toString().substring(4)}';

  group('citizen flow against the real Docker backend', () {
    late String challengeId;

    setUpAll(() async {
      final up = await _backendIsUp();
      if (!up) {
        fail(
          'Backend is not reachable at http://localhost:8000 — start it with '
          '`docker compose up -d` before running this integration test.',
        );
      }
    });

    test('1. OTP request + dev OTP retrieval + verify -> real JWT session', () async {
      await AuthRepository.instance.requestOtp(phone);
      final code = await _fetchDevOtp(phone);
      await AuthRepository.instance.verifyOtp(phone: phone, code: code);
      expect(await AuthRepository.instance.hasSession(), isTrue);
    });

    test('2. invalid OTP is rejected with 401', () async {
      await AuthRepository.instance.requestOtp(phone);
      expect(
        () => AuthRepository.instance.verifyOtp(phone: phone, code: '000000'),
        throwsA(isA<ApiException>().having((e) => e.isUnauthorized, 'isUnauthorized', isTrue)),
      );
      // Restore a valid session for the remaining tests.
      final code = await _fetchDevOtp(phone);
      await AuthRepository.instance.verifyOtp(phone: phone, code: code);
    });

    test('3. GET /users/me returns the real, freshly auto-created citizen', () async {
      final me = await UserRepository.instance.getMe();
      expect(me.phone, phone);
      expect(me.role, 'citizen');
    });

    test('4. administrative areas list is real backend data', () async {
      final areas = await AdministrativeAreaRepository.instance.list();
      expect(areas, isNotEmpty);
    });

    test('5. create a real challenge, persisted in Postgres', () async {
      final areas = await AdministrativeAreaRepository.instance.list();
      final challenge = await ChallengeRepository.instance.createChallenge(
        title: 'Integration test: broken streetlight',
        description: 'Filed by the Flutter integration test suite against the live backend.',
        administrativeAreaId: areas.first.id,
      );
      challengeId = challenge.id;
      expect(challenge.title, 'Integration test: broken streetlight');
      expect(challenge.status, 'submitted');
    });

    test('6. the created challenge appears in "my challenges"', () async {
      final me = await UserRepository.instance.getMe();
      final mine = await ChallengeRepository.instance.listMyChallenges(me.id);
      expect(mine.any((c) => c.id == challengeId), isTrue);
    });

    test('7. get challenge by id returns the same real row', () async {
      final challenge = await ChallengeRepository.instance.getChallenge(challengeId);
      expect(challenge.id, challengeId);
    });

    test('8. logout clears the session', () async {
      await AuthRepository.instance.logout();
      expect(await AuthRepository.instance.hasSession(), isFalse);
    });

    test('9. protected API rejects the now-unauthenticated client', () async {
      expect(
        () => UserRepository.instance.getMe(),
        throwsA(isA<ApiException>()),
      );
    });

    test('10. logging in again establishes a working session', () async {
      await AuthRepository.instance.requestOtp(phone);
      final code = await _fetchDevOtp(phone);
      await AuthRepository.instance.verifyOtp(phone: phone, code: code);
      final me = await UserRepository.instance.getMe();
      expect(me.phone, phone);
    });
  });
}
