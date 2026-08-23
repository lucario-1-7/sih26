import 'package:flutter/material.dart';
import '../data/models/project.dart';
import '../data/repositories/project_repository.dart';
import '../theme/app_theme.dart';

/// "Which university has taken up this problem" - fetched live from the
/// same canonical GET /projects endpoint the organizational web client
/// uses (ProjectRepository.listByCluster), keyed by the challenge's own
/// cluster_id. Shows nothing (not even the section) until the challenge has
/// actually been clustered - a freshly submitted, not-yet-triaged issue has
/// no cluster yet, so there is nothing to look up.
typedef ProjectsByClusterFetcher = Future<List<Project>> Function(String clusterId);

class UniversityUptakeSection extends StatefulWidget {
  final String? clusterId;

  /// Defaults to the real ProjectRepository call. Overridable only for
  /// widget tests, which otherwise have no seam into the singleton
  /// ApiClient's real HTTP stack.
  final ProjectsByClusterFetcher fetchProjects;

  UniversityUptakeSection({super.key, required this.clusterId, ProjectsByClusterFetcher? fetchProjects})
      : fetchProjects = fetchProjects ?? ProjectRepository.instance.listByCluster;

  @override
  State<UniversityUptakeSection> createState() => _UniversityUptakeSectionState();
}

class _UniversityUptakeSectionState extends State<UniversityUptakeSection> {
  late Future<List<Project>> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<List<Project>> _load() {
    final clusterId = widget.clusterId;
    if (clusterId == null) return Future.value(const []);
    return widget.fetchProjects(clusterId);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.clusterId == null) {
      // Not yet triaged into a cluster at all — nothing to show yet, and
      // showing "not taken up" here would misleadingly suggest the pipeline
      // had already reached the point of considering it.
      return const SizedBox.shrink();
    }

    return FutureBuilder<List<Project>>(
      future: _future,
      builder: (context, snapshot) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'University Partner',
              style: AppTypography.heading(context).copyWith(
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            _buildContent(context, snapshot),
            const SizedBox(height: 28),
          ],
        );
      },
    );
  }

  Widget _buildContent(BuildContext context, AsyncSnapshot<List<Project>> snapshot) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return const SizedBox(
        height: 20,
        width: 20,
        child: CircularProgressIndicator(strokeWidth: 2),
      );
    }
    if (snapshot.hasError) {
      return Text(
        'Could not load university partner information right now.',
        style: AppTypography.supporting(context).copyWith(
          fontSize: 14,
          color: AppColors.secondaryText,
        ),
      );
    }
    final universities = (snapshot.data ?? const []).map((p) => p.university).whereType<University>();
    final university = universities.isEmpty ? null : universities.first;
    return Text(
      university != null ? university.name : 'Not yet taken up by a university',
      style: AppTypography.supporting(context).copyWith(
        fontSize: 15,
        color: university != null ? AppColors.primaryText : AppColors.mutedText,
      ),
    );
  }
}
