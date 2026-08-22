import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';
import '../widgets/custom_bottom_navbar.dart';
import '../widgets/dashboard_issue_card.dart';
import '../widgets/issue_card.dart';
import '../widgets/media_upload_card.dart';
import '../widgets/primary_button.dart';
import 'issue_detail_screen.dart';
import 'settings_screen.dart';

class MainDashboardScreen extends StatefulWidget {
  final List<IssueItem>? initialIssues;

  const MainDashboardScreen({
    super.key,
    this.initialIssues,
  });

  @override
  State<MainDashboardScreen> createState() => _MainDashboardScreenState();
}

class _MainDashboardScreenState extends State<MainDashboardScreen> {
  late List<IssueItem> _issues;
  int _currentTabIndex = 0;
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _issues = widget.initialIssues ?? List.from(MockIssueRepository.initialIssues);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _formFullNameController.dispose();
    _formEmailController.dispose();
    _formMobileController.dispose();
    _formAddressController.dispose();
    _formCityWardController.dispose();
    _formPincodeController.dispose();
    _formTitleController.dispose();
    _formDescriptionController.dispose();
    super.dispose();
  }

  void _onFileIssuePressed() {
    setState(() {
      _currentTabIndex = 2; // Jump to File Grievance tab
    });
  }

  void _navigateToDetail(IssueItem issue) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => IssueDetailScreen(issue: issue),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: IndexedStack(
          index: _currentTabIndex,
          children: [
            _buildHomeTab(),
            _buildMyIssuesTab(),
            _buildFileGrievanceTab(),
            _buildActivityTab(),
            _buildProfileTab(),
          ],
        ),
      ),
      bottomNavigationBar: CustomBottomNavbar(
        currentIndex: _currentTabIndex,
        onTabSelected: (index) {
          setState(() {
            _currentTabIndex = index;
          });
        },
        onAddPressed: _onFileIssuePressed,
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 0: HOME / DASHBOARD
  // ---------------------------------------------------------------------------
  Widget _buildHomeTab() {
    final filteredIssues = _searchQuery.isEmpty
        ? _issues
        : _issues
            .where((i) =>
                i.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
                i.category.toLowerCase().contains(_searchQuery.toLowerCase()) ||
                i.location.toLowerCase().contains(_searchQuery.toLowerCase()))
            .toList();

    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top Bar with Grid & Notification Bell
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(10.0),
                decoration: BoxDecoration(
                  color: AppColors.inputBackground,
                  borderRadius: BorderRadius.circular(12.0),
                  border: Border.all(color: AppColors.border, width: 1.0),
                ),
                child: const Icon(
                  FeatherIcons.grid,
                  size: 18,
                  color: AppColors.primaryText,
                ),
              ),
              Text(
                'Home',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                ),
              ),
              InkWell(
                onTap: () {
                  setState(() {
                    _currentTabIndex = 2; // Jump to activity/notifications
                  });
                },
                borderRadius: BorderRadius.circular(12.0),
                child: Container(
                  padding: const EdgeInsets.all(10.0),
                  decoration: BoxDecoration(
                    color: AppColors.inputBackground,
                    borderRadius: BorderRadius.circular(12.0),
                    border: Border.all(color: AppColors.border, width: 1.0),
                  ),
                  child: const Icon(
                    FeatherIcons.bell,
                    size: 18,
                    color: AppColors.primaryText,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Greeting Section
          Text(
            'Hi Dhyan!',
            style: AppTypography.heading(context).copyWith(
              fontSize: 26,
              fontWeight: FontWeight.w700,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Good morning',
            style: AppTypography.supporting(context).copyWith(
              fontSize: 14,
              color: AppColors.secondaryText,
            ),
          ),

          const SizedBox(height: 20),

          // Search Bar with Feather Icons
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            decoration: BoxDecoration(
              color: AppColors.inputBackground,
              borderRadius: BorderRadius.circular(14.0),
              border: Border.all(color: AppColors.border, width: 1.0),
            ),
            child: Row(
              children: [
                const Icon(
                  FeatherIcons.search,
                  size: 18,
                  color: AppColors.mutedText,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    onChanged: (val) {
                      setState(() {
                        _searchQuery = val;
                      });
                    },
                    style: AppTypography.inputText(context).copyWith(
                      fontSize: 14,
                    ),
                    decoration: InputDecoration(
                      hintText: 'Search',
                      hintStyle: AppTypography.placeholder(context).copyWith(
                        fontSize: 14,
                      ),
                      border: InputBorder.none,
                      isDense: true,
                      contentPadding:
                          const EdgeInsets.symmetric(vertical: 14.0),
                    ),
                  ),
                ),
                if (_searchQuery.isNotEmpty)
                  GestureDetector(
                    onTap: () {
                      _searchController.clear();
                      setState(() {
                        _searchQuery = '';
                      });
                    },
                    child: const Icon(
                      FeatherIcons.x,
                      size: 16,
                      color: AppColors.secondaryText,
                    ),
                  ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Welcome Action Card matching reference
          Container(
            padding: const EdgeInsets.all(18.0),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(18.0),
              border: Border.all(color: AppColors.border, width: 1.0),
            ),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome!',
                        style: AppTypography.heading(context).copyWith(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        "Let's schedule your civic grievance resolution.",
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 13,
                          color: AppColors.secondaryText,
                          height: 1.35,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: SizedBox(
                    height: 90,
                    child: Lottie.asset(
                      'lib/assets/welcome_back.json',
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          decoration: BoxDecoration(
                            color: AppColors.background,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppColors.border),
                          ),
                          child: const Icon(
                            FeatherIcons.edit3,
                            size: 32,
                            color: AppColors.primaryText,
                          ),
                        );
                      },
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 28),

          // Section Header: Ongoing Projects / Ongoing Issues
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Ongoing Issues',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              GestureDetector(
                onTap: () {
                  setState(() {
                    _currentTabIndex = 1; // Switch to My Issues Tab
                  });
                },
                child: Text(
                  'View all',
                  style: AppTypography.supporting(context).copyWith(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: AppColors.secondaryText,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 2x2 Grid of Issue Cards matching reference
          if (filteredIssues.isEmpty)
            _buildEmptyState()
          else
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: filteredIssues.length > 4 ? 4 : filteredIssues.length,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12.0,
                mainAxisSpacing: 12.0,
                childAspectRatio: 0.74,
              ),
              itemBuilder: (context, index) {
                final issue = filteredIssues[index];
                return DashboardIssueCard(
                  issue: issue,
                  isFeatured: index == 0,
                  onTap: () => _navigateToDetail(issue),
                );
              },
            ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 1: MY ISSUES (ALL FILED ISSUES)
  // ---------------------------------------------------------------------------
  Widget _buildMyIssuesTab() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'My Issues',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12.0, vertical: 4.0),
                decoration: BoxDecoration(
                  color: AppColors.primaryText,
                  borderRadius: BorderRadius.circular(16.0),
                ),
                child: Text(
                  '${_issues.length}',
                  style: AppTypography.supporting(context).copyWith(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'All public grievances filed by you and their current status.',
            style: AppTypography.supporting(context).copyWith(fontSize: 13),
          ),
          const SizedBox(height: 20),

          if (_issues.isEmpty)
            _buildEmptyState()
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _issues.length,
              itemBuilder: (context, index) {
                final issue = _issues[index];
                return IssueCard(
                  issue: issue,
                  onTap: () => _navigateToDetail(issue),
                );
              },
            ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 2: FILE GRIEVANCE (CHECKOUT-STYLE FORM UX)
  // ---------------------------------------------------------------------------
  final TextEditingController _formFullNameController =
      TextEditingController(text: 'Rahul Tiwari');
  final TextEditingController _formEmailController =
      TextEditingController(text: 'rahul.tiwari@janseva.gov.in');
  final TextEditingController _formMobileController =
      TextEditingController(text: '9876543210');
  final TextEditingController _formAddressController =
      TextEditingController(text: 'House 42, Outer Ring Road');
  final TextEditingController _formCityWardController =
      TextEditingController(text: 'Sector 12, Ward 4');
  final TextEditingController _formPincodeController =
      TextEditingController(text: '600028');
  final TextEditingController _formTitleController = TextEditingController();
  final TextEditingController _formDescriptionController = TextEditingController();

  String _formSelectedCategory = 'Roads & Infrastructure';
  bool _formHasAttachedMedia = false;

  void _onFormSubmit() {
    final titleText = _formTitleController.text.trim().isEmpty
        ? 'Civic Grievance Report'
        : _formTitleController.text.trim();
    final descriptionText = _formDescriptionController.text.trim().isEmpty
        ? 'Reported issue submitted for review and resolution.'
        : _formDescriptionController.text.trim();
    final locationText = _formAddressController.text.trim().isEmpty
        ? 'Sector 12, Main Ward'
        : '${_formAddressController.text.trim()}, ${_formCityWardController.text.trim()}';

    final newIssue = IssueItem(
      id: 'ISS-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
      title: titleText,
      category: _formSelectedCategory,
      description: descriptionText,
      location: locationText,
      dateFiled: 'Today',
      status: IssueStatus.underReview,
      imagePath: _formHasAttachedMedia ? 'mock_evidence.jpg' : null,
    );

    setState(() {
      _issues.insert(0, newIssue);
      _currentTabIndex = 1; // Switch to My Issues tab
      _formTitleController.clear();
      _formDescriptionController.clear();
      _formHasAttachedMedia = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Grievance filed successfully!')),
    );
  }

  Widget _buildFileGrievanceTab() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top Heading Bar matching reference image
          _buildFormTopBar(),

          const SizedBox(height: 18),

          // SECTION 1: Contact Information
          _buildFormSectionHeader(1, 'Contact Information'),
          const SizedBox(height: 12),
          _buildFormInputField(
            controller: _formFullNameController,
            placeholder: 'Full Name',
            icon: FeatherIcons.user,
          ),
          const SizedBox(height: 10),
          _buildFormInputField(
            controller: _formEmailController,
            placeholder: 'Email Address',
            icon: FeatherIcons.mail,
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 10),
          _buildFormInputField(
            controller: _formMobileController,
            placeholder: 'Phone Number',
            icon: FeatherIcons.phone,
            keyboardType: TextInputType.phone,
          ),

          const SizedBox(height: 24),

          // SECTION 2: Grievance Location
          _buildFormSectionHeader(2, 'Grievance Location'),
          const SizedBox(height: 12),
          _buildFormInputField(
            controller: _formAddressController,
            placeholder: 'Address (House no., Street name)',
            icon: FeatherIcons.mapPin,
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: _buildFormInputField(
                  controller: _formCityWardController,
                  placeholder: 'City / Ward',
                  icon: FeatherIcons.compass,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildFormInputField(
                  controller: _formPincodeController,
                  placeholder: 'ZIP / Pincode',
                  icon: FeatherIcons.hash,
                  keyboardType: TextInputType.number,
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // SECTION 3: Issue Category & Details
          _buildFormSectionHeader(3, 'Issue Category & Details'),
          const SizedBox(height: 12),

          // 4 Category Tiles matching the reference selector style
          _buildCategoryTiles(),

          const SizedBox(height: 14),

          _buildFormInputField(
            controller: _formTitleController,
            placeholder: 'Subject / Short Title (e.g. Broken water pipe)',
            icon: FeatherIcons.fileText,
          ),
          const SizedBox(height: 10),
          _buildFormInputField(
            controller: _formDescriptionController,
            placeholder: 'Detailed problem description...',
            icon: FeatherIcons.alignLeft,
            maxLines: 3,
          ),

          const SizedBox(height: 16),

          MediaUploadCard(
            onMediaSelected: (hasPhoto) {
              setState(() => _formHasAttachedMedia = hasPhoto);
            },
          ),

          const SizedBox(height: 24),

          PrimaryButton(
            text: 'Submit Grievance',
            onPressed: _onFormSubmit,
          ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // Top Bar matching reference image with centered title/subtitle and security shield
  Widget _buildFormTopBar() {
    return Row(
      children: [
        GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () {
            setState(() {
              _currentTabIndex = 0; // Return to Home
            });
          },
          child: Container(
            width: 36,
            height: 36,
            alignment: Alignment.centerLeft,
            child: const Icon(
              FeatherIcons.arrowLeft,
              size: 20,
              color: AppColors.primaryText,
            ),
          ),
        ),
        Expanded(
          child: Column(
            children: [
              Text(
                'File Grievance',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                'Submit municipal issue securely',
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 12,
                  color: AppColors.secondaryText,
                ),
              ),
            ],
          ),
        ),
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(10.0),
            border: Border.all(color: const Color(0xFFDCFCE7), width: 1.0),
          ),
          child: const Center(
            child: Icon(
              FeatherIcons.shield,
              size: 16,
              color: Color(0xFF16A34A),
            ),
          ),
        ),
      ],
    );
  }

  // Numbered step badge + section heading
  Widget _buildFormSectionHeader(int step, String title) {
    return Row(
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: const BoxDecoration(
            color: Color(0xFF16A34A),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$step',
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ),
        ),
        const SizedBox(width: 10),
        Text(
          title,
          style: AppTypography.heading(context).copyWith(
            fontSize: 15,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }

  // Input Field with leading icon matching reference image
  Widget _buildFormInputField({
    required TextEditingController controller,
    required String placeholder,
    required IconData icon,
    int maxLines = 1,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 2.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Row(
        crossAxisAlignment:
            maxLines > 1 ? CrossAxisAlignment.start : CrossAxisAlignment.center,
        children: [
          Padding(
            padding: EdgeInsets.only(top: maxLines > 1 ? 12.0 : 0.0),
            child: Icon(
              icon,
              size: 18,
              color: AppColors.secondaryText,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: controller,
              maxLines: maxLines,
              keyboardType: keyboardType,
              style: AppTypography.inputText(context).copyWith(fontSize: 14),
              decoration: InputDecoration(
                hintText: placeholder,
                hintStyle: AppTypography.placeholder(context).copyWith(
                  fontSize: 14,
                  color: AppColors.mutedText,
                ),
                border: InputBorder.none,
                isDense: true,
                contentPadding: const EdgeInsets.symmetric(vertical: 13.0),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Category Tiles matching the payment methods in reference image
  Widget _buildCategoryTiles() {
    final categories = [
      {'id': 'Roads & Infrastructure', 'label': 'Roads', 'icon': FeatherIcons.mapPin},
      {'id': 'Water & Utilities', 'label': 'Water', 'icon': FeatherIcons.droplet},
      {'id': 'Electrical & Lighting', 'label': 'Electrical', 'icon': FeatherIcons.zap},
      {'id': 'Sanitation & Health', 'label': 'Sanitation', 'icon': FeatherIcons.trash},
    ];

    return Row(
      children: categories.map((cat) {
        final id = cat['id'] as String;
        final label = cat['label'] as String;
        final icon = cat['icon'] as IconData;
        final isSelected = _formSelectedCategory == id;

        return Expanded(
          child: GestureDetector(
            onTap: () {
              setState(() {
                _formSelectedCategory = id;
              });
            },
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 3.0),
              padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 4.0),
              decoration: BoxDecoration(
                color: isSelected ? const Color(0xFFF0FDF4) : AppColors.background,
                borderRadius: BorderRadius.circular(12.0),
                border: Border.all(
                  color: isSelected ? const Color(0xFF16A34A) : AppColors.border,
                  width: isSelected ? 1.5 : 1.0,
                ),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    icon,
                    size: 20,
                    color: isSelected ? const Color(0xFF16A34A) : AppColors.primaryText,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 11,
                      fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                      color: isSelected ? const Color(0xFF16A34A) : AppColors.primaryText,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 3: ACTIVITY / NOTIFICATIONS
  // ---------------------------------------------------------------------------
  Widget _buildActivityTab() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recent Activity',
            style: AppTypography.heading(context).copyWith(
              fontSize: 22,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Live updates and status changes on your reported grievances.',
            style: AppTypography.supporting(context).copyWith(fontSize: 13),
          ),
          const SizedBox(height: 20),

          _buildActivityTile(
            icon: FeatherIcons.checkCircle,
            title: 'Streetlight outage marked Resolved',
            subtitle: 'Municipal Electrical Division completed inspection',
            time: '2h ago',
          ),
          _buildActivityTile(
            icon: FeatherIcons.truck,
            title: 'Road damage inspection scheduled',
            subtitle: 'Assigned to Public Works Department field unit',
            time: 'Yesterday',
          ),
          _buildActivityTile(
            icon: FeatherIcons.droplet,
            title: 'Water supply interruption under review',
            subtitle: 'Sector 4 water lines triage in progress',
            time: '3 days ago',
          ),
          _buildActivityTile(
            icon: FeatherIcons.fileText,
            title: 'Citizen grievance submitted',
            subtitle: 'Reference ISS-2026-001 created successfully',
            time: '4 days ago',
          ),
        ],
      ),
    );
  }

  Widget _buildActivityTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required String time,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(14.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10.0),
            decoration: BoxDecoration(
              color: AppColors.inputBackground,
              borderRadius: BorderRadius.circular(10.0),
            ),
            child: Icon(icon, size: 18, color: AppColors.primaryText),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTypography.heading(context).copyWith(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: AppTypography.supporting(context).copyWith(
                    fontSize: 12,
                    color: AppColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Text(
            time,
            style: AppTypography.supporting(context).copyWith(
              fontSize: 11,
              color: AppColors.mutedText,
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 3: PROFILE
  // ---------------------------------------------------------------------------
  Widget _buildProfileTab() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const SizedBox(height: 12),
          // User Avatar & Name
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.inputBackground,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.border, width: 1.5),
            ),
            child: const Center(
              child: Icon(
                FeatherIcons.user,
                size: 38,
                color: AppColors.primaryText,
              ),
            ),
          ),
          const SizedBox(height: 14),
          Text(
            'Dhyan Kannoth',
            style: AppTypography.heading(context).copyWith(
              fontSize: 22,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Verified Citizen • Chennai, TN',
            style: AppTypography.supporting(context).copyWith(
              fontSize: 13,
              color: AppColors.secondaryText,
            ),
          ),

          const SizedBox(height: 24),

          // Stats Row
          Row(
            children: [
              _buildStatItem('Reported', '${_issues.length}'),
              const SizedBox(width: 10),
              _buildStatItem('In Progress', '2'),
              const SizedBox(width: 10),
              _buildStatItem('Resolved', '1'),
            ],
          ),

          const SizedBox(height: 24),
          const Divider(height: 1, thickness: 1, color: AppColors.divider),
          const SizedBox(height: 20),

          // Profile Actions
          _buildProfileOption(
            icon: FeatherIcons.phone,
            title: 'Phone Number',
            subtitle: '+91 98765 43210',
            onTap: () {},
          ),
          _buildProfileOption(
            icon: FeatherIcons.mail,
            title: 'Email Address',
            subtitle: 'dhyan@janseva.gov.in',
            onTap: () {},
          ),
          _buildProfileOption(
            icon: FeatherIcons.settings,
            title: 'Settings & Notifications',
            subtitle: 'Configure SMS and email updates',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
            },
          ),
          _buildProfileOption(
            icon: FeatherIcons.logOut,
            title: 'Logout',
            subtitle: 'Sign out of Social Serve',
            onTap: () {
              Navigator.popUntil(context, (route) => route.isFirst);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14.0),
        decoration: BoxDecoration(
          color: AppColors.inputBackground,
          borderRadius: BorderRadius.circular(14.0),
          border: Border.all(color: AppColors.border, width: 1.0),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: AppTypography.heading(context).copyWith(
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: AppTypography.supporting(context).copyWith(
                fontSize: 11,
                color: AppColors.mutedText,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(14.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14.0),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
          child: Row(
            children: [
              Icon(icon, size: 18, color: AppColors.primaryText),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: AppTypography.heading(context).copyWith(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 12,
                        color: AppColors.secondaryText,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                FeatherIcons.chevronRight,
                size: 16,
                color: AppColors.mutedText,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 36.0, horizontal: 20.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Column(
        children: [
          const Icon(
            FeatherIcons.inbox,
            size: 40,
            color: AppColors.mutedText,
          ),
          const SizedBox(height: 12),
          Text(
            'No issues found',
            style: AppTypography.heading(context).copyWith(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Report a problem in your community to track it here.',
            textAlign: TextAlign.center,
            style: AppTypography.supporting(context).copyWith(
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }
}
