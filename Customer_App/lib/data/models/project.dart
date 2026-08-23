/// Raw, backend-shaped representation of `ProjectResponse` from
/// `server/app/schemas/project.py`. Only the fields this app actually
/// displays are parsed — same convention as `Challenge`.
class University {
  final String id;
  final String name;
  final String type;

  const University({required this.id, required this.name, required this.type});

  factory University.fromJson(Map<String, dynamic> json) => University(
        id: json['id'] as String,
        name: json['name'] as String,
        type: json['type'] as String,
      );
}

class Project {
  final String id;
  final String clusterId;
  final String title;
  final String status;
  // Null until the project has actually been accepted (status past
  // "proposed") — never a placeholder name. See
  // server/app/services/project_service.py:_has_been_taken_up.
  final University? university;

  const Project({
    required this.id,
    required this.clusterId,
    required this.title,
    required this.status,
    required this.university,
  });

  factory Project.fromJson(Map<String, dynamic> json) => Project(
        id: json['id'] as String,
        clusterId: json['cluster_id'] as String,
        title: json['title'] as String,
        status: json['status'] as String,
        university: json['university'] != null
            ? University.fromJson(json['university'] as Map<String, dynamic>)
            : null,
      );
}
