import '../../core/networking/api_client.dart';
import '../models/auth_tokens.dart';

class UserRepository {
  UserRepository._internal();
  static final UserRepository instance = UserRepository._internal();

  final ApiClient _client = ApiClient.instance;

  Future<CurrentUser> getMe() async {
    final json = await _client.get('/users/me');
    return CurrentUser.fromJson(json!);
  }
}
