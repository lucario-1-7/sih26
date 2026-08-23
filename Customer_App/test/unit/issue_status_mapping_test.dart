import 'package:flutter_test/flutter_test.dart';
import 'package:customer_app/models/issue_model.dart';

void main() {
  group('issueStatusFromChallengeStatus', () {
    test('maps every real backend ChallengeStatus value explicitly', () {
      expect(issueStatusFromChallengeStatus('submitted'), IssueStatus.underReview);
      expect(issueStatusFromChallengeStatus('open'), IssueStatus.inProgress);
      expect(issueStatusFromChallengeStatus('duplicate'), IssueStatus.duplicate);
      expect(issueStatusFromChallengeStatus('resolved'), IssueStatus.resolved);
    });

    test('an unrecognized backend value degrades to the least-committal state, not a crash', () {
      expect(issueStatusFromChallengeStatus('some_future_status'), IssueStatus.underReview);
    });

    test('duplicate is never silently displayed as resolved', () {
      expect(issueStatusFromChallengeStatus('duplicate'), isNot(IssueStatus.resolved));
    });
  });
}
