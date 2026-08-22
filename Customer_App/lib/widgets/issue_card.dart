import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
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

  List<String> _getIssueTags() {
    final lower = '${issue.category} ${issue.title}'.toLowerCase();
    final tags = <String>[];
    if (lower.contains('road') || lower.contains('infra') || lower.contains('pothole')) {
      tags.addAll(['Roads', 'Infra']);
    } else if (lower.contains('water') || lower.contains('pipe') || lower.contains('drain')) {
      tags.addAll(['Water', 'Utilities']);
    } else if (lower.contains('elect') || lower.contains('light') || lower.contains('power')) {
      tags.addAll(['Electric', 'Lighting']);
    } else if (lower.contains('waste') || lower.contains('garbage') || lower.contains('sanitation')) {
      tags.addAll(['Sanitation', 'Cleanliness']);
    } else {
      tags.addAll(['Civic', 'Public']);
    }
    return tags;
  }

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
    final tags = _getIssueTags();

    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16.0),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Left Content Column
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title
                    Text(
                      issue.title,
                      style: AppTypography.heading(context).copyWith(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        height: 1.25,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 6),

                    // Location
                    Text(
                      issue.location,
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 13,
                        color: AppColors.secondaryText,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),

                    // Date Filed
                    Text(
                      'Filed ${issue.dateFiled}',
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 12,
                        color: AppColors.mutedText,
                      ),
                    ),
                    const SizedBox(height: 10),

                    // Hashtag chips
                    Wrap(
                      spacing: 6.0,
                      runSpacing: 4.0,
                      children: tags.map(
                        (tag) => Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
                          decoration: BoxDecoration(
                            color: AppColors.inputBackground,
                            borderRadius: BorderRadius.circular(8.0),
                          ),
                          child: Text(
                            tag,
                            style: AppTypography.supporting(context).copyWith(
                              fontSize: 11.5,
                              fontWeight: FontWeight.w600,
                              color: AppColors.secondaryText,
                            ),
                          ),
                        ),
                      ).toList(),
                    ),
                  ],
                ),
              ),

              const SizedBox(width: 12),

              // Right-hand side Domain Lottie Animation (0.8km section removed)
              SizedBox(
                width: 82,
                height: 82,
                child: _buildLottieAnimation(issue.category),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
