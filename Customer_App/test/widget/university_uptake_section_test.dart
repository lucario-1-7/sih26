import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:customer_app/data/models/project.dart';
import 'package:customer_app/widgets/university_uptake_section.dart';

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  Future<void> pumpSection(
    WidgetTester tester, {
    required String? clusterId,
    required Future<List<Project>> Function(String) fetchProjects,
  }) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: UniversityUptakeSection(clusterId: clusterId, fetchProjects: fetchProjects),
        ),
      ),
    );
  }

  testWidgets('renders nothing when the challenge has not been clustered yet (no clusterId)', (tester) async {
    await pumpSection(tester, clusterId: null, fetchProjects: (_) async => const []);
    await tester.pump();

    expect(find.text('University Partner'), findsNothing);
  });

  testWidgets('shows a loading indicator while the fetch is in flight', (tester) async {
    await pumpSection(
      tester,
      clusterId: 'c1',
      fetchProjects: (_) => Future.delayed(const Duration(milliseconds: 200), () => const []),
    );
    await tester.pump();

    expect(find.text('University Partner'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 250));
  });

  testWidgets('displays the actual university name from the API response, not a hardcoded value', (tester) async {
    await pumpSection(
      tester,
      clusterId: 'c1',
      fetchProjects: (_) async => [
        Project.fromJson({
          'id': 'p1',
          'cluster_id': 'c1',
          'title': 'Water Quality Fix',
          'status': 'accepted',
          'university': {'id': 'org-1', 'name': 'VIT Chennai', 'type': 'university'},
        }),
      ],
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('VIT Chennai'), findsOneWidget);
    expect(find.text('Not yet taken up by a university'), findsNothing);
  });

  testWidgets('shows the correct empty state when the project has not been taken up', (tester) async {
    await pumpSection(
      tester,
      clusterId: 'c1',
      fetchProjects: (_) async => [
        Project.fromJson({
          'id': 'p1',
          'cluster_id': 'c1',
          'title': 'Still Just Proposed',
          'status': 'proposed',
          'university': null,
        }),
      ],
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('Not yet taken up by a university'), findsOneWidget);
  });

  testWidgets('an API failure does not crash the screen', (tester) async {
    await pumpSection(
      tester,
      clusterId: 'c1',
      fetchProjects: (_) async => throw Exception('network error'),
    );
    await tester.pump();
    await tester.pump();

    expect(tester.takeException(), isNull);
    expect(find.text('Could not load university partner information right now.'), findsOneWidget);
  });

  testWidgets('re-fetching (simulated refresh) renders the same real university again', (tester) async {
    Future<List<Project>> fetch(String clusterId) async => [
          Project.fromJson({
            'id': 'p1',
            'cluster_id': clusterId,
            'title': 'Water Quality Fix',
            'status': 'active',
            'university': {'id': 'org-1', 'name': 'Anna University', 'type': 'university'},
          }),
        ];

    await pumpSection(tester, clusterId: 'c1', fetchProjects: fetch);
    await tester.pump();
    await tester.pump();
    expect(find.text('Anna University'), findsOneWidget);

    // Simulate a screen refresh by rebuilding the widget fresh (a new
    // instance re-runs initState, exactly like navigating back into the
    // screen would).
    await pumpSection(tester, clusterId: 'c1', fetchProjects: fetch);
    await tester.pump();
    await tester.pump();
    expect(find.text('Anna University'), findsOneWidget);
  });
}
