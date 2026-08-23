import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:customer_app/core/config/api_config.dart';
import 'package:customer_app/screens/demo_citizen_auth_screen.dart';
import 'package:customer_app/screens/onboarding_screen.dart';
import 'package:customer_app/screens/otp_verification_screen.dart';
import 'package:customer_app/screens/phone_number_screen.dart';
import 'package:customer_app/screens/welcome_language_screen.dart';
import 'package:customer_app/theme/app_theme.dart';

/// DemoConfig.enabled is hardcoded true, so this is no longer a
/// --dart-define-controlled branch: "Continue" always reaches
/// DemoCitizenAuthScreen — a real `/auth/demo/login` call for the real,
/// backend-persisted "Demo Citizen" user — never PhoneNumberScreen, and
/// never a screen that skips authentication straight to OnboardingScreen.
void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  test('DemoConfig.enabled is hardcoded true', () {
    expect(DemoConfig.enabled, isTrue);
  });

  testWidgets('Continue reaches the real demo-citizen login, never a phone/OTP or no-auth bypass screen', (tester) async {
    await tester.pumpWidget(
      MaterialApp(theme: buildAppTheme(), home: const WelcomeLanguageScreen()),
    );
    await tester.pump();

    await tester.tap(find.text('Continue'));
    // Not pumpAndSettle(): DemoCitizenAuthScreen shows an indefinitely
    // animating CircularProgressIndicator while its real demo-login network
    // call is in flight.
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.byType(DemoCitizenAuthScreen), findsOneWidget);
    expect(find.byType(PhoneNumberScreen), findsNothing);
    expect(find.byType(OtpVerificationScreen), findsNothing);
    expect(find.byType(OnboardingScreen), findsNothing);
  });
}
