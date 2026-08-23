import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Encrypted, on-device storage for the auth token pair — Android Keystore /
/// iOS Keychain under the hood via flutter_secure_storage, never SharedPreferences
/// or a plain file. Tokens never touch application logs.
class TokenStorage {
  TokenStorage._();

  static const _storage = FlutterSecureStorage();
  static const _accessKey = 'sahyog_access_token';
  static const _refreshKey = 'sahyog_refresh_token';

  static Future<void> save({required String accessToken, required String refreshToken}) async {
    await _storage.write(key: _accessKey, value: accessToken);
    await _storage.write(key: _refreshKey, value: refreshToken);
  }

  static Future<String?> getAccessToken() => _storage.read(key: _accessKey);
  static Future<String?> getRefreshToken() => _storage.read(key: _refreshKey);

  static Future<void> updateAccessToken(String accessToken) async {
    await _storage.write(key: _accessKey, value: accessToken);
  }

  static Future<bool> hasSession() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  static Future<void> clear() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }
}
