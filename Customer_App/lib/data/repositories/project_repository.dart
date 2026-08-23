import '../../core/networking/api_client.dart';
import '../models/project.dart';

class ProjectRepository {
  ProjectRepository._internal();
  static final ProjectRepository instance = ProjectRepository._internal();

  final ApiClient _client = ApiClient.instance;

  /// The existing canonical GET /projects listing, filtered to the one
  /// cluster a citizen's challenge belongs to — the same endpoint the
  /// organizational web client uses, not a Flutter-specific one. A cluster
  /// can in principle have more than one project (see the server's
  /// PROJECT_STATUS_TRANSITIONS model), so this returns the list rather
  /// than assuming exactly one.
  Future<List<Project>> listByCluster(String clusterId) async {
    final json = await _client.get('/projects', query: {'cluster_id': clusterId, 'limit': '20'});
    final items = (json?['items'] as List<dynamic>?) ?? const [];
    return items.map((e) => Project.fromJson(e as Map<String, dynamic>)).toList();
  }
}
