import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'data/repositories/auth_repository.dart';
import 'screens/main_dashboard_screen.dart';
import 'screens/welcome_language_screen.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      statusBarBrightness: Brightness.light,
      systemNavigationBarColor: AppColors.background,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );
  runApp(const SocialServeApp());
}

class SocialServeApp extends StatelessWidget {
  const SocialServeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Social Serve',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const _SessionGate(),
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
          return const Scaffold(
            backgroundColor: AppColors.background,
            body: Center(child: CircularProgressIndicator()),
          );
        }
        return snapshot.data == true ? const MainDashboardScreen() : const WelcomeLanguageScreen();
      },
    );
  }
}
