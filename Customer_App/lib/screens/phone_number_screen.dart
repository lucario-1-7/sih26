import 'package:flutter/material.dart';
import '../core/networking/api_exception.dart';
import '../data/repositories/auth_repository.dart';
import '../services/language_service.dart';
import '../services/theme_service.dart';
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
  final _authRepo = AuthRepository.instance;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _onContinue() async {
    final rawPhone = _phoneController.text.trim();
    if (rawPhone.length < 10) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(LanguageService.t('enter_phone'))),
      );
      return;
    }

    final backendPhone = rawPhone.startsWith('+') ? rawPhone : '+91$rawPhone';
    final displayPhone = rawPhone.startsWith('+') ? rawPhone : '+91 $rawPhone';

    setState(() => _isSubmitting = true);
    try {
      await _authRepo.requestOtp(backendPhone);
      if (!mounted) return;
      Navigator.push(
        context,
        SmoothPageRoute(
          child: OtpVerificationScreen(
            phoneNumber: displayPhone,
            backendPhone: backendPhone,
          ),
        ),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.userMessage)),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(LanguageService.t('enter_phone'))),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([ThemeService.instance, LanguageService.instance]),
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
          bottomCta: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              PrimaryButton(
                text: _isSubmitting ? 'Sending OTP…' : LanguageService.t('continue_btn'),
                isEnabled: !_isSubmitting,
                onPressed: _onContinue,
              ),
            ],
          ),
        );
      },
    );
  }
}

