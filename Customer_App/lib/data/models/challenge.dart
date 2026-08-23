/// Raw, backend-shaped representation of `ChallengeResponse` from
/// `server/app/schemas/challenge.py`. Field names and the `status` values
/// ("submitted" | "open" | "duplicate" | "resolved") are the backend's own —
/// nothing here is renamed or reinterpreted. UI-facing mapping into the
/// existing `IssueItem` model happens in `issue_model.dart`, in one place,
/// so the correspondence is explicit and auditable rather than scattered.
class Challenge {
  final String id;
  final String title;
  final String description;
  final String status;
  final String? severity;
  final String administrativeAreaId;
  final String? pinCode;
  final String? clusterId;
  final String? contentDomain;
  final double? contentDomainConfidence;
  final double? contentFieldIntensity;
  final String? contentFieldLabel;
  final DateTime createdAt;

  const Challenge({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.severity,
    required this.administrativeAreaId,
    required this.pinCode,
    required this.clusterId,
    required this.contentDomain,
    required this.contentDomainConfidence,
    required this.contentFieldIntensity,
    required this.contentFieldLabel,
    required this.createdAt,
  });

  factory Challenge.fromJson(Map<String, dynamic> json) => Challenge(
        id: json['id'] as String,
        title: json['title'] as String,
        description: json['description'] as String,
        status: json['status'] as String,
        severity: json['severity'] as String?,
        administrativeAreaId: json['administrative_area_id'] as String,
        pinCode: json['pin_code'] as String?,
        // Null until a VALIDATOR clusters this challenge (see
        // server/app/services/challenge_service.py), the join point used
        // to look up which, if any, university has taken up the project
        // this challenge eventually became part of.
        clusterId: json['cluster_id'] as String?,
        contentDomain: json['content_domain'] as String?,
        contentDomainConfidence: (json['content_domain_confidence'] as num?)?.toDouble(),
        contentFieldIntensity: (json['content_field_intensity'] as num?)?.toDouble(),
        contentFieldLabel: json['content_field_label'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}
