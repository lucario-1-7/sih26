import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/phone_number_screen.dart';
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
      home: const PhoneNumberScreen(),
    );
  }
}
