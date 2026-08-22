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

  double get defaultProgress {
    switch (this) {
      case IssueStatus.underReview:
        return 0.30;
      case IssueStatus.inProgress:
        return 0.65;
      case IssueStatus.resolved:
        return 1.0;
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
  });

  double get progressValue => progress ?? status.defaultProgress;
  int get progressPercent => (progressValue * 100).round();
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
