class AdministrativeArea {
  final String id;
  final String name;
  final String level;

  const AdministrativeArea({required this.id, required this.name, required this.level});

  factory AdministrativeArea.fromJson(Map<String, dynamic> json) => AdministrativeArea(
        id: json['id'] as String,
        name: json['name'] as String,
        level: json['level'] as String,
      );

  String get label => '$name (${level[0].toUpperCase()}${level.substring(1)})';
}
