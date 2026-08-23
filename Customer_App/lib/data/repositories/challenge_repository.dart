import '../../core/networking/api_client.dart';
import '../models/challenge.dart';

class ChallengeRepository {
  ChallengeRepository._internal();
  static final ChallengeRepository instance = ChallengeRepository._internal();

  final ApiClient _client = ApiClient.instance;

  Future<Challenge> createChallenge({
    required String title,
    required String description,
    required String administrativeAreaId,
    String? pinCode,
  }) async {
    final json = await _client.post('/challenges', body: {
      'title': title,
      'description': description,
      'administrative_area_id': administrativeAreaId,
      if (pinCode != null && pinCode.isNotEmpty) 'pin_code': pinCode,
    });
    return Challenge.fromJson(json!);
  }

  /// The backend never exposes an implicit "my challenges" endpoint — the
  /// caller must pass its own user id as `submitted_by_id`, exactly the way
  /// the organizational web client's list calls work.
  Future<List<Challenge>> listMyChallenges(String submittedById) async {
    final json = await _client.get('/challenges', query: {'submitted_by_id': submittedById, 'limit': '100'});
    final items = (json?['items'] as List<dynamic>?) ?? const [];
    return items.map((e) => Challenge.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Challenge> getChallenge(String id) async {
    final json = await _client.get('/challenges/$id');
    return Challenge.fromJson(json!);
  }
}
