import 'package:flutter/material.dart';
import 'data/repositories/auth_repository.dart';
import 'screens/main_dashboard_screen.dart';
import 'screens/welcome_language_screen.dart';
import 'services/theme_service.dart';
import 'theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ThemeService.instance.init();
  ThemeService.instance.updateSystemUi();
  runApp(const SocialServeApp());
}

class SocialServeApp extends StatelessWidget {
  const SocialServeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: ThemeService.instance,
      builder: (context, _) {
        return MaterialApp(
          title: 'Social Serve',
          debugShowCheckedModeBanner: false,
          theme: buildLightTheme(),
          darkTheme: buildDarkTheme(),
          themeMode: ThemeService.instance.themeMode,
          home: const _SessionGate(),
        );
      },
    );
  }
}

/// Real session persistence: a stored access token routes straight to the
/// dashboard on app relaunch, skipping the login flow — no re-entering an
/// OTP every time the app is reopened. An expired/invalid token still falls
/// through safely, since ApiClient's 401-refresh path (and its failure mode,
/// clearing the stored session) is exercised the first time any authenticated
/// call is made from the dashboard.
class _SessionGate extends StatelessWidget {
  const _SessionGate();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: AuthRepository.instance.hasSession(),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return Scaffold(
            backgroundColor: AppColors.background,
            body: const Center(child: CircularProgressIndicator()),
          );
        }
        return snapshot.data == true ? const MainDashboardScreen() : const WelcomeLanguageScreen();
      },
    );
  }
}
