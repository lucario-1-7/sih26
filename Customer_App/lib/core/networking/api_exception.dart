/// Thrown for every non-2xx response and every network-level failure.
/// Screens should catch this (never a raw [Exception]/[SocketException]) and
/// use [userMessage] — never [detail]/[code] straight from the wire without
/// going through it, so a backend error string is never shown verbatim.
class ApiException implements Exception {
  final int? statusCode;
  final String code;
  final String detail;
  final String? requestId;

  const ApiException({required this.statusCode, required this.code, required this.detail, this.requestId});

  factory ApiException.network() =>
      const ApiException(statusCode: null, code: 'NETWORK_ERROR', detail: 'Could not reach the server.');

  factory ApiException.timeout() =>
      const ApiException(statusCode: null, code: 'TIMEOUT', detail: 'The request took too long.');

  factory ApiException.malformedResponse() => const ApiException(
        statusCode: null,
        code: 'MALFORMED_RESPONSE',
        detail: 'The server sent an unexpected response.',
      );

  bool get isUnauthorized => statusCode == 401;
  bool get isForbidden => statusCode == 403;
  bool get isNotFound => statusCode == 404;
  bool get isConflict => statusCode == 409;
  bool get isValidation => statusCode == 422;
  bool get isServiceUnavailable => statusCode == 503;
  bool get isServerError => statusCode != null && statusCode! >= 500;

  /// A single, safe-to-display message — never a raw backend stack trace or
  /// internal detail. Falls back to the backend's own `detail` for expected
  /// 4xx cases (validation, not-found, conflict), where it's meant to be shown.
  String get userMessage {
    switch (code) {
      case 'NETWORK_ERROR':
        return 'No internet connection. Please check your network and try again.';
      case 'TIMEOUT':
        return 'The server is taking too long to respond. Please try again.';
      case 'MALFORMED_RESPONSE':
        return 'Something went wrong on our end. Please try again shortly.';
      case 'UNAUTHORIZED':
        return 'Your session has expired. Please log in again.';
      case 'FORBIDDEN':
        return 'You do not have permission to do that.';
    }
    if (isServiceUnavailable) return 'The service is temporarily unavailable. Please try again shortly.';
    if (isServerError) return 'Something went wrong on our end. Please try again shortly.';
    return detail.isNotEmpty ? detail : 'Something went wrong. Please try again.';
  }

  @override
  String toString() => 'ApiException($statusCode, $code, $detail)';
}
