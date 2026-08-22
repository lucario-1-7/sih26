import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';

class DashboardIssueCard extends StatelessWidget {
  final IssueItem issue;
  final bool isFeatured;
  final VoidCallback onTap;

  const DashboardIssueCard({
    super.key,
    required this.issue,
    this.isFeatured = false,
    required this.onTap,
  });

  IconData _getCategoryIcon(String category) {
    final lower = category.toLowerCase();
    if (lower.contains('road') || lower.contains('infra')) {
      return FeatherIcons.mapPin;
    } else if (lower.contains('water') || lower.contains('pipe')) {
      return FeatherIcons.droplet;
    } else if (lower.contains('elect') || lower.contains('light')) {
      return FeatherIcons.zap;
    } else if (lower.contains('waste') || lower.contains('garbage') || lower.contains('sanitation')) {
      return FeatherIcons.trash;
    } else if (lower.contains('health') || lower.contains('med')) {
      return FeatherIcons.heart;
    } else {
      return FeatherIcons.fileText;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bgColor = isFeatured ? AppColors.primaryButton : AppColors.background;
    final primaryTextColor =
        isFeatured ? Colors.white : AppColors.primaryText;
    final secondaryTextColor =
        isFeatured ? const Color(0xFFAAAAAA) : AppColors.secondaryText;
    final borderColor =
        isFeatured ? AppColors.primaryButton : AppColors.border;
    final progressTrackColor =
        isFeatured ? const Color(0xFF333333) : AppColors.inputBackground;
    final progressFillColor =
        isFeatured ? Colors.white : AppColors.primaryText;
    final iconBgColor =
        isFeatured ? const Color(0xFF222222) : AppColors.inputBackground;
    final iconColor =
        isFeatured ? Colors.white : AppColors.primaryText;

    return Container(
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: borderColor, width: 1.0),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16.0),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 13.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Top Row: Category Icon & Date
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Container(
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      color: iconBgColor,
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                    child: Center(
                      child: Icon(
                        _getCategoryIcon(issue.category),
                        size: 15,
                        color: iconColor,
                      ),
                    ),
                  ),
                  Text(
                    issue.dateFiled,
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: secondaryTextColor,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // Title & Category (flexible to avoid vertical overflows)
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      issue.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: AppTypography.heading(context).copyWith(
                        fontSize: 13.5,
                        fontWeight: FontWeight.w600,
                        color: primaryTextColor,
                        height: 1.25,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      issue.category,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 11,
                        color: secondaryTextColor,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 8),

              // Progress Section
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Progress',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w500,
                          color: secondaryTextColor,
                        ),
                      ),
                      Text(
                        '${issue.progressPercent}%',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w700,
                          color: primaryTextColor,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 5),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4.0),
                    child: LinearProgressIndicator(
                      value: issue.progressValue,
                      minHeight: 4,
                      backgroundColor: progressTrackColor,
                      valueColor: AlwaysStoppedAnimation<Color>(progressFillColor),
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
}
