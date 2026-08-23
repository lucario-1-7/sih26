import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:customer_app/screens/demo_citizen_auth_screen.dart';
import 'package:customer_app/screens/phone_number_screen.dart';
import 'package:customer_app/screens/otp_verification_screen.dart';
import 'package:customer_app/theme/app_theme.dart';

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('calls the real demo login on mount — never a login form or phone/OTP entry point',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(theme: buildAppTheme(), home: const DemoCitizenAuthScreen()),
    );
    // Deliberately no settle/extra pumps here: whether the fake HttpClient's
    // instant failure has already landed or not, this screen must never
    // show a login form or the real phone/OTP screens at any point.
    await tester.pump();

    expect(find.byType(TextField), findsNothing);
    expect(find.byType(PhoneNumberScreen), findsNothing);
    expect(find.byType(OtpVerificationScreen), findsNothing);
  });

  testWidgets(
      'a failed demo login shows a concise retry state instead of falling back to phone/OTP authentication',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(theme: buildAppTheme(), home: const DemoCitizenAuthScreen()),
    );
    await tester.pump();
    // flutter_test fakes every HttpClient to fail instantly (deliberate
    // network isolation) — the same established pattern
    // otp_verification_screen_test.dart uses to prove failure handling
    // without hitting a real backend.
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.textContaining('Demo login failed'), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
    // The critical requirement: never routes into real OTP auth on failure.
    expect(find.byType(PhoneNumberScreen), findsNothing);
    expect(find.byType(OtpVerificationScreen), findsNothing);
  });
}
