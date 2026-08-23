import 'package:flutter_test/flutter_test.dart';
import 'package:customer_app/data/models/project.dart';

void main() {
  group('Project.fromJson', () {
    test('parses a project response containing a real university', () {
      final project = Project.fromJson({
        'id': 'p1',
        'cluster_id': 'c1',
        'title': 'Water Quality Fix',
        'status': 'accepted',
        'university': {
          'id': 'org-1',
          'name': 'Indian Institute of Technology Dhanbad',
          'type': 'university',
        },
      });

      expect(project.id, 'p1');
      expect(project.clusterId, 'c1');
      expect(project.title, 'Water Quality Fix');
      expect(project.status, 'accepted');
      expect(project.university, isNotNull);
      expect(project.university!.id, 'org-1');
      expect(project.university!.name, 'Indian Institute of Technology Dhanbad');
      expect(project.university!.type, 'university');
    });

    test('parses a proposed project with no university as null, not a placeholder', () {
      final project = Project.fromJson({
        'id': 'p2',
        'cluster_id': 'c2',
        'title': 'Not Yet Accepted',
        'status': 'proposed',
        'university': null,
      });

      expect(project.university, isNull);
    });
  });
}
