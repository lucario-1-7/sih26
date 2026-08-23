import '../data/models/challenge.dart';

enum IssueStatus {
  underReview,
  inProgress,
  resolved,
  duplicate,
}

/// Maps the backend's real `ChallengeStatus` ("submitted" | "open" |
/// "duplicate" | "resolved" — see server/app/models/enums.py) onto this
/// screen-facing enum. Every backend value has an explicit, named
/// counterpart here — none are silently folded into an unrelated meaning:
///   submitted -> underReview   (not yet triaged by a validator)
///   open      -> inProgress    (triaged, visible to institutions, being worked)
///   duplicate -> duplicate     (its own state, never disguised as resolved/in-progress)
///   resolved  -> resolved      (exact match)
IssueStatus issueStatusFromChallengeStatus(String backendStatus) {
  switch (backendStatus) {
    case 'submitted':
      return IssueStatus.underReview;
    case 'open':
      return IssueStatus.inProgress;
    case 'duplicate':
      return IssueStatus.duplicate;
    case 'resolved':
      return IssueStatus.resolved;
    default:
      // Unknown value from the backend: surface as "under review" (the most
      // conservative, least-committal state) rather than guessing further.
      return IssueStatus.underReview;
  }
}

extension IssueStatusExtension on IssueStatus {
  String get label {
    switch (this) {
      case IssueStatus.underReview:
        return 'Under Review';
      case IssueStatus.inProgress:
        return 'In Progress';
      case IssueStatus.resolved:
        return 'Resolved';
      case IssueStatus.duplicate:
        return 'Marked Duplicate';
    }
  }

  double get defaultProgress {
    switch (this) {
      case IssueStatus.underReview:
        return 0.30;
      case IssueStatus.inProgress:
        return 0.65;
      case IssueStatus.resolved:
        return 1.0;
      case IssueStatus.duplicate:
        return 0.30;
    }
  }
}

class IssueItem {
  final String id;
  final String title;
  final String category;
  final String description;
  final String location;
  final String dateFiled;
  final IssueStatus status;
  final double? progress;
  final String? imagePath;
  final String? citizenName;
  final String? citizenEmail;
  final String? citizenMobile;
  final String? cityWard;
  final String? pincode;
  // Not resolved from the challenge alone: a challenge only carries a
  // cluster_id (once a validator has triaged it); the caller (see
  // issue_detail_screen.dart) looks up the taken-up project for that
  // cluster separately via ProjectRepository, the same as areaName above.
  final String? clusterId;

  const IssueItem({
    required this.id,
    required this.title,
    required this.category,
    required this.description,
    required this.location,
    required this.dateFiled,
    required this.status,
    this.progress,
    this.imagePath,
    this.citizenName,
    this.citizenEmail,
    this.citizenMobile,
    this.cityWard,
    this.pincode,
    this.clusterId,
  });

  double get progressValue => progress ?? status.defaultProgress;
  int get progressPercent => (progressValue * 100).round();

  /// The single place a real backend `Challenge` becomes the UI-facing
  /// `IssueItem` these widgets already render. `areaName` is resolved by the
  /// caller (via AdministrativeAreaRepository) since the backend response
  /// only carries the area's id, not its display name.
  factory IssueItem.fromChallenge(Challenge challenge, {String? areaName}) {
    return IssueItem(
      id: challenge.id,
      title: challenge.title,
      // Real AI domain classification when available; the worker job that
      // populates it runs asynchronously after submission, so it is
      // legitimately absent for a few seconds on a freshly-filed issue —
      // shown as such rather than guessed at client-side.
      category: challenge.contentDomain ?? 'Classifying…',
      description: challenge.description,
      location: [areaName, challenge.pinCode].whereType<String>().join(', '),
      dateFiled: _formatDate(challenge.createdAt),
      status: issueStatusFromChallengeStatus(challenge.status),
      pincode: challenge.pinCode,
      clusterId: challenge.clusterId,
    );
  }

  static String _formatDate(DateTime date) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', //
    ];
    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }
}

// Global mock dataset for UI demonstration
class MockIssueRepository {
  static final List<IssueItem> initialIssues = [
    const IssueItem(
      id: 'ISS-2026-001',
      title: 'Road damage near Main Road',
      category: 'Roads & Infrastructure',
      description:
          'Deep pothole on the outer lane causing vehicle damage and traffic slowdowns during peak hours.',
      location: 'Chennai, Tamil Nadu',
      dateFiled: '18 Aug 2026',
      status: IssueStatus.inProgress,
      progress: 0.65,
    ),
    const IssueItem(
      id: 'ISS-2026-002',
      title: 'Water supply interruption',
      category: 'Water & Utilities',
      description:
          'Low water pressure and intermittent supply in sector 4 over the past two days.',
      location: 'Manapakkam',
      dateFiled: '15 Aug 2026',
      status: IssueStatus.underReview,
      progress: 0.35,
    ),
    const IssueItem(
      id: 'ISS-2026-003',
      title: 'Streetlight outage on 5th Cross',
      category: 'Electrical & Lighting',
      description:
          'Three consecutive streetlights are out, creating safety concerns at night.',
      location: 'Adyar, Chennai',
      dateFiled: '04 Aug 2026',
      status: IssueStatus.resolved,
      progress: 1.0,
    ),
    const IssueItem(
      id: 'ISS-2026-004',
      title: 'Waste clearance delay',
      category: 'Sanitation & Health',
      description:
          'Community waste bins overflowing near central park corner since weekend.',
      location: 'Sector 12, Chennai',
      dateFiled: '02 Aug 2026',
      status: IssueStatus.inProgress,
      progress: 0.50,
    ),
  ];
}
