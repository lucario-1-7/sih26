import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import '../core/networking/api_exception.dart';
import '../data/models/administrative_area.dart';
import '../data/models/auth_tokens.dart';
import '../data/repositories/administrative_area_repository.dart';
import '../data/repositories/auth_repository.dart';
import '../data/repositories/challenge_repository.dart';
import '../data/repositories/user_repository.dart';
import '../models/issue_model.dart';
import '../services/language_service.dart';
import '../theme/app_theme.dart';
import '../widgets/custom_bottom_navbar.dart';
import '../widgets/dashboard_issue_card.dart';
import '../widgets/issue_card.dart';
import '../widgets/media_upload_card.dart';
import '../widgets/primary_button.dart';
import 'issue_detail_screen.dart';
import 'issue_success_screen.dart';
import 'recent_activity_screen.dart';
import 'settings_screen.dart';
import 'welcome_language_screen.dart';

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
  List<IssueItem> _issues = [];
  int _currentTabIndex = 0;
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _myIssuesSearchController = TextEditingController();
  String _myIssuesStatusFilter = 'All';
  String _myIssuesLocationFilter = 'All';
  String _myIssuesCategoryFilter = 'All';

  final List<String> _myIssuesStatusSections = [
    'All',
    'Issued',
    'In Progress',
    'Resolved',
  ];

  // -- Real backend state -----------------------------------------------
  bool _isLoading = true;
  String? _loadError;
  CurrentUser? _currentUser;
  List<AdministrativeArea> _areas = [];
  final Map<String, String> _areaNamesById = {};
  AdministrativeArea? _selectedArea;

  List<String> get _availableLocations {
    final locs = _issues
        .map((i) => i.location.trim())
        .where((l) => l.isNotEmpty)
        .toSet()
        .toList();
    locs.sort();
    return ['All Locations', ...locs];
  }

  @override
  void initState() {
    super.initState();
    if (widget.initialIssues != null) {
      _issues = widget.initialIssues!;
      _isLoading = false;
    } else {
      _bootstrap();
    }
  }

  /// Loads everything the dashboard needs from the real backend: the
  /// authenticated citizen's profile, the administrative-area reference list
  /// (needed both to resolve challenge locations for display and to let the
  /// grievance form submit a valid `administrative_area_id`), and the
  /// citizen's own challenges.
  Future<void> _bootstrap() async {
    setState(() {
      _isLoading = true;
      _loadError = null;
    });
    try {
      final user = await UserRepository.instance.getMe();
      final areas = await AdministrativeAreaRepository.instance.list();
      final areaNames = {for (final a in areas) a.id: a.name};
      final challenges = await ChallengeRepository.instance.listMyChallenges(user.id);

      if (!mounted) return;
      setState(() {
        _currentUser = user;
        _areas = areas;
        _areaNamesById
          ..clear()
          ..addAll(areaNames);
        _issues = challenges
            .map((c) => IssueItem.fromChallenge(c, areaName: _areaNamesById[c.administrativeAreaId]))
            .toList();
        _isLoading = false;
        // The backend has no email field for a citizen user — the mobile
        // number and name are the only real identity fields to prefill.
        _formMobileController.text = user.phone;
        if (user.name != user.phone) _formFullNameController.text = user.name;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _loadError = e.userMessage;
        _isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    _myIssuesSearchController.dispose();
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

  void _openFilterBottomSheet() {
    String tempStatus = _myIssuesStatusFilter;
    String tempLocation = _myIssuesLocationFilter;
    String tempCategory = _myIssuesCategoryFilter;

    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.background,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20.0)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 36,
                      height: 4,
                      decoration: BoxDecoration(
                        color: AppColors.border,
                        borderRadius: BorderRadius.circular(2.0),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Filter Grievances',
                        style: AppTypography.heading(context).copyWith(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      GestureDetector(
                        onTap: () {
                          setModalState(() {
                            tempStatus = 'All';
                            tempLocation = 'All';
                            tempCategory = 'All';
                          });
                        },
                        child: Text(
                          'Reset All',
                          style: AppTypography.supporting(context).copyWith(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: AppColors.secondaryText,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 18),

                  // STATUS FILTER
                  Text(
                    'Status',
                    style: AppTypography.heading(context).copyWith(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: ['All', 'Issued', 'In Progress', 'Resolved'].map((st) {
                      final sel = tempStatus == st;
                      return ChoiceChip(
                        label: Text(st),
                        selected: sel,
                        onSelected: (val) {
                          if (val) setModalState(() => tempStatus = st);
                        },
                        selectedColor: AppColors.primaryButton,
                        backgroundColor: AppColors.inputBackground,
                        labelStyle: TextStyle(
                          fontSize: 12,
                          fontWeight: sel ? FontWeight.w700 : FontWeight.w500,
                          color: sel ? Colors.white : AppColors.primaryText,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16.0),
                          side: BorderSide(
                            color: sel ? AppColors.primaryButton : AppColors.border,
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 18),

                  // LOCATION FILTER
                  Text(
                    'Location / Ward',
                    style: AppTypography.heading(context).copyWith(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 2.0),
                    decoration: BoxDecoration(
                      color: AppColors.inputBackground,
                      borderRadius: BorderRadius.circular(12.0),
                      border: Border.all(color: AppColors.border, width: 1.0),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _availableLocations.contains(tempLocation == 'All' ? 'All Locations' : tempLocation)
                            ? (tempLocation == 'All' ? 'All Locations' : tempLocation)
                            : 'All Locations',
                        isExpanded: true,
                        icon: const Icon(FeatherIcons.chevronDown, size: 16, color: AppColors.secondaryText),
                        dropdownColor: AppColors.background,
                        borderRadius: BorderRadius.circular(12.0),
                        items: _availableLocations.map((loc) {
                          return DropdownMenuItem<String>(
                            value: loc,
                            child: Text(
                              loc,
                              style: AppTypography.supporting(context).copyWith(
                                fontSize: 13,
                                color: AppColors.primaryText,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) {
                            setModalState(() {
                              tempLocation = val == 'All Locations' ? 'All' : val;
                            });
                          }
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),

                  // CATEGORY FILTER
                  Text(
                    'Department Category',
                    style: AppTypography.heading(context).copyWith(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: ['All', 'Roads', 'Water', 'Electrical', 'Sanitation'].map((cat) {
                      final sel = tempCategory == cat;
                      return ChoiceChip(
                        label: Text(cat),
                        selected: sel,
                        onSelected: (val) {
                          if (val) setModalState(() => tempCategory = cat);
                        },
                        selectedColor: AppColors.primaryButton,
                        backgroundColor: AppColors.inputBackground,
                        labelStyle: TextStyle(
                          fontSize: 12,
                          fontWeight: sel ? FontWeight.w700 : FontWeight.w500,
                          color: sel ? Colors.white : AppColors.primaryText,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16.0),
                          side: BorderSide(
                            color: sel ? AppColors.primaryButton : AppColors.border,
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),

                  // APPLY BUTTON
                  PrimaryButton(
                    text: 'Apply Filters',
                    onPressed: () {
                      setState(() {
                        _myIssuesStatusFilter = tempStatus;
                        _myIssuesLocationFilter = tempLocation;
                        _myIssuesCategoryFilter = tempCategory;
                      });
                      Navigator.pop(ctx);
                    },
                  ),
                ],
              ),
            );
          },
        );
      },
    );
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
    return AnimatedBuilder(
      animation: LanguageService.instance,
      builder: (context, _) {
        return Scaffold(
          backgroundColor: AppColors.background,
          body: SafeArea(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _loadError != null
                    ? _buildLoadErrorState()
                    : IndexedStack(
                        index: _currentTabIndex,
                        children: [
                          _buildHomeTab(),
                          _buildMyIssuesTab(),
                          _buildFileGrievanceTab(),
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
      },
    );
  }

  Widget _buildLoadErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(FeatherIcons.wifiOff, size: 48, color: AppColors.secondaryText),
            const SizedBox(height: 16),
            Text(
              _loadError ?? 'Something went wrong.',
              textAlign: TextAlign.center,
              style: AppTypography.supporting(context).copyWith(color: AppColors.secondaryText),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: 160,
              child: PrimaryButton(text: 'Retry', onPressed: () => _bootstrap()),
            ),
          ],
        ),
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
          // Top Header Bar: Avatar + Welcome Back & Name + Notification Bell
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Citizen Avatar with Online Status
              GestureDetector(
                onTap: () {
                  setState(() {
                    _currentTabIndex = 3; // Jump to Profile
                  });
                },
                child: Stack(
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: AppColors.inputBackground,
                        shape: BoxShape.circle,
                        border: Border.all(color: AppColors.border, width: 1.2),
                      ),
                      child: const Center(
                        child: Icon(
                          FeatherIcons.user,
                          size: 20,
                          color: AppColors.primaryText,
                        ),
                      ),
                    ),
                    Positioned(
                      right: 1,
                      bottom: 1,
                      child: Container(
                        width: 10,
                        height: 10,
                        decoration: BoxDecoration(
                          color: const Color(0xFF10B981),
                          shape: BoxShape.circle,
                          border: Border.all(color: AppColors.background, width: 2),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),

              // Welcome Back & Name
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      LanguageService.t('welcome_back'),
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: AppColors.secondaryText,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      LanguageService.t('hi_user'),
                      style: AppTypography.heading(context).copyWith(
                        fontSize: 20,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.4,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),

              // Notification Bell
              Material(
                color: Colors.transparent,
                shape: const CircleBorder(),
                clipBehavior: Clip.antiAlias,
                child: InkWell(
                  customBorder: const CircleBorder(),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => RecentActivityScreen(issues: _issues),
                      ),
                    );
                  },
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      Container(
                        width: 42,
                        height: 42,
                        decoration: BoxDecoration(
                          color: AppColors.inputBackground,
                          shape: BoxShape.circle,
                          border: Border.all(color: AppColors.border, width: 1.0),
                        ),
                        child: const Center(
                          child: Icon(
                            FeatherIcons.bell,
                            size: 18,
                            color: AppColors.primaryText,
                          ),
                        ),
                      ),
                      Positioned(
                        top: 9,
                        right: 10,
                        child: Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Color(0xFF2563EB),
                            shape: BoxShape.circle,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 18),

          // Search Bar with Feather Icons
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 18.0),
            decoration: BoxDecoration(
              color: AppColors.inputBackground,
              borderRadius: BorderRadius.circular(30.0),
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
                      hintText: LanguageService.t('search_hint'),
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
                        LanguageService.t('welcome_card_title'),
                        style: AppTypography.heading(context).copyWith(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        LanguageService.t('welcome_card_sub'),
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
                LanguageService.t('ongoing_issues'),
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
                  LanguageService.t('view_all'),
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
            _buildEmptyState(
              title: LanguageService.t('no_issues_found'),
              subtitle: LanguageService.t('no_issues_sub'),
              buttonText: LanguageService.t('file_grievance_btn'),
            )
          else
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: filteredIssues.length > 4 ? 4 : filteredIssues.length,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12.0,
                mainAxisSpacing: 12.0,
                childAspectRatio: 0.72,
              ),
              itemBuilder: (context, index) {
                final issue = filteredIssues[index];
                return DashboardIssueCard(
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
  // TAB 1: MY ISSUES (ALL FILED ISSUES - REDESIGNED PER REFERENCE)
  // ---------------------------------------------------------------------------
  Widget _buildMyIssuesTab() {
    final query = _myIssuesSearchController.text.trim().toLowerCase();
    final filteredIssues = _issues.where((issue) {
      final matchesQuery = query.isEmpty ||
          issue.title.toLowerCase().contains(query) ||
          issue.description.toLowerCase().contains(query) ||
          issue.location.toLowerCase().contains(query) ||
          issue.category.toLowerCase().contains(query) ||
          issue.id.toLowerCase().contains(query);

      // Status filter
      bool matchesStatus = true;
      if (_myIssuesStatusFilter == 'Issued') {
        matchesStatus = issue.status == IssueStatus.underReview;
      } else if (_myIssuesStatusFilter == 'In Progress') {
        matchesStatus = issue.status == IssueStatus.inProgress;
      } else if (_myIssuesStatusFilter == 'Resolved') {
        matchesStatus = issue.status == IssueStatus.resolved;
      }

      // Location filter
      bool matchesLocation = true;
      if (_myIssuesLocationFilter != 'All') {
        matchesLocation = issue.location
            .toLowerCase()
            .contains(_myIssuesLocationFilter.toLowerCase());
      }

      // Category filter
      bool matchesCategory = true;
      if (_myIssuesCategoryFilter != 'All') {
        matchesCategory = issue.category
            .toLowerCase()
            .contains(_myIssuesCategoryFilter.toLowerCase());
      }

      return matchesQuery && matchesStatus && matchesLocation && matchesCategory;
    }).toList();

    final hasActiveFilter = _myIssuesStatusFilter != 'All' ||
        _myIssuesLocationFilter != 'All' ||
        _myIssuesCategoryFilter != 'All';

    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Search Bar Pill with Filter Action matching reference image
          Container(
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(30.0),
              border: Border.all(color: AppColors.border, width: 1.0),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 2.0),
            child: Row(
              children: [
                const Icon(
                  FeatherIcons.search,
                  size: 18,
                  color: AppColors.secondaryText,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextField(
                    controller: _myIssuesSearchController,
                    onChanged: (val) => setState(() {}),
                    style: AppTypography.inputText(context).copyWith(fontSize: 14),
                    decoration: InputDecoration(
                      hintText: 'Search grievances, ID, location...',
                      hintStyle: AppTypography.placeholder(context).copyWith(
                        fontSize: 14,
                        color: AppColors.mutedText,
                      ),
                      border: InputBorder.none,
                      isDense: true,
                      contentPadding: const EdgeInsets.symmetric(vertical: 12.0),
                    ),
                  ),
                ),
                Container(
                  width: 1.0,
                  height: 20.0,
                  color: AppColors.border,
                ),
                const SizedBox(width: 10),
                GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: _openFilterBottomSheet,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4.0),
                    child: Icon(
                      FeatherIcons.sliders,
                      size: 16,
                      color: hasActiveFilter
                          ? AppColors.primaryText
                          : AppColors.secondaryText,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 2. Section Filter - Primary Status Segmented Bar
          Container(
            decoration: BoxDecoration(
              color: AppColors.inputBackground,
              borderRadius: BorderRadius.circular(12.0),
              border: Border.all(color: AppColors.border, width: 1.0),
            ),
            padding: const EdgeInsets.all(3.0),
            child: Row(
              children: _myIssuesStatusSections.map((status) {
                final isSelected = _myIssuesStatusFilter == status;
                return Expanded(
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () {
                      setState(() {
                        _myIssuesStatusFilter = status;
                      });
                    },
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 150),
                      padding: const EdgeInsets.symmetric(vertical: 8.0),
                      decoration: BoxDecoration(
                        color: isSelected
                            ? AppColors.primaryButton
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(9.0),
                      ),
                      child: Text(
                        status,
                        textAlign: TextAlign.center,
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 12,
                          fontWeight:
                              isSelected ? FontWeight.w700 : FontWeight.w500,
                          color: isSelected
                              ? AppColors.buttonText
                              : AppColors.secondaryText,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 10),

          // 2b. Location Filter Dropdown (Locations where issues have been filed)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 2.0),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(12.0),
              border: Border.all(color: AppColors.border, width: 1.0),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _availableLocations.contains(_myIssuesLocationFilter == 'All' ? 'All Locations' : _myIssuesLocationFilter)
                    ? (_myIssuesLocationFilter == 'All' ? 'All Locations' : _myIssuesLocationFilter)
                    : 'All Locations',
                isExpanded: true,
                icon: const Icon(
                  FeatherIcons.chevronDown,
                  size: 16,
                  color: AppColors.secondaryText,
                ),
                borderRadius: BorderRadius.circular(12.0),
                dropdownColor: AppColors.background,
                items: _availableLocations.map((loc) {
                  final isAll = loc == 'All Locations';
                  final isSelected = (_myIssuesLocationFilter == 'All' && isAll) ||
                      _myIssuesLocationFilter == loc;
                  return DropdownMenuItem<String>(
                    value: loc,
                    child: Row(
                      children: [
                        Icon(
                          isAll ? FeatherIcons.map : FeatherIcons.mapPin,
                          size: 14,
                          color: isSelected ? AppColors.primaryText : AppColors.secondaryText,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            loc,
                            style: AppTypography.supporting(context).copyWith(
                              fontSize: 13.5,
                              fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                              color: AppColors.primaryText,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      _myIssuesLocationFilter = val == 'All Locations' ? 'All' : val;
                    });
                  }
                },
              ),
            ),
          ),

          const SizedBox(height: 18),

          // 3. Locality / Ward Title Header matching reference image
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  _myIssuesLocationFilter != 'All'
                      ? _myIssuesLocationFilter
                      : 'All Reported Locations',
                  style: AppTypography.heading(context).copyWith(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (hasActiveFilter)
                    GestureDetector(
                      onTap: () {
                        setState(() {
                          _myIssuesStatusFilter = 'All';
                          _myIssuesLocationFilter = 'All';
                          _myIssuesCategoryFilter = 'All';
                          _myIssuesSearchController.clear();
                        });
                      },
                      child: Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: Text(
                          'Clear',
                          style: AppTypography.supporting(context).copyWith(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.secondaryText,
                          ),
                        ),
                      ),
                    ),
                  Text(
                    '${filteredIssues.length} issues',
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 14.5,
                      fontWeight: FontWeight.w600,
                      color: AppColors.secondaryText,
                    ),
                  ),
                ],
              ),
            ],
          ),

          const SizedBox(height: 14),

          // 4. Issue Cards List
          if (filteredIssues.isEmpty)
            _buildEmptyState(
              title: 'No Issues Found',
              subtitle: 'All clear in your selected area.',
              showButton: false,
            )
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: filteredIssues.length,
              itemBuilder: (context, index) {
                final issue = filteredIssues[index];
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
  final TextEditingController _formFullNameController = TextEditingController();
  final TextEditingController _formEmailController = TextEditingController();
  final TextEditingController _formMobileController = TextEditingController();
  final TextEditingController _formAddressController = TextEditingController();
  final TextEditingController _formCityWardController = TextEditingController();
  final TextEditingController _formPincodeController = TextEditingController();
  final TextEditingController _formTitleController = TextEditingController();
  final TextEditingController _formDescriptionController = TextEditingController();

  bool _formHasAttachedMedia = false;
  bool _formIsLocationShared = false;
  bool _isSubmittingForm = false;
  String? _formError;

  Future<void> _requestLocationPermission() async {
    final bool? granted = await showDialog<bool>(
      context: context,
      builder: (BuildContext ctx) {
        return Dialog(
          backgroundColor: AppColors.background,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.0),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppColors.inputBackground,
                    shape: BoxShape.circle,
                    border: Border.all(color: AppColors.border),
                  ),
                  child: const Icon(
                    FeatherIcons.mapPin,
                    size: 22,
                    color: AppColors.primaryText,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Allow JanSeva to access this device\'s location?',
                  textAlign: TextAlign.center,
                  style: AppTypography.heading(context).copyWith(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Precise GPS location is used to pinpoint civic issues and dispatch departmental response teams directly to the site.',
                  textAlign: TextAlign.center,
                  style: AppTypography.supporting(context).copyWith(
                    fontSize: 12.5,
                    color: AppColors.secondaryText,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primaryButton,
                      foregroundColor: AppColors.buttonText,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12.0),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 12.0),
                      elevation: 0,
                    ),
                    onPressed: () => Navigator.pop(ctx, true),
                    child: const Text(
                      'While Using the App',
                      style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13.5),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: TextButton(
                    style: TextButton.styleFrom(
                      foregroundColor: AppColors.secondaryText,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12.0),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 10.0),
                    ),
                    onPressed: () => Navigator.pop(ctx, false),
                    child: const Text(
                      'Don\'t Allow',
                      style: TextStyle(fontWeight: FontWeight.w500, fontSize: 13.5),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );

    if (granted == true) {
      setState(() {
        _formIsLocationShared = true;
        _formAddressController.text = 'Near Anna Nagar Junction, 2nd Avenue';
        _formCityWardController.text = 'Ward 4, Zone 2';
        _formPincodeController.text = '600040';
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Location permission granted! Address details auto-filled from GPS.'),
            duration: Duration(seconds: 3),
          ),
        );
      }
    } else if (granted == false) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Location permission denied. Please enter address manually.'),
            duration: Duration(seconds: 3),
          ),
        );
      }
    }
  }

  Future<void> _onFormSubmit() async {
    final titleText = _formTitleController.text.trim();
    final descriptionText = _formDescriptionController.text.trim();

    setState(() => _formError = null);

    if (titleText.length < 5) {
      setState(() => _formError = 'Title must be at least 5 characters.');
      return;
    }
    if (descriptionText.length < 20) {
      setState(() => _formError = 'Please describe the issue in at least 20 characters.');
      return;
    }
    if (_selectedArea == null) {
      setState(() => _formError = 'Select an area so the report reaches the right office.');
      return;
    }

    // Media attachment is captured in the UI but the backend has no upload
    // endpoint for it yet — see the integration report. It is never sent as
    // if it were part of the submission.

    setState(() => _isSubmittingForm = true);
    try {
      final challenge = await ChallengeRepository.instance.createChallenge(
        title: titleText,
        description: descriptionText,
        administrativeAreaId: _selectedArea!.id,
        pinCode: _formPincodeController.text.trim().isEmpty ? null : _formPincodeController.text.trim(),
      );
      final newIssue = IssueItem.fromChallenge(challenge, areaName: _selectedArea!.name);

      if (!mounted) return;
      final result = await Navigator.push<String>(
        context,
        MaterialPageRoute(
          builder: (context) => IssueSuccessScreen(createdIssue: newIssue),
        ),
      );

      if (!mounted) return;
      setState(() {
        _issues.insert(0, newIssue);
        _formTitleController.clear();
        _formDescriptionController.clear();
        _formHasAttachedMedia = false;
        if (result == 'file_another') {
          _currentTabIndex = 2; // Stay on File Grievance tab
        } else {
          _currentTabIndex = 0; // Switch to Home tab
        }
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _formError = e.userMessage);
    } finally {
      if (mounted) setState(() => _isSubmittingForm = false);
    }
  }

  Widget _buildFileGrievanceTab() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top Heading Bar
          _buildFormTopBar(),

          const SizedBox(height: 18),

          // SECTION 1: Personal Info
          _buildFormSectionHeader(1, LanguageService.t('step1_title')),
          const SizedBox(height: 12),

          _buildFormInputField(
            controller: _formFullNameController,
            placeholder: 'Full Name (e.g. Dhyan Kannoth)',
            icon: FeatherIcons.user,
          ),
          const SizedBox(height: 10),
          _buildFormInputField(
            controller: _formEmailController,
            placeholder: 'Email Address (e.g. citizen@example.com)',
            icon: FeatherIcons.mail,
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 10),
          _buildFormInputField(
            controller: _formMobileController,
            placeholder: 'Mobile Number (+91 XXXXX XXXXX)',
            icon: FeatherIcons.phone,
            keyboardType: TextInputType.phone,
          ),

          const SizedBox(height: 24),

          // SECTION 2: Location
          _buildFormSectionHeader(
            2,
            LanguageService.t('step2_title'),
            trailing: GestureDetector(
              onTap: _requestLocationPermission,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
                decoration: BoxDecoration(
                  color: AppColors.inputBackground,
                  borderRadius: BorderRadius.circular(6.0),
                  border: Border.all(color: AppColors.border, width: 0.8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _formIsLocationShared ? FeatherIcons.check : FeatherIcons.mapPin,
                      size: 13,
                      color: AppColors.primaryText,
                    ),
                    const SizedBox(width: 5),
                    Text(
                      _formIsLocationShared ? 'GPS Linked' : 'Use GPS',
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 11.5,
                        fontWeight: FontWeight.w600,
                        color: AppColors.primaryText,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),

          _buildFormInputField(
            controller: _formAddressController,
            placeholder: 'Address (House no., Street name)',
            icon: FeatherIcons.mapPin,
            suffixIcon: FeatherIcons.crosshair,
            onSuffixTap: _requestLocationPermission,
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
          const SizedBox(height: 10),

          // Administrative area — required by the backend to route the
          // report; there is no pincode/GPS-to-area lookup on the server, so
          // this is a small, explicit picker rather than a guess.
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 2.0),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(12.0),
              border: Border.all(color: AppColors.border, width: 1.0),
            ),
            child: Row(
              children: [
                const Icon(FeatherIcons.mapPin, size: 18, color: AppColors.secondaryText),
                const SizedBox(width: 12),
                Expanded(
                  child: _areas.isEmpty
                      ? Padding(
                          padding: const EdgeInsets.symmetric(vertical: 13.0),
                          child: Text(
                            'No administrative areas available yet',
                            style: AppTypography.placeholder(context).copyWith(fontSize: 14, color: AppColors.mutedText),
                          ),
                        )
                      : DropdownButtonHideUnderline(
                          child: DropdownButton<AdministrativeArea>(
                            value: _selectedArea,
                            isExpanded: true,
                            hint: Text(
                              'Select area',
                              style: AppTypography.placeholder(context).copyWith(fontSize: 14, color: AppColors.mutedText),
                            ),
                            items: _areas
                                .map((a) => DropdownMenuItem(value: a, child: Text(a.label, style: AppTypography.inputText(context).copyWith(fontSize: 14))))
                                .toList(),
                            onChanged: (a) => setState(() => _selectedArea = a),
                          ),
                        ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // SECTION 3: Issue Details
          _buildFormSectionHeader(3, LanguageService.t('step3_title')),
          const SizedBox(height: 12),

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
            maxLines: 4,
          ),

          const SizedBox(height: 24),

          // SECTION 4: Upload or Click Photo (Optional)
          _buildFormSectionHeader(4, LanguageService.t('step4_title')),
          const SizedBox(height: 12),

          MediaUploadCard(
            onMediaSelected: (hasPhoto) {
              setState(() => _formHasAttachedMedia = hasPhoto);
            },
          ),
          if (_formHasAttachedMedia) ...[
            const SizedBox(height: 8),
            Text(
              'Photos are not yet sent with the report — the backend does not support attachments yet.',
              style: AppTypography.supporting(context).copyWith(fontSize: 11.5, color: AppColors.mutedText),
            ),
          ],

          if (_formError != null) ...[
            const SizedBox(height: 16),
            Text(
              _formError!,
              style: AppTypography.supporting(context).copyWith(color: Colors.red, fontSize: 13),
            ),
          ],

          const SizedBox(height: 24),

          PrimaryButton(
            text: _isSubmittingForm ? 'Submitting…' : LanguageService.t('submit_grievance'),
            isEnabled: !_isSubmittingForm,
            onPressed: () => _onFormSubmit(),
          ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // Top Bar with centered title and back button
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
          child: Center(
            child: Text(
              LanguageService.t('nav_file'),
              style: AppTypography.heading(context).copyWith(
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
        const SizedBox(width: 36), // Balances the leading back button for true centering
      ],
    );
  }

  // Monochromatic Numbered step badge + section heading
  Widget _buildFormSectionHeader(int step, String title, {Widget? trailing}) {
    return Row(
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: const BoxDecoration(
            color: AppColors.primaryButton,
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
        Expanded(
          child: Text(
            title,
            style: AppTypography.heading(context).copyWith(
              fontSize: 15,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        ?trailing,
      ],
    );
  }

  // Input Field with leading icon matching reference image
  Widget _buildFormInputField({
    required TextEditingController controller,
    required String placeholder,
    required IconData icon,
    IconData? suffixIcon,
    VoidCallback? onSuffixTap,
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
          if (suffixIcon != null)
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: onSuffixTap,
              child: Padding(
                padding: const EdgeInsets.only(left: 6.0),
                child: Icon(
                  suffixIcon,
                  size: 18,
                  color: AppColors.primaryText,
                ),
              ),
            ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 3: PROFILE
  // ---------------------------------------------------------------------------
  Future<void> _onLogout() async {
    await AuthRepository.instance.logout();
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => const WelcomeLanguageScreen()),
      (route) => false,
    );
  }

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
            _currentUser?.name ?? 'Citizen',
            style: AppTypography.heading(context).copyWith(
              fontSize: 22,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Verified Citizen',
            style: AppTypography.supporting(context).copyWith(
              fontSize: 13,
              color: AppColors.secondaryText,
            ),
          ),

          const SizedBox(height: 24),

          // Stats Row — computed from the citizen's real challenges.
          Row(
            children: [
              _buildStatItem(LanguageService.t('reported'), '${_issues.length}'),
              const SizedBox(width: 10),
              _buildStatItem(
                LanguageService.t('in_progress_count'),
                '${_issues.where((i) => i.status == IssueStatus.inProgress).length}',
              ),
              const SizedBox(width: 10),
              _buildStatItem(
                LanguageService.t('resolved_count'),
                '${_issues.where((i) => i.status == IssueStatus.resolved).length}',
              ),
            ],
          ),

          const SizedBox(height: 24),
          const Divider(height: 1, thickness: 1, color: AppColors.divider),
          const SizedBox(height: 20),

          // Profile Actions
          _buildProfileOption(
            icon: FeatherIcons.phone,
            title: LanguageService.t('phone_number'),
            subtitle: _currentUser?.phone ?? 'Not available',
            onTap: () {},
          ),
          _buildProfileOption(
            icon: FeatherIcons.mail,
            title: LanguageService.t('email_address'),
            // The backend citizen account has no email field at all.
            subtitle: 'Not provided',
            onTap: () {},
          ),
          _buildProfileOption(
            icon: FeatherIcons.settings,
            title: LanguageService.t('settings_notif'),
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
            title: LanguageService.t('logout'),
            subtitle: 'Sign out of Social Serve',
            onTap: () => _onLogout(),
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

  Widget _buildEmptyState({
    String title = 'No Issues Found',
    String subtitle = 'All clear in your selected area. Have a municipal concern to report?',
    String buttonText = 'File a Grievance',
    bool showButton = true,
    double animationHeight = 280,
  }) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 28.0, horizontal: 20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Centered Lottie Animation with fallback
            SizedBox(
              height: animationHeight,
              child: Lottie.asset(
                'lib/assets/no_issues_found.json',
                fit: BoxFit.contain,
                errorBuilder: (context, error, stackTrace) {
                  return Lottie.asset(
                    'assets/animations/no_issues_found.json',
                    fit: BoxFit.contain,
                    errorBuilder: (context, err2, stack2) {
                      return const Icon(
                        FeatherIcons.checkCircle,
                        size: 80,
                        color: AppColors.primaryText,
                      );
                    },
                  );
                },
              ),
            ),
            const SizedBox(height: 16),

            // Headline Message
            Text(
              title,
              textAlign: TextAlign.center,
              style: AppTypography.heading(context).copyWith(
                fontSize: 22,
                fontWeight: FontWeight.w700,
                letterSpacing: -0.4,
              ),
            ),
            const SizedBox(height: 8),

            // Sub-Message
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: AppTypography.supporting(context).copyWith(
                fontSize: 14.5,
                color: AppColors.secondaryText,
                height: 1.35,
              ),
            ),

            if (showButton) ...[
              const SizedBox(height: 20),
              SizedBox(
                width: 220,
                child: PrimaryButton(
                  text: buttonText,
                  onPressed: _onFileIssuePressed,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
