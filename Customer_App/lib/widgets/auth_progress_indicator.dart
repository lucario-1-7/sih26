import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class AuthProgressIndicator extends StatelessWidget {
  final int currentStep;
  final int totalSteps;

  const AuthProgressIndicator({
    super.key,
    required this.currentStep,
    this.totalSteps = 2,
  });

  @override
  Widget build(BuildContext context) {
    final progressFraction = (currentStep / totalSteps).clamp(0.0, 1.0);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final totalWidth = constraints.maxWidth;
          return Container(
            height: 2.0,
            width: double.infinity,
            decoration: BoxDecoration(
              color: AppColors.border,
              borderRadius: BorderRadius.circular(1.0),
            ),
            child: Stack(
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeInOut,
                  width: totalWidth * progressFraction,
                  height: 2.0,
                  decoration: BoxDecoration(
                    color: AppColors.primaryText,
                    borderRadius: BorderRadius.circular(1.0),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
