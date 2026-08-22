import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';

class IssueDetailScreen extends StatelessWidget {
  final IssueItem issue;

  const IssueDetailScreen({
    super.key,
    required this.issue,
  });

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
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1.0),
          child: Divider(height: 1, thickness: 1, color: AppColors.divider),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header tag & ID
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10.0, vertical: 4.0),
                    decoration: BoxDecoration(
                      color: AppColors.inputBackground,
                      borderRadius: BorderRadius.circular(6.0),
                      border: Border.all(color: AppColors.border, width: 1.0),
                    ),
                    child: Text(
                      issue.category.toUpperCase(),
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.8,
                        color: AppColors.primaryText,
                      ),
                    ),
                  ),
                  Text(
                    issue.id,
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: AppColors.mutedText,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Title
              Text(
                issue.title,
                style: AppTypography.heading(context).copyWith(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  height: 1.25,
                ),
              ),

              const SizedBox(height: 16),

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

              const SizedBox(height: 24),
              const Divider(height: 1, thickness: 1, color: AppColors.divider),
              const SizedBox(height: 24),

              // Status Timeline Section
              Text(
                'Status & Timeline',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 16,
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

              const SizedBox(height: 20),
              const Divider(height: 1, thickness: 1, color: AppColors.divider),
              const SizedBox(height: 24),

              // Description Section
              Text(
                'Description',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 16,
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
                  fontSize: 15,
                  fontWeight:
                      isCurrent || isCompleted ? FontWeight.w600 : FontWeight.w400,
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
