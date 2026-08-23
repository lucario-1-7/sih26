import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'auth_header.dart';
import 'auth_progress_indicator.dart';

class AuthScreenLayout extends StatelessWidget {
  final int currentStep;
  final int totalSteps;
  final bool showBack;
  final VoidCallback? onBack;
  final String heading;
  final Widget? supportingWidget;
  final Widget middleContent;
  final Widget bottomCta;

  const AuthScreenLayout({
    super.key,
    required this.currentStep,
    this.totalSteps = 6,
    this.showBack = true,
    this.onBack,
    required this.heading,
    this.supportingWidget,
    required this.middleContent,
    required this.bottomCta,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              physics: const AlwaysScrollableScrollPhysics(
                parent: BouncingScrollPhysics(),
              ),
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight: constraints.maxHeight,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Top Content Group (Header, Progress, Headings, and Input directly below)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        AuthHeader(
                          showBack: showBack,
                          onBack: onBack,
                        ),
                        AuthProgressIndicator(
                          currentStep: currentStep,
                          totalSteps: totalSteps,
                        ),
                        const SizedBox(height: 24),
                        Text(
                          heading,
                          style: AppTypography.heading(context),
                        ),
                        if (supportingWidget != null) ...[
                          const SizedBox(height: 12),
                          supportingWidget!,
                        ],
                        const SizedBox(height: 32),
                        middleContent,
                      ],
                    ),

                    // Bottom CTA Section
                    Padding(
                      padding: const EdgeInsets.only(bottom: 20.0, top: 16.0),
                      child: bottomCta,
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
