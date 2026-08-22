import 'package:flutter/material.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';
import '../widgets/primary_button.dart';

class IssueSuccessScreen extends StatelessWidget {
  final IssueItem createdIssue;

  const IssueSuccessScreen({
    super.key,
    required this.createdIssue,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Spacer(flex: 2),

              // Success Icon Container
              Container(
                width: 80,
                height: 80,
                decoration: const BoxDecoration(
                  color: AppColors.primaryButton,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.check_rounded,
                  color: Colors.white,
                  size: 44,
                ),
              ),

              const SizedBox(height: 28),

              // Title
              Text(
                'Issue Submitted',
                textAlign: TextAlign.center,
                style: AppTypography.heading(context).copyWith(
                  fontSize: 26,
                  fontWeight: FontWeight.w700,
                ),
              ),

              const SizedBox(height: 12),

              // Supporting text
              Text(
                'Your issue has been recorded and will be reviewed by the appropriate department.',
                textAlign: TextAlign.center,
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 15,
                  height: 1.4,
                ),
              ),

              const SizedBox(height: 24),

              // Issue details card preview
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: AppColors.inputBackground,
                  borderRadius: BorderRadius.circular(12.0),
                  border: Border.all(color: AppColors.border, width: 1.0),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'REFERENCE ID',
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: AppColors.mutedText,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      createdIssue.id,
                      style: AppTypography.phoneHighlight(context).copyWith(
                        fontSize: 15,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      createdIssue.title,
                      style: AppTypography.heading(context).copyWith(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),

              const Spacer(flex: 3),

              // View My Issues CTA Button
              PrimaryButton(
                text: 'View My Issues',
                onPressed: () {
                  Navigator.pop(context, createdIssue);
                },
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
