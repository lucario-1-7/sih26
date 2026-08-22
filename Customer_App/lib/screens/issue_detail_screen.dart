import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';

class IssueDetailScreen extends StatelessWidget {
  final IssueItem issue;

  const IssueDetailScreen({
    super.key,
    required this.issue,
  });

  String _getCategoryAnimation(String category) {
    final lower = category.toLowerCase();
    if (lower.contains('water') ||
        lower.contains('pipe') ||
        lower.contains('drain') ||
        lower.contains('leak') ||
        lower.contains('sewage')) {
      return 'assets/animations/water.json';
    } else if (lower.contains('elect') ||
        lower.contains('light') ||
        lower.contains('power') ||
        lower.contains('energy') ||
        lower.contains('wire')) {
      return 'assets/animations/energy.json';
    } else if (lower.contains('sanitat') ||
        lower.contains('waste') ||
        lower.contains('garbage') ||
        lower.contains('trash') ||
        lower.contains('clean')) {
      return 'assets/animations/sanitation.json';
    } else if (lower.contains('road') ||
        lower.contains('infra') ||
        lower.contains('pothole') ||
        lower.contains('bridge') ||
        lower.contains('traffic') ||
        lower.contains('street') ||
        lower.contains('urban')) {
      return 'assets/animations/urban_infrastructure.json';
    } else if (lower.contains('health') ||
        lower.contains('med') ||
        lower.contains('hosp') ||
        lower.contains('clinic')) {
      return 'assets/animations/healthcare.json';
    } else if (lower.contains('edu') ||
        lower.contains('school') ||
        lower.contains('college')) {
      return 'assets/animations/education.json';
    } else if (lower.contains('agri') ||
        lower.contains('farm') ||
        lower.contains('crop')) {
      return 'assets/animations/Agriculture.json';
    } else if (lower.contains('access') ||
        lower.contains('disab') ||
        lower.contains('ramp')) {
      return 'assets/animations/accesibility.json';
    } else {
      return 'assets/animations/public_administration.json';
    }
  }

  Widget _buildLottieAnimation(String category) {
    final primaryPath = _getCategoryAnimation(category);
    final fallbackPath = primaryPath.startsWith('assets/animations/')
        ? primaryPath.replaceFirst('assets/animations/', 'lib/assets/')
        : primaryPath.replaceFirst('lib/assets/', 'assets/animations/');

    return Lottie.asset(
      primaryPath,
      fit: BoxFit.contain,
      repeat: true,
      errorBuilder: (context, error, stackTrace) {
        return Lottie.asset(
          fallbackPath,
          fit: BoxFit.contain,
          repeat: true,
          errorBuilder: (context, err2, stack2) {
            return const SizedBox.shrink();
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(FeatherIcons.arrowLeft, color: AppColors.primaryText),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Issue Details',
          style: AppTypography.heading(context).copyWith(
            fontSize: 18,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title (Issue Name)
              Text(
                issue.title,
                style: AppTypography.heading(context).copyWith(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  height: 1.25,
                ),
              ),

              const SizedBox(height: 8),

              // Location and Date Row
              Row(
                children: [
                  const Icon(
                    FeatherIcons.mapPin,
                    size: 14,
                    color: AppColors.secondaryText,
                  ),
                  const SizedBox(width: 5),
                  Expanded(
                    child: Text(
                      issue.location,
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 14,
                        color: AppColors.secondaryText,
                      ),
                    ),
                  ),
                  Text(
                    'Filed ${issue.dateFiled}',
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 13,
                      color: AppColors.mutedText,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Domain Animation (Blending with background)
              SizedBox(
                width: double.infinity,
                height: 210,
                child: Center(
                  child: _buildLottieAnimation(issue.category),
                ),
              ),

              const SizedBox(height: 20),

              // 1. Description Section (Followed by description)
              Text(
                'Description',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                issue.description,
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 15,
                  height: 1.45,
                  color: AppColors.primaryText,
                ),
              ),

              const SizedBox(height: 28),

              // 2. Status & Timeline Section (Lastly Status and timeline)
              Text(
                'Status & Timeline',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 16),
              _buildTimelineStep(
                context: context,
                title: 'Issue Submitted',
                subtitle: 'Grievance recorded and assigned reference ${issue.id}',
                isCompleted: true,
                isCurrent: issue.status == IssueStatus.underReview,
              ),
              _buildTimelineStep(
                context: context,
                title: 'Under Departmental Review',
                subtitle: 'Triaged and routed to Municipal Field Engineering Team',
                isCompleted: issue.status == IssueStatus.inProgress ||
                    issue.status == IssueStatus.resolved,
                isCurrent: issue.status == IssueStatus.underReview,
              ),
              _buildTimelineStep(
                context: context,
                title: 'In Progress',
                subtitle: 'Field team dispatched for ground inspection & repair',
                isCompleted: issue.status == IssueStatus.resolved,
                isCurrent: issue.status == IssueStatus.inProgress,
              ),
              _buildTimelineStep(
                context: context,
                title: 'Resolved',
                subtitle: 'Work verified and grievance marked complete',
                isCompleted: issue.status == IssueStatus.resolved,
                isCurrent: issue.status == IssueStatus.resolved,
                isLast: true,
              ),

              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTimelineStep({
    required BuildContext context,
    required String title,
    required String subtitle,
    required bool isCompleted,
    required bool isCurrent,
    bool isLast = false,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 18,
              height: 18,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isCompleted
                    ? AppColors.primaryText
                    : isCurrent
                        ? AppColors.background
                        : AppColors.inputBackground,
                border: Border.all(
                  color: isCompleted || isCurrent
                      ? AppColors.primaryText
                      : AppColors.border,
                  width: 2.0,
                ),
              ),
              child: isCompleted
                  ? const Icon(
                      FeatherIcons.check,
                      size: 11,
                      color: Colors.white,
                    )
                  : isCurrent
                      ? Center(
                          child: Container(
                            width: 6,
                            height: 6,
                            decoration: const BoxDecoration(
                              shape: BoxShape.circle,
                              color: AppColors.primaryText,
                            ),
                          ),
                        )
                      : null,
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 44,
                color: isCompleted ? AppColors.primaryText : AppColors.divider,
              ),
          ],
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: AppTypography.heading(context).copyWith(
                  fontSize: 15.5,
                  fontWeight:
                      isCurrent || isCompleted ? FontWeight.w600 : FontWeight.w500,
                  color: isCurrent || isCompleted
                      ? AppColors.primaryText
                      : AppColors.mutedText,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 13,
                  color: AppColors.secondaryText,
                ),
              ),
              const SizedBox(height: 18),
            ],
          ),
        ),
      ],
    );
  }
}
