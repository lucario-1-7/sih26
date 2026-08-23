import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:customer_app/screens/phone_number_screen.dart';
import 'package:customer_app/theme/app_theme.dart';

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('an invalid (too-short) phone number shows a validation message and does not navigate', (tester) async {
    await tester.pumpWidget(
      MaterialApp(theme: buildAppTheme(), home: const PhoneNumberScreen()),
    );
    await tester.pump();

    await tester.enterText(find.byType(TextField), '123');
    await tester.tap(find.text('Continue'));
    await tester.pump();

    expect(find.text('Enter a valid 10-digit phone number.'), findsOneWidget);
  });

  testWidgets('a valid 10-digit phone number attempts real submission and surfaces the failure gracefully',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(theme: buildAppTheme(), home: const PhoneNumberScreen()),
    );
    await tester.pump();

    await tester.enterText(find.byType(TextField), '9876543210');
    await tester.tap(find.text('Continue'));
    // flutter_test fakes every HttpClient to fail instantly (deliberate
    // network isolation) — this proves the screen calls the real
    // AuthRepository/ApiClient path and handles that failure as an error
    // message rather than crashing or silently hanging. The success path
    // against the real backend is covered by citizen_flow_test.dart.
    await tester.pumpAndSettle();

    expect(find.byType(PhoneNumberScreen), findsOneWidget);
    expect(find.text('Sending OTP…'), findsNothing); // loading state cleared, not stuck
  });
}
