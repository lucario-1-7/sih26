import 'package:flutter/material.dart';
import '../core/networking/api_exception.dart';
import '../data/repositories/auth_repository.dart';
import '../services/language_service.dart';
import '../services/theme_service.dart';
import '../theme/app_theme.dart';
import '../widgets/auth_screen_layout.dart';
import '../widgets/otp_input.dart';
import '../widgets/primary_button.dart';
import '../widgets/smooth_page_route.dart';
import 'onboarding_screen.dart';

class OtpVerificationScreen extends StatefulWidget {
  final String phoneNumber;

  /// The backend-formatted phone (e.g. "+919876543210") — kept distinct from
  /// [phoneNumber], which is the "+91 98765 43210" display string.
  final String backendPhone;

  const OtpVerificationScreen({
    super.key,
    required this.phoneNumber,
    required this.backendPhone,
  });

  @override
  State<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends State<OtpVerificationScreen> {
  String _enteredOtp = '';
  bool _isVerifying = false;
  bool _isResending = false;
  String? _errorText;

  Future<void> _onVerify() async {
    if (_enteredOtp.length != 6) {
      setState(() => _errorText = 'Enter the 6-digit code.');
      return;
    }
    setState(() {
      _isVerifying = true;
      _errorText = null;
    });
    try {
      await AuthRepository.instance.verifyOtp(phone: widget.backendPhone, code: _enteredOtp);
      if (!mounted) return;
      Navigator.push(
        context,
        SmoothPageRoute(
          child: const OnboardingScreen(),
        ),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _errorText = e.userMessage);
    } finally {
      if (mounted) setState(() => _isVerifying = false);
    }
  }

  Future<void> _onResend() async {
    setState(() => _isResending = true);
    try {
      await AuthRepository.instance.requestOtp(widget.backendPhone);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('A new code has been sent.')));
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.userMessage)));
    } finally {
      if (mounted) setState(() => _isResending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([ThemeService.instance, LanguageService.instance]),
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
              OtpInput(
                length: 6,
                onChanged: (value) => setState(() {
                  _enteredOtp = value;
                  _errorText = null;
                }),
                onCompleted: (_) => _onVerify(),
              ),

              if (_errorText != null) ...[
                const SizedBox(height: 10),
                Text(
                  _errorText!,
                  style: AppTypography.supporting(context).copyWith(color: Colors.red),
                ),
              ],

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
                      onTap: _isResending ? null : () => _onResend(),
                      child: Text(
                        _isResending ? 'Sending…' : LanguageService.t('resend'),
                        style: AppTypography.link(context),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          bottomCta: PrimaryButton(
            text: _isVerifying ? 'Verifying…' : LanguageService.t('verify'),
            isEnabled: !_isVerifying,
            onPressed: () => _onVerify(),
          ),
        );
      },
    );
  }
}

