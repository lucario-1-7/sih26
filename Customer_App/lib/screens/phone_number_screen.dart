import 'package:flutter/material.dart';
import '../services/language_service.dart';
import '../theme/app_theme.dart';
import '../widgets/auth_screen_layout.dart';
import '../widgets/phone_number_input.dart';
import '../widgets/primary_button.dart';
import '../widgets/smooth_page_route.dart';
import 'otp_verification_screen.dart';

class PhoneNumberScreen extends StatefulWidget {
  const PhoneNumberScreen({super.key});

  @override
  State<PhoneNumberScreen> createState() => _PhoneNumberScreenState();
}

class _PhoneNumberScreenState extends State<PhoneNumberScreen> {
  final TextEditingController _phoneController = TextEditingController();

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  void _onContinue() {
    final phoneNumber = _phoneController.text.trim().isNotEmpty
        ? '+91 ${_phoneController.text.trim()}'
        : '+91 ••••• •••••';

    Navigator.push(
      context,
      SmoothPageRoute(
        child: OtpVerificationScreen(phoneNumber: phoneNumber),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: LanguageService.instance,
      builder: (context, _) {
        return AuthScreenLayout(
          currentStep: 1,
          totalSteps: 6,
          showBack: true,
          onBack: () => Navigator.pop(context),
          heading: LanguageService.t('enter_phone'),
          supportingWidget: Text(
            LanguageService.t('phone_sub'),
            style: AppTypography.supporting(context),
          ),
          middleContent: PhoneNumberInput(
            controller: _phoneController,
            countryCode: '+91',
            onSubmitted: (_) => _onContinue(),
          ),
          bottomCta: PrimaryButton(
            text: LanguageService.t('continue_btn'),
            isEnabled: true,
            onPressed: _onContinue,
          ),
        );
      },
    );
  }
}

