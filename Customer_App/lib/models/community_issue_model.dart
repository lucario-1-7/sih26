import 'issue_model.dart';
import '../data/models/challenge.dart';

class CommunityComment {
  final String id;
  final String author;
  final String role; // e.g. "Resident", "Ward Committee", "Civic Volunteer", "Local Official"
  final String timeAgo;
  final String content;
  int upvotes;
  bool isUpvoted;
  bool isDownvoted;
  final bool isOfficial;
  final bool isOp;
  final String? parentId;
  final List<CommunityComment> replies;

  CommunityComment({
    required this.id,
    required this.author,
    this.role = 'Resident',
    required this.timeAgo,
    required this.content,
    this.upvotes = 0,
    this.isUpvoted = false,
    this.isDownvoted = false,
    this.isOfficial = false,
    this.isOp = false,
    this.parentId,
    List<CommunityComment>? replies,
  }) : replies = replies ?? [];
}

class CommunityIssue {
  final String id;
  final String title;
  final String description;
  final String category; // e.g. "Roads & Infrastructure", "Water Scarcity", "Sanitation & Waste", "Accessibility", "Public Safety", "Environment", "Education & Health"
  final String location;
  final String responsibleAuthority; // e.g. "Public Works Dept (PWD)", "Municipal Corporation", "Drinking Water & Sanitation Dept"
  final String affectedPopulation; // e.g. "~1,800 commuters & school buses"
  final String actionPlan; // What actions can be taken to solve it
  final String evidenceSummary; // Evidence user provided
  final String dateFiled;
  final IssueStatus status;
  int upvotes;
  bool isUpvoted;
  bool isDownvoted;
  int commentsCount;
  final List<CommunityComment> comments;
  final int? trendingRank;
  final String? backendChallengeId;
  final String author;
  final String authorFlair;
  final String timeAgo;
  final int shares;

  CommunityIssue({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.location,
    required this.responsibleAuthority,
    required this.affectedPopulation,
    required this.actionPlan,
    this.evidenceSummary = '2 photos & GPS coordinates attached',
    required this.dateFiled,
    required this.status,
    this.upvotes = 0,
    this.isUpvoted = false,
    this.isDownvoted = false,
    int? commentsCount,
    List<CommunityComment>? comments,
    this.trendingRank,
    this.backendChallengeId,
    String? author,
    String? authorFlair,
    String? timeAgo,
    int? shares,
  })  : author = author ?? 'citizen_${id.replaceAll(RegExp(r'[^a-zA-Z0-9]'), '').toLowerCase()}',
        authorFlair = authorFlair ?? 'Verified Resident',
        timeAgo = timeAgo ?? '13h',
        shares = shares ?? (41 + (id.hashCode.abs() % 50)),
        comments = comments ?? [],
        commentsCount = commentsCount ?? (comments?.length ?? 0);

  /// Converts a category string into a Reddit-style subreddit name (e.g. r/RoadsAndInfra)
  String get subredditName {
    final clean = category
        .replaceAll('&', 'And')
        .replaceAll(' ', '')
        .replaceAll(RegExp(r'[^a-zA-Z0-9]'), '');
    return 'r/$clean';
  }

  /// Converts a real backend challenge into a CommunityIssue
  factory CommunityIssue.fromChallenge(Challenge challenge, {String? areaName}) {
    final status = issueStatusFromChallengeStatus(challenge.status);
    final domain = _mapDomainToCategory(challenge.contentDomain);

    return CommunityIssue(
      id: challenge.id,
      title: challenge.title,
      description: challenge.description,
      category: domain,
      location: [areaName, challenge.pinCode].whereType<String>().join(', ').isEmpty
          ? 'Community District'
          : [areaName, challenge.pinCode].whereType<String>().join(', '),
      responsibleAuthority: _authorityForDomain(challenge.contentDomain),
      affectedPopulation: 'Local community & residents',
      actionPlan: 'Official inspection scheduled; community tracking active.',
      evidenceSummary: 'Geolocated citizen submission',
      dateFiled: _formatDate(challenge.createdAt),
      status: status,
      upvotes: 45 + (challenge.id.hashCode.abs() % 120),
      isUpvoted: false,
      isDownvoted: false,
      author: 'resident_${challenge.id.substring(0, 4)}',
      authorFlair: 'Ward Citizen',
      timeAgo: '4h',
      shares: 18,
      comments: [
        CommunityComment(
          id: 'comm-init-${challenge.id}',
          author: 'Civic Desk Bot',
          role: 'Official System',
          timeAgo: 'Just now',
          content: 'Issue registered and synchronized with service operations database.',
          isOfficial: true,
          upvotes: 12,
        ),
      ],
      backendChallengeId: challenge.id,
    );
  }

  static String _mapDomainToCategory(String? domain) {
    if (domain == null) return 'Community General';
    switch (domain.toLowerCase()) {
      case 'urban_infrastructure':
      case 'roads':
        return 'Roads & Infrastructure';
      case 'water':
      case 'water_scarcity':
        return 'Water Scarcity';
      case 'sanitation':
      case 'waste':
        return 'Sanitation & Waste';
      case 'education':
        return 'Education & Literacy';
      case 'healthcare':
      case 'health':
        return 'Healthcare Access';
      case 'public_safety':
      case 'safety':
        return 'Public Safety';
      case 'energy':
      case 'lighting':
        return 'Streetlights & Energy';
      case 'accessibility':
        return 'Accessibility';
      case 'environment':
        return 'Environmental Pollution';
      default:
        return domain.replaceAll('_', ' ').split(' ').map((w) => w.isNotEmpty ? '${w[0].toUpperCase()}${w.substring(1)}' : '').join(' ');
    }
  }

  static String _authorityForDomain(String? domain) {
    if (domain == null) return 'Civic Works & Public Services';
    switch (domain.toLowerCase()) {
      case 'urban_infrastructure':
      case 'roads':
        return 'Public Works Department (PWD)';
      case 'water':
      case 'water_scarcity':
        return 'Drinking Water & Sanitation Dept';
      case 'sanitation':
      case 'waste':
        return 'Sanitation & Solid Waste Management';
      case 'education':
        return 'Department of School Education';
      case 'healthcare':
      case 'health':
        return 'District Health Society';
      case 'public_safety':
      case 'safety':
        return 'Local Police & Traffic Directorate';
      case 'energy':
      case 'lighting':
        return 'Power Grid & Community Lighting';
      default:
        return 'Competent District Authority';
    }
  }

  static String _formatDate(DateTime date) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }
}

class MockCommunityRepository {
  static List<CommunityIssue> getInitialTrendingIssues() {
    return [
      CommunityIssue(
        id: 'SOC-2026-001',
        title: 'Collapsed culvert & severe road cave-in on Central Ring Road blocking school transit',
        description:
            'A 1.2m deep cave-in on the outer carriage lane has rendered Central Ring Road hazardous. Water logging from broken drainage worsens the erosion during rain, forcing emergency detours for 3 school buses.',
        category: 'Roads & Infrastructure',
        location: 'Central Ring Road, Ward 14',
        responsibleAuthority: 'Public Works & Infrastructure Dept',
        affectedPopulation: '~1,800 daily commuters & 3 school transit routes',
        actionPlan: 'Deploy structural shoring, replace 900mm Hume pipe, and lay reinforced bituminous patch.',
        evidenceSummary: '4 photos, depth measurements, and resident traffic complaint log',
        dateFiled: '24 Sep 2026',
        status: IssueStatus.inProgress,
        upvotes: 217,
        isUpvoted: true,
        trendingRank: 1,
        author: 'manor2003',
        authorFlair: 'Ward 14 Resident',
        timeAgo: '13h',
        shares: 41,
        comments: [
          CommunityComment(
            id: 'c1',
            author: 'lugla50',
            role: 'Resident',
            timeAgo: '12h',
            content: 'Wow, thanks for posting this. I noticed this culvert cracked weeks ago during the monsoon, and now school buses are forced to take a huge detour. We really need immediate municipal action before more accidents happen.',
            upvotes: 27,
            replies: [
              CommunityComment(
                id: 'c1-1',
                author: 'manor2003',
                role: 'Ward 14 Resident',
                timeAgo: '12h',
                isOp: true,
                content: 'I spoke with the ward supervisor at 9 AM, they confirmed the engineering team was dispatched. Hope the repair finishes before Monday transit!',
                upvotes: 14,
              ),
            ],
          ),
          CommunityComment(
            id: 'c2',
            author: 'Er. Rajesh Kumar',
            role: 'Operations Engineer',
            timeAgo: '1h',
            content: 'Inspection completed at 11 AM. Barricades placed and contractor mobilized with gravel.',
            isOfficial: true,
            upvotes: 45,
          ),
          CommunityComment(
            id: 'c3',
            author: 'Priya Mukherjee',
            role: 'Ward Volunteer',
            timeAgo: '35m',
            content: 'Please ensure nighttime reflective markers are installed so two-wheelers do not fall in.',
            upvotes: 19,
          ),
        ],
      ),
      CommunityIssue(
        id: 'SOC-2026-002',
        title: 'Dry community borewell and contaminated pipeline backflow in low-income settlement',
        description:
            'The main 10HP submersible pump broke down 5 days ago. Concurrently, cracked distribution lines are drawing in open drain runoff, leaving families reliant on unsafe stagnant pond water.',
        category: 'Water Scarcity',
        location: 'Greenfield Enclave, Sector 3',
        responsibleAuthority: 'Public Water Supply & Sanitation Board',
        affectedPopulation: '420 low-income households (~2,100 citizens)',
        actionPlan: 'Dispatch emergency mobile water tankers, replace burned motor, and isolate leaking supply pipe.',
        evidenceSummary: 'Turbidity test photos, video of dry communal taps',
        dateFiled: '23 Sep 2026',
        status: IssueStatus.underReview,
        upvotes: 589,
        isUpvoted: false,
        trendingRank: 2,
        author: 'suman_devi',
        authorFlair: 'Basti Representative',
        timeAgo: '1d',
        shares: 63,
        comments: [
          CommunityComment(
            id: 'c4',
            author: 'Suman Devi',
            role: 'Basti Representative',
            timeAgo: '5h',
            content: 'Children are developing stomach infections. We urgently need drinking water tankers!',
            upvotes: 62,
            replies: [
              CommunityComment(
                id: 'c4-1',
                author: 'Vikas Toppo',
                role: 'Social Worker',
                timeAgo: '3h',
                content: 'Submitted request to Water Supply Operations Desk. Expecting tanker delivery today.',
                upvotes: 34,
              ),
            ],
          ),
        ],
      ),
      CommunityIssue(
        id: 'SOC-2026-003',
        title: 'Missing wheelchair ramps and blocked accessibility paths at Civil Hospital OPD',
        description:
            'The main outpatient entry has a steep 5-step concrete flight without any ramp or grab rails. Tactile floor markers for visually impaired visitors are broken or covered with construction debris.',
        category: 'Accessibility',
        location: 'District Central Hospital, Main Access Rd',
        responsibleAuthority: 'Health Facilities & Infrastructure Operations',
        affectedPopulation: 'Elderly patients, pregnant women & persons with disabilities (~300 daily)',
        actionPlan: 'Construct non-slip 1:12 slope ramp with dual handrails and reinstall yellow tactile warning tiles.',
        evidenceSummary: 'Photographic evidence showing wheelchair patients being carried up steps manually',
        dateFiled: '22 Sep 2026',
        status: IssueStatus.inProgress,
        upvotes: 345,
        isUpvoted: false,
        trendingRank: 3,
        author: 'dr_anand_minz',
        authorFlair: 'Hospital Visitor',
        timeAgo: '2d',
        shares: 29,
        comments: [
          CommunityComment(
            id: 'c6',
            author: 'Dr. Anand Minz',
            role: 'Hospital Visitor',
            timeAgo: '1d',
            content: 'Elderly patients struggle daily. It is a fundamental right under the Rights of Persons with Disabilities Act.',
            upvotes: 41,
            replies: [
              CommunityComment(
                id: 'c7',
                author: 'Rameshwar Singh',
                role: 'Civil Contractor',
                timeAgo: '18h',
                content: 'Ramp layout drawings approved. Construction starting this Saturday.',
                isOfficial: true,
                upvotes: 53,
              ),
            ],
          ),
        ],
      ),
      CommunityIssue(
        id: 'SOC-2026-004',
        title: 'Illegal chemical sludge dumping along Subarnarekha river agricultural belt',
        description:
            'Unidentified tankers are dumping dark industrial effluent into drainage culverts that discharge directly into the riverbank. Strong chemical fumes reported at dawn, killing local vegetation.',
        category: 'Environmental Pollution',
        location: 'Riverfront Industrial Corridor, Zone 2',
        responsibleAuthority: 'Environmental Safety & Pollution Control Board',
        affectedPopulation: 'Downstream farming hamlets across 4 panchayats',
        actionPlan: 'Deploy mobile environmental testing van, install CCTV surveillance, and lodge FIR against violators.',
        evidenceSummary: 'Time-stamped photos of toxic foam and tanker tire track marks',
        dateFiled: '21 Sep 2026',
        status: IssueStatus.underReview,
        upvotes: 721,
        isUpvoted: true,
        trendingRank: 4,
        comments: [
          CommunityComment(
            id: 'c8',
            author: 'Balram Mahto',
            role: 'Farmer',
            timeAgo: '2d ago',
            content: 'Our vegetable crop leaves are scorching after using river pump water. Strict action needed against factories.',
            upvotes: 89,
          ),
          CommunityComment(
            id: 'c9',
            author: 'Green Action Collective',
            role: 'Environmental NGO',
            timeAgo: '1d ago',
            content: 'Water samples sent to accredited environmental testing lab for chemical analysis.',
            upvotes: 67,
          ),
        ],
      ),
      CommunityIssue(
        id: 'SOC-2026-005',
        title: 'Zero streetlighting on 800m stretch connecting Girls’ Polytechnic and bus stand',
        description:
            'Eight consecutive poles have burned bulbs or severed wiring. Female students and healthcare workers returning from evening shifts face severe safety hazards in complete pitch darkness.',
        category: 'Public Safety',
        location: 'Circular Road to Tech Institute Junction',
        responsibleAuthority: 'Power & Street Lighting Division',
        affectedPopulation: '650+ evening students, nurses, and pedestrians daily',
        actionPlan: 'Replace fixtures with 90W LED smart streetlights and trim obscuring tree foliage.',
        evidenceSummary: 'Nighttime lux measurement photos (< 0.5 lux), student petition with 180 signatures',
        dateFiled: '20 Sep 2026',
        status: IssueStatus.inProgress,
        upvotes: 534,
        isUpvoted: false,
        trendingRank: 5,
        comments: [
          CommunityComment(
            id: 'c10',
            author: 'Sneha Kumari',
            role: 'Student Representative',
            timeAgo: '2d ago',
            content: 'We avoid walking alone after 6:30 PM. PCR vans should patrol till lights are restored.',
            upvotes: 74,
          ),
          CommunityComment(
            id: 'c11',
            author: 'Civic Support Desk',
            role: 'Official',
            timeAgo: '1d ago',
            content: 'Work order #EL-492 issued to contractor. Pole wiring replacement in progress.',
            isOfficial: true,
            upvotes: 58,
          ),
        ],
      ),
      CommunityIssue(
        id: 'SOC-2026-006',
        title: 'Open drainage overflow creating dengue and vector breeding hotspot near primary school',
        description:
            'Uncovered community drain choked with single-use plastic waste has formed a stagnant 200m swamp directly fronting the primary school gate. 6 suspected dengue cases reported in 10 days.',
        category: 'Sanitation & Waste',
        location: 'Old Town Quarter, Ward 8',
        responsibleAuthority: 'Civic Sanitation & Vector Control Cell',
        affectedPopulation: '380 school children and ~1,500 neighborhood residents',
        actionPlan: 'Mechanized vacuum desilting, placement of RCC precast cover slabs, and malathion thermal fogging.',
        evidenceSummary: 'Video of black sludge overflow, clinic prescription logs',
        dateFiled: '15 Sep 2026',
        status: IssueStatus.resolved,
        upvotes: 398,
        isUpvoted: false,
        trendingRank: 6,
        comments: [
          CommunityComment(
            id: 'c12',
            author: 'Mohd. Salim',
            role: 'Ward 8 Resident',
            timeAgo: '3d ago',
            content: 'Sanitation team arrived with suction machine yesterday. Heavy silt cleared and lime sprinkled!',
            isOfficial: false,
            upvotes: 49,
          ),
          CommunityComment(
            id: 'c13',
            author: 'Ward Operations Office',
            role: 'Civic Operations',
            timeAgo: '2d ago',
            content: 'Drain covers have been installed. Fogging will continue twice weekly.',
            isOfficial: true,
            upvotes: 82,
          ),
        ],
      ),
    ];
  }
}
