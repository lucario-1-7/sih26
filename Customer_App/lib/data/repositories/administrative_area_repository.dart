import '../../core/networking/api_client.dart';
import '../models/administrative_area.dart';

class AdministrativeAreaRepository {
  AdministrativeAreaRepository._internal();
  static final AdministrativeAreaRepository instance = AdministrativeAreaRepository._internal();

  final ApiClient _client = ApiClient.instance;

  /// Used to resolve the free-text location a citizen types into a valid
  /// `administrative_area_id` for challenge submission — the backend has no
  /// pincode/geocoding lookup, so this fetches the small reference list and
  /// the caller matches on name/search.
  Future<List<AdministrativeArea>> list({String? search}) async {
    final json = await _client.get('/administrative-areas', query: search != null ? {'search': search} : null);
    final items = (json?['items'] as List<dynamic>?) ?? const [];
    return items.map((e) => AdministrativeArea.fromJson(e as Map<String, dynamic>)).toList();
  }
}
