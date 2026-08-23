import 'package:flutter_test/flutter_test.dart';
import 'package:customer_app/core/networking/api_exception.dart';

void main() {
  group('ApiException', () {
    test('classifies status codes correctly', () {
      const unauthorized = ApiException(statusCode: 401, code: 'UNAUTHORIZED', detail: 'x');
      expect(unauthorized.isUnauthorized, isTrue);
      expect(unauthorized.isForbidden, isFalse);

      const forbidden = ApiException(statusCode: 403, code: 'FORBIDDEN', detail: 'x');
      expect(forbidden.isForbidden, isTrue);

      const notFound = ApiException(statusCode: 404, code: 'NOT_FOUND', detail: 'x');
      expect(notFound.isNotFound, isTrue);

      const conflict = ApiException(statusCode: 409, code: 'CONFLICT', detail: 'x');
      expect(conflict.isConflict, isTrue);

      const validation = ApiException(statusCode: 422, code: 'VALIDATION_ERROR', detail: 'x');
      expect(validation.isValidation, isTrue);

      const unavailable = ApiException(statusCode: 503, code: 'ML_SERVICE_UNAVAILABLE', detail: 'x');
      expect(unavailable.isServiceUnavailable, isTrue);

      const serverError = ApiException(statusCode: 500, code: 'INTERNAL_ERROR', detail: 'x');
      expect(serverError.isServerError, isTrue);
    });

    test('network/timeout/malformed-response factories never leak a raw backend detail', () {
      expect(ApiException.network().userMessage, contains('internet'));
      expect(ApiException.timeout().userMessage, contains('too long'));
      expect(ApiException.malformedResponse().userMessage, isNotEmpty);
    });

    test('a 4xx validation/not-found/conflict error surfaces the backend detail verbatim', () {
      const e = ApiException(statusCode: 422, code: 'VALIDATION_ERROR', detail: 'Title must be at least 5 characters');
      expect(e.userMessage, 'Title must be at least 5 characters');
    });

    test('a 500-class error never surfaces the raw backend detail', () {
      const e = ApiException(
        statusCode: 500,
        code: 'INTERNAL_ERROR',
        detail: 'Traceback (most recent call last): ...',
      );
      expect(e.userMessage, isNot(contains('Traceback')));
    });

    test('a 401 always maps to a session-expired message regardless of backend detail', () {
      const e = ApiException(statusCode: 401, code: 'UNAUTHORIZED', detail: 'Invalid or expired token');
      expect(e.userMessage, contains('session'));
    });
  });
}
