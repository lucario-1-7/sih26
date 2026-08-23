import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../storage/token_storage.dart';
import 'api_exception.dart';

/// Thin, centralized HTTP layer. Every screen/repository goes through this —
/// no raw `http.get`/`http.post` calls scattered across the app, no
/// hardcoded URLs, no manually-attached Authorization headers.
///
/// Handles: base URL, JSON encode/decode, bearer auth header, request
/// timeout, and a single-flight refresh-and-retry on 401 (de-duplicated
/// across concurrent requests the same way the organizational web client
/// does it) — a caller only ever sees the *final* outcome after a refresh
/// attempt, never a raw 401 that was actually recoverable.
class ApiClient {
  ApiClient._();
  static final ApiClient instance = ApiClient._();

  final http.Client _http = http.Client();

  /// Set once by AuthRepository at app start. Attempts a token refresh and
  /// returns whether it succeeded. Kept as an injected callback (rather than
  /// importing AuthRepository directly) to avoid a networking↔auth import cycle.
  Future<bool> Function()? onUnauthorized;

  Future<Map<String, dynamic>?> get(String path, {Map<String, String>? query}) =>
      _request('GET', path, query: query);

  Future<Map<String, dynamic>?> post(String path, {Map<String, dynamic>? body, bool auth = true}) =>
      _request('POST', path, body: body, auth: auth);

  Future<Map<String, dynamic>?> patch(String path, {Map<String, dynamic>? body}) =>
      _request('PATCH', path, body: body);

  Future<Map<String, dynamic>?> _request(
    String method,
    String path, {
    Map<String, String>? query,
    Map<String, dynamic>? body,
    bool auth = true,
    bool isRetry = false,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$path').replace(queryParameters: query);
    final headers = <String, String>{'Content-Type': 'application/json'};

    if (auth) {
      final token = await TokenStorage.getAccessToken();
      if (token != null) headers['Authorization'] = 'Bearer $token';
    }

    http.Response response;
    try {
      response = await _send(method, uri, headers, body).timeout(ApiConfig.requestTimeout);
    } on TimeoutException {
      throw ApiException.timeout();
    } on SocketException {
      throw ApiException.network();
    } on http.ClientException {
      throw ApiException.network();
    }

    if (response.statusCode == 401 && auth && !isRetry && onUnauthorized != null) {
      final refreshed = await onUnauthorized!();
      if (refreshed) {
        return _request(method, path, query: query, body: body, auth: auth, isRetry: true);
      }
    }

    return _parse(response);
  }

  Future<http.Response> _send(
    String method,
    Uri uri,
    Map<String, String> headers,
    Map<String, dynamic>? body,
  ) {
    final encodedBody = body != null ? jsonEncode(body) : null;
    switch (method) {
      case 'GET':
        return _http.get(uri, headers: headers);
      case 'POST':
        return _http.post(uri, headers: headers, body: encodedBody);
      case 'PATCH':
        return _http.patch(uri, headers: headers, body: encodedBody);
      default:
        throw ArgumentError('Unsupported method: $method');
    }
  }

  Map<String, dynamic>? _parse(http.Response response) {
    Map<String, dynamic>? payload;
    if (response.body.isNotEmpty) {
      try {
        final decoded = jsonDecode(response.body);
        payload = decoded is Map<String, dynamic> ? decoded : null;
      } on FormatException {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          throw ApiException.malformedResponse();
        }
        payload = null;
      }
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return payload;
    }

    throw ApiException(
      statusCode: response.statusCode,
      code: (payload?['code'] as String?) ?? _codeForStatus(response.statusCode),
      detail: (payload?['detail'] as String?) ?? 'Request failed with status ${response.statusCode}',
      requestId: payload?['request_id'] as String?,
    );
  }

  String _codeForStatus(int status) {
    switch (status) {
      case 401:
        return 'UNAUTHORIZED';
      case 403:
        return 'FORBIDDEN';
      case 404:
        return 'NOT_FOUND';
      case 409:
        return 'CONFLICT';
      case 422:
        return 'VALIDATION_ERROR';
      case 503:
        return 'ML_SERVICE_UNAVAILABLE';
      default:
        return 'UNKNOWN_ERROR';
    }
  }
}
