class AuthTokens {
  final String accessToken;
  final String refreshToken;

  const AuthTokens({required this.accessToken, required this.refreshToken});

  factory AuthTokens.fromJson(Map<String, dynamic> json) => AuthTokens(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
      );
}

class CurrentUser {
  final String id;
  final String phone;
  final String name;
  final String role;

  const CurrentUser({required this.id, required this.phone, required this.name, required this.role});

  factory CurrentUser.fromJson(Map<String, dynamic> json) => CurrentUser(
        id: json['id'] as String,
        phone: json['phone'] as String,
        name: json['name'] as String,
        role: json['role'] as String,
      );
}
