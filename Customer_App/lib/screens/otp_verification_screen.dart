import 'package:flutter/material.dart';
import '../services/language_service.dart';
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
    return AnimatedBuilder(
      animation: LanguageService.instance,
      builder: (context, _) {
        return AuthScreenLayout(
          currentStep: 2,
          totalSteps: 6,
          showBack: true,
          onBack: () => Navigator.pop(context),
          heading: LanguageService.t('enter_otp'),
          supportingWidget: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                LanguageService.t('otp_sub'),
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
                      LanguageService.t('didnt_receive'),
                      style: AppTypography.supporting(context),
                    ),
                    const SizedBox(height: 4),
                    GestureDetector(
                      onTap: () {
                        // Visual feedback only for UI demo
                      },
                      child: Text(
                        LanguageService.t('resend'),
                        style: AppTypography.link(context),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          bottomCta: PrimaryButton(
            text: LanguageService.t('verify'),
            isEnabled: true,
            onPressed: _onVerify,
          ),
        );
      },
    );
  }
}

