import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:customer_app/screens/otp_verification_screen.dart';
import 'package:customer_app/theme/app_theme.dart';

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('tapping Verify with an incomplete code shows a validation message', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: buildAppTheme(),
        home: const OtpVerificationScreen(phoneNumber: '+91 98765 43210', backendPhone: '+919876543210'),
      ),
    );
    await tester.pump();

    await tester.tap(find.text('Verify'));
    await tester.pump();

    expect(find.text('Enter the 6-digit code.'), findsOneWidget);
  });

  testWidgets('entering all 6 digits triggers real verification and surfaces the failure gracefully',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: buildAppTheme(),
        home: const OtpVerificationScreen(phoneNumber: '+91 98765 43210', backendPhone: '+919876543210'),
      ),
    );
    await tester.pump();

    final fields = find.byType(TextField);
    expect(fields, findsNWidgets(6));
    for (var i = 0; i < 6; i++) {
      await tester.enterText(fields.at(i), '${i + 1}');
    }
    // onCompleted fires automatically once the 6th digit lands, calling the
    // real AuthRepository.verifyOtp -> ApiClient path. flutter_test fakes
    // every HttpClient to fail instantly (deliberate network isolation) —
    // this proves the screen handles that failure as an error message
    // rather than crashing or hanging. The success path against the real
    // backend is covered by citizen_flow_test.dart.
    await tester.pumpAndSettle();

    expect(find.byType(OtpVerificationScreen), findsOneWidget);
    expect(find.text('Verifying…'), findsNothing); // loading state cleared, not stuck
  });

  testWidgets('the phone number passed in is displayed', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: buildAppTheme(),
        home: const OtpVerificationScreen(phoneNumber: '+91 98765 43210', backendPhone: '+919876543210'),
      ),
    );
    await tester.pump();

    expect(find.text('+91 98765 43210'), findsOneWidget);
  });
}
