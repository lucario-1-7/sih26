import 'package:flutter/material.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';
import '../widgets/issue_card.dart';
import '../widgets/primary_button.dart';
import '../widgets/side_drawer.dart';
import 'issue_detail_screen.dart';
import 'issue_filing_screen.dart';
import 'profile_screen.dart';
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
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  void initState() {
    super.initState();
    _issues = widget.initialIssues ?? List.from(MockIssueRepository.initialIssues);
  }

  void _onFileIssuePressed() async {
    final newIssue = await Navigator.push<IssueItem>(
      context,
      MaterialPageRoute(
        builder: (context) => const IssueFilingScreen(),
      ),
    );

    if (newIssue != null) {
      setState(() {
        _issues.insert(0, newIssue);
      });
    }
  }

  void _onSelectDrawerRoute(DrawerRoute route) {
    switch (route) {
      case DrawerRoute.home:
        // Already on home/dashboard
        break;
      case DrawerRoute.issues:
        // Scroll to issues or stay on dashboard
        break;
      case DrawerRoute.fileIssue:
        _onFileIssuePressed();
        break;
      case DrawerRoute.profile:
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const ProfileScreen()),
        );
        break;
      case DrawerRoute.settings:
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const SettingsScreen()),
        );
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: AppColors.background,
      drawer: SideDrawer(
        currentRoute: DrawerRoute.home,
        onSelectRoute: _onSelectDrawerRoute,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Top Bar with Monochromatic Hamburger Menu
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () {
                      _scaffoldKey.currentState?.openDrawer();
                    },
                    child: Container(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            width: 22,
                            height: 2.5,
                            color: AppColors.primaryText,
                          ),
                          const SizedBox(height: 4.5),
                          Container(
                            width: 22,
                            height: 2.5,
                            color: AppColors.primaryText,
                          ),
                          const SizedBox(height: 4.5),
                          Container(
                            width: 22,
                            height: 2.5,
                            color: AppColors.primaryText,
                          ),
                        ],
                      ),
                    ),
                  ),
                  Text(
                    'Social Serve',
                    style: AppTypography.heading(context).copyWith(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(width: 38), // Balance spacing
                ],
              ),
            ),

            const Divider(
              height: 1,
              thickness: 1,
              color: AppColors.divider,
            ),

            // Main Scrollable Content
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 24),

                    // Greeting Section
                    Text(
                      'Hello, Dhyan',
                      style: AppTypography.heading(context).copyWith(
                        fontSize: 28,
                        fontWeight: FontWeight.w700,
                        letterSpacing: -0.6,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Track your reported issues and help turn them into solutions.',
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 15,
                        height: 1.4,
                      ),
                    ),

                    const SizedBox(height: 32),

                    // File an Issue CTA Card Section
                    Container(
                      padding: const EdgeInsets.all(20.0),
                      decoration: BoxDecoration(
                        color: AppColors.inputBackground,
                        borderRadius: BorderRadius.circular(16.0),
                        border: Border.all(color: AppColors.border, width: 1.0),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Have an issue to report?',
                            style: AppTypography.heading(context).copyWith(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Tell us about a problem in your community and help get it to the right people.',
                            style: AppTypography.supporting(context).copyWith(
                              fontSize: 14,
                              color: AppColors.secondaryText,
                            ),
                          ),
                          const SizedBox(height: 16),
                          PrimaryButton(
                            text: 'File an Issue',
                            onPressed: _onFileIssuePressed,
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 36),

                    // Issues Header with Counter
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Text(
                          'Your Issues',
                          style: AppTypography.heading(context).copyWith(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12.0,
                            vertical: 4.0,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.primaryText,
                            borderRadius: BorderRadius.circular(20.0),
                          ),
                          child: Text(
                            '${_issues.length}',
                            style: AppTypography.supporting(context).copyWith(
                              fontSize: 13,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Issues List or Empty State
                    if (_issues.isEmpty)
                      _buildEmptyState(context)
                    else
                      ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _issues.length,
                        itemBuilder: (context, index) {
                          final issue = _issues[index];
                          return IssueCard(
                            issue: issue,
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) =>
                                      IssueDetailScreen(issue: issue),
                                ),
                              );
                            },
                          );
                        },
                      ),

                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 40.0, horizontal: 24.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Column(
        children: [
          const Icon(
            Icons.assignment_late_outlined,
            size: 48,
            color: AppColors.mutedText,
          ),
          const SizedBox(height: 16),
          Text(
            'No issues filed yet',
            style: AppTypography.heading(context).copyWith(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Report a problem in your community and track its progress here.',
            textAlign: TextAlign.center,
            style: AppTypography.supporting(context).copyWith(
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: 180,
            child: PrimaryButton(
              text: 'Report an Issue',
              onPressed: _onFileIssuePressed,
            ),
          ),
        ],
      ),
    );
  }
}
