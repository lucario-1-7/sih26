import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';

class DashboardIssueCard extends StatelessWidget {
  final IssueItem issue;
  final VoidCallback onTap;

  const DashboardIssueCard({
    super.key,
    required this.issue,
    required this.onTap,
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
    return Container(
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16.0),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 13.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Row: Category tag on left & Date on right (Consistent colors)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Flexible(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 7.0, vertical: 3.5),
                      decoration: BoxDecoration(
                        color: AppColors.inputBackground,
                        borderRadius: BorderRadius.circular(6.0),
                      ),
                      child: Text(
                        issue.category.toUpperCase(),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 9.0,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.4,
                          color: AppColors.secondaryText,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    issue.dateFiled,
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: AppColors.secondaryText,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // Title (shortened to 2 lines max)
              Text(
                issue.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: AppTypography.heading(context).copyWith(
                  fontSize: 13.5,
                  fontWeight: FontWeight.w600,
                  color: AppColors.primaryText,
                  height: 1.25,
                ),
              ),

              const SizedBox(height: 3),

              // Subtitle / Location (shortened to 1 line)
              Text(
                issue.location,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 11,
                  color: AppColors.secondaryText,
                ),
              ),

              const SizedBox(height: 6),

              // Animation Area: Centered in the middle-bottom with ample size
              Expanded(
                child: Center(
                  child: SizedBox(
                    height: 90,
                    width: double.infinity,
                    child: _buildLottieAnimation(issue.category),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
