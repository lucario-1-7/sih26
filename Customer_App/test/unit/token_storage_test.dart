import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:customer_app/core/storage/token_storage.dart';

const _channel = MethodChannel('plugins.it_nomads.com/flutter_secure_storage');

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late Map<String, String> backing;

  setUp(() {
    backing = <String, String>{};
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(_channel, (call) async {
      switch (call.method) {
        case 'write':
          backing[call.arguments['key'] as String] = call.arguments['value'] as String;
          return null;
        case 'read':
          return backing[call.arguments['key'] as String];
        case 'delete':
          backing.remove(call.arguments['key'] as String);
          return null;
        case 'deleteAll':
          backing.clear();
          return null;
        default:
          return null;
      }
    });
  });

  group('TokenStorage', () {
    test('has no session before anything is saved', () async {
      expect(await TokenStorage.hasSession(), isFalse);
    });

    test('save then read round-trips both tokens', () async {
      await TokenStorage.save(accessToken: 'a1', refreshToken: 'r1');
      expect(await TokenStorage.getAccessToken(), 'a1');
      expect(await TokenStorage.getRefreshToken(), 'r1');
      expect(await TokenStorage.hasSession(), isTrue);
    });

    test('updateAccessToken replaces only the access token', () async {
      await TokenStorage.save(accessToken: 'a1', refreshToken: 'r1');
      await TokenStorage.updateAccessToken('a2');
      expect(await TokenStorage.getAccessToken(), 'a2');
      expect(await TokenStorage.getRefreshToken(), 'r1');
    });

    test('clear removes both tokens and ends the session', () async {
      await TokenStorage.save(accessToken: 'a1', refreshToken: 'r1');
      await TokenStorage.clear();
      expect(await TokenStorage.getAccessToken(), isNull);
      expect(await TokenStorage.getRefreshToken(), isNull);
      expect(await TokenStorage.hasSession(), isFalse);
    });
  });
}
