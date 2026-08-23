import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:customer_app/models/issue_model.dart';
import 'package:customer_app/screens/main_dashboard_screen.dart';
import 'package:customer_app/screens/recent_activity_screen.dart';
import 'package:customer_app/theme/app_theme.dart';
import 'package:customer_app/widgets/custom_bottom_navbar.dart';

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('Dashboard navbar has exactly 4 tabs and no Activity tab',
      (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      MaterialApp(
        theme: buildAppTheme(),
        home: MainDashboardScreen(initialIssues: List.from(MockIssueRepository.initialIssues)),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));

    // Verify 4 navbar tabs exist
    expect(find.byType(CustomBottomNavbar), findsOneWidget);
    expect(find.text('Home'), findsWidgets);
    expect(find.text('My Issues'), findsWidgets);
    expect(find.text('File Grievance'), findsWidgets);
    expect(find.text('Profile'), findsWidgets);

    // Verify Activity tab is NOT in the bottom navigation bar
    expect(find.text('Activity'), findsNothing);
  });

  testWidgets('Notification bell on Home opens Notifications screen and supports pull-to-right to mark as read',
      (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      MaterialApp(
        theme: buildAppTheme(),
        home: MainDashboardScreen(initialIssues: List.from(MockIssueRepository.initialIssues)),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));

    // Find and tap notification bell
    final bellFinder = find.byIcon(FeatherIcons.bell);
    expect(bellFinder, findsOneWidget);
    await tester.tap(bellFinder);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    // Verify RecentActivityScreen is opened
    expect(find.byType(RecentActivityScreen), findsOneWidget);
    expect(find.text('NOTIFICATIONS'), findsOneWidget);
    expect(find.text('App Update'), findsOneWidget);

    // Pull notification item to the right
    await tester.drag(find.text('App Update'), const Offset(300.0, 0.0));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    // Verify 'Marked as read' snackbar feedback
    expect(find.text('Marked as read'), findsOneWidget);
  });

  testWidgets('My Issues location filter is a dropdown of locations with reported issues only',
      (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      MaterialApp(
        theme: buildAppTheme(),
        home: MainDashboardScreen(initialIssues: List.from(MockIssueRepository.initialIssues)),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));

    // Navigate to My Issues tab
    await tester.tap(find.text('My Issues'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));

    // Verify DropdownButton is present for location filter
    final dropdownFinder = find.byType(DropdownButton<String>);
    expect(dropdownFinder, findsOneWidget);

    // Open location dropdown
    await tester.tap(dropdownFinder);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));

    // Verify locations from MockIssueRepository exist in dropdown items
    expect(find.text('All Locations').hitTestable(), findsOneWidget);
    expect(find.text('Adyar, Chennai').hitTestable(), findsOneWidget);
    expect(find.text('Chennai, Tamil Nadu').hitTestable(), findsOneWidget);
    expect(find.text('Manapakkam').hitTestable(), findsOneWidget);
    expect(find.text('Sector 12, Chennai').hitTestable(), findsOneWidget);

    // Non-existent location should not be in the dropdown
    expect(find.text('Outer Ring Road'), findsNothing);
  });
}
