import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/auth_screen_layout.dart';
import '../widgets/otp_input.dart';
import '../widgets/primary_button.dart';
import '../widgets/smooth_page_route.dart';
import 'onboarding_screen.dart';

class OtpVerificationScreen extends StatefulWidget {
  final String phoneNumber;

  const OtpVerificationScreen({
    super.key,
    required this.phoneNumber,
  });

  @override
  State<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends State<OtpVerificationScreen> {
  void _onVerify() {
    Navigator.push(
      context,
      SmoothPageRoute(
        child: const OnboardingScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AuthScreenLayout(
      currentStep: 2,
      totalSteps: 6,
      showBack: true,
      onBack: () => Navigator.pop(context),
      heading: 'Enter verification code',
      supportingWidget: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Enter the 6-digit code sent to your phone number',
            style: AppTypography.supporting(context),
          ),
          const SizedBox(height: 4),
          Text(
            widget.phoneNumber,
            style: AppTypography.phoneHighlight(context),
          ),
        ],
      ),
      middleContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 6-digit OTP Input
          const OtpInput(
            length: 6,
          ),

          const SizedBox(height: 24),

          // Resend Section
          Center(
            child: Column(
              children: [
                Text(
                  "Didn't receive the code?",
                  style: AppTypography.supporting(context),
                ),
                const SizedBox(height: 4),
                GestureDetector(
                  onTap: () {
                    // Visual feedback only for UI demo
                  },
                  child: Text(
                    'Resend code',
                    style: AppTypography.link(context),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      bottomCta: PrimaryButton(
        text: 'Verify',
        isEnabled: true,
        onPressed: _onVerify,
      ),
    );
  }
}
