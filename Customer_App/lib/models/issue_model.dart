enum IssueStatus {
  underReview,
  inProgress,
  resolved,
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
  final String? imagePath;

  const IssueItem({
    required this.id,
    required this.title,
    required this.category,
    required this.description,
    required this.location,
    required this.dateFiled,
    required this.status,
    this.imagePath,
  });
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
      status: IssueStatus.underReview,
    ),
    const IssueItem(
      id: 'ISS-2026-002',
      title: 'Water supply interruption',
      category: 'Water & Utilities',
      description:
          'Low water pressure and intermittent supply in sector 4 over the past two days.',
      location: 'Manapakkam',
      dateFiled: '15 Aug 2026',
      status: IssueStatus.inProgress,
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
    ),
  ];
}
