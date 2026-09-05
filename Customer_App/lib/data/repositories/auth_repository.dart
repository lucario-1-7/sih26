import '../../core/networking/api_client.dart';
import '../../core/storage/token_storage.dart';
import '../models/auth_tokens.dart';

/// Owns the real SocioSolve OTP auth flow — this is the app's only authentication
/// path. There is no separate/parallel login system and no bypass: every
/// screen that needs a session goes through here.
class AuthRepository {
  AuthRepository._internal() {
    ApiClient.instance.onUnauthorized = refreshSession;
  }

  static final AuthRepository instance = AuthRepository._internal();

  final ApiClient _client = ApiClient.instance;

  /// phone must already be in the backend's expected format, e.g. "+919876543210".
  Future<void> requestOtp(String phone) async {
    await _client.post('/auth/otp/request', body: {'phone': phone}, auth: false);
  }

  Future<void> verifyOtp({required String phone, required String code}) async {
    final json = await _client.post('/auth/otp/verify', body: {'phone': phone, 'code': code}, auth: false);
    final tokens = AuthTokens.fromJson(json!);
    await TokenStorage.save(accessToken: tokens.accessToken, refreshToken: tokens.refreshToken);
  }

  /// PRESENTATION-ONLY. Bypasses the OTP challenge entirely — issues a real
  /// SocioSolve session for a real, backend-persisted demo citizen. Only ever
  /// called from a UI path gated by DemoConfig.enabled, and only ever
  /// succeeds if the backend's own DEMO_MODE is also explicitly enabled
  /// (404 otherwise) — this flag alone can never grant access.
  Future<void> demoLogin({String persona = 'citizen'}) async {
    final json = await _client.post('/auth/demo/login', body: {'persona': persona}, auth: false);
    final tokens = AuthTokens.fromJson(json!);
    await TokenStorage.save(accessToken: tokens.accessToken, refreshToken: tokens.refreshToken);
  }

  /// Single-flight refresh, invoked by ApiClient on a 401. Returns whether the
  /// caller's original request should be retried.
  Future<bool> refreshSession() async {
    final refreshToken = await TokenStorage.getRefreshToken();
    if (refreshToken == null) return false;
    try {
      final json = await _client.post('/auth/refresh', body: {'refresh_token': refreshToken}, auth: false);
      final tokens = AuthTokens.fromJson(json!);
      await TokenStorage.updateAccessToken(tokens.accessToken);
      return true;
    } catch (_) {
      await TokenStorage.clear();
      return false;
    }
  }

  Future<bool> hasSession() => TokenStorage.hasSession();

  Future<void> logout() async {
    final refreshToken = await TokenStorage.getRefreshToken();
    if (refreshToken != null) {
      try {
        await _client.post('/auth/logout', body: {'refresh_token': refreshToken});
      } catch (_) {
        // Best-effort server-side revocation — the local session is cleared
        // either way so the device can never be treated as logged in again.
      }
    }
    await TokenStorage.clear();
  }
}
