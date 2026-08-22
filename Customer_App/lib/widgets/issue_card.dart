import 'package:flutter/material.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';

class IssueCard extends StatelessWidget {
  final IssueItem issue;
  final VoidCallback onTap;

  const IssueCard({
    super.key,
    required this.issue,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(14.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14.0),
        child: Padding(
          padding: const EdgeInsets.all(18.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Category tag and status badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    issue.category.toUpperCase(),
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.8,
                      color: AppColors.mutedText,
                    ),
                  ),
                  _buildMonochromeStatusBadge(context, issue.status),
                ],
              ),
              const SizedBox(height: 10),

              // Title
              Text(
                issue.title,
                style: AppTypography.heading(context).copyWith(
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  height: 1.25,
                ),
              ),
              const SizedBox(height: 12),

              // Location and Date
              Row(
                children: [
                  const Icon(
                    Icons.location_on_outlined,
                    size: 14,
                    color: AppColors.secondaryText,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      issue.location,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 13,
                        color: AppColors.secondaryText,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Filed ${issue.dateFiled}',
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 12,
                      color: AppColors.mutedText,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMonochromeStatusBadge(
      BuildContext context, IssueStatus status) {
    Color dotColor;
    Color textColor;
    Color bgColor;

    switch (status) {
      case IssueStatus.underReview:
        dotColor = AppColors.secondaryText;
        textColor = AppColors.primaryText;
        bgColor = AppColors.inputBackground;
        break;
      case IssueStatus.inProgress:
        dotColor = AppColors.primaryText;
        textColor = AppColors.primaryText;
        bgColor = AppColors.border;
        break;
      case IssueStatus.resolved:
        dotColor = const Color(0xFF333333);
        textColor = AppColors.primaryText;
        bgColor = AppColors.inputBackground;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20.0),
        border: Border.all(color: AppColors.border, width: 0.8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            status.label,
            style: AppTypography.supporting(context).copyWith(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: textColor,
            ),
          ),
          const SizedBox(width: 6),
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: dotColor,
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }
}
