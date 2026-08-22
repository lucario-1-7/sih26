import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:customer_app/main.dart';

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('Authentication to Onboarding flow smoke test',
      (WidgetTester tester) async {
    // Set phone viewport
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    // Build app
    await tester.pumpWidget(const SocialServeApp());
    await tester.pump();

    // 1. Phone number screen checks
    expect(find.text('Enter your phone number'), findsOneWidget);
    expect(find.text("We'll send you a verification code"), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);

    // 2. Navigate to OTP screen
    await tester.tap(find.text('Continue'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    // OTP screen checks
    expect(find.text('Enter verification code'), findsOneWidget);
    expect(find.text('Verify'), findsOneWidget);
    expect(find.text("Didn't receive the code?"), findsOneWidget);
    expect(find.text('Resend code'), findsOneWidget);

    // 3. Tap Verify to directly navigate to Onboarding screen
    await tester.tap(find.text('Verify'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    // Onboarding screen checks
    expect(find.text('Connect & Collaborate'), findsOneWidget);
    expect(find.text('Skip'), findsOneWidget);
  });
}
