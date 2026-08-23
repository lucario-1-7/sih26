import 'package:flutter/material.dart';
import '../core/networking/api_exception.dart';
import '../data/repositories/auth_repository.dart';
import '../theme/app_theme.dart';
import '../widgets/primary_button.dart';
import 'onboarding_screen.dart';

/// PRESENTATION-ONLY. The only route this screen leads to is
/// [OnboardingScreen] — never [PhoneNumberScreen] / [OtpVerificationScreen].
/// This is not a UI shortcut: it performs a real
/// `POST /api/v1/auth/demo/login {"persona":"citizen"}` call and stores the
/// real backend-issued JWT through the exact same [AuthRepository] /
/// TokenStorage path a normal OTP login uses. From that point on the app is
/// a genuinely authenticated citizen session — every subsequent screen and
/// API call is real.
///
/// Reached only from [WelcomeLanguageScreen] when `DemoConfig.enabled` is
/// true; the real OTP screens are entirely unreachable from that path in
/// that case, not merely hidden.
class DemoCitizenAuthScreen extends StatefulWidget {
  const DemoCitizenAuthScreen({super.key});

  @override
  State<DemoCitizenAuthScreen> createState() => _DemoCitizenAuthScreenState();
}

class _DemoCitizenAuthScreenState extends State<DemoCitizenAuthScreen> {
  String? _errorText;

  @override
  void initState() {
    super.initState();
    _authenticate();
  }

  Future<void> _authenticate() async {
    setState(() => _errorText = null);
    try {
      await AuthRepository.instance.demoLogin(persona: 'citizen');
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const OnboardingScreen()),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      // Demo mode never falls back to real OTP authentication — a failure
      // here is shown as a concise technical error with a retry, not a
      // redirect into the phone/OTP flow.
      setState(() => _errorText = 'Demo login failed: ${e.code} — ${e.userMessage}');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32.0),
            child: _errorText == null
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    children: const [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text(
                        'Starting demo citizen session…',
                        style: TextStyle(color: AppColors.secondaryText, fontSize: 13),
                      ),
                    ],
                  )
                : Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.error_outline, color: Colors.redAccent, size: 40),
                      const SizedBox(height: 12),
                      Text(
                        _errorText!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: AppColors.secondaryText, fontSize: 13),
                      ),
                      const SizedBox(height: 20),
                      PrimaryButton(text: 'Retry', onPressed: _authenticate),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}
