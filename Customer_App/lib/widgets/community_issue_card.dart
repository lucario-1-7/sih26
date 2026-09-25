import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/community_issue_model.dart';
import '../services/theme_service.dart';
import '../theme/app_theme.dart';

/// Old Reddit Mobile UI Style Card for Community Civic Discussions Feed
class CommunityIssueCard extends StatelessWidget {
  final CommunityIssue issue;
  final VoidCallback onUpvote;
  final VoidCallback? onDownvote;
  final VoidCallback onCommentTap;
  final VoidCallback onTap;
  final VoidCallback? onShareTap;
  final bool isDetailView;

  const CommunityIssueCard({
    super.key,
    required this.issue,
    required this.onUpvote,
    this.onDownvote,
    required this.onCommentTap,
    required this.onTap,
    this.onShareTap,
    this.isDetailView = false,
  });

  Color _getCategoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'roads & infrastructure':
      case 'roads':
        return const Color(0xFFF97316); // Orange
      case 'water scarcity':
      case 'water':
        return const Color(0xFF0284C7); // Sky Blue
      case 'sanitation & waste':
      case 'sanitation':
        return const Color(0xFF10B981); // Emerald Green
      case 'accessibility':
        return const Color(0xFF8B5CF6); // Purple
      case 'public safety':
      case 'safety':
        return const Color(0xFFEF4444); // Red
      case 'environmental pollution':
      case 'environment':
        return const Color(0xFF14B8A6); // Teal
      case 'education & literacy':
      case 'education':
        return const Color(0xFFEAB308); // Yellow
      case 'healthcare access':
      case 'healthcare':
        return const Color(0xFFEC4899); // Pink
      default:
        return const Color(0xFF64748B); // Slate
    }
  }

  IconData _getCategoryIcon(String category) {
    final lower = category.toLowerCase();
    if (lower.contains('road') || lower.contains('infra') || lower.contains('pothole')) {
      return Icons.construction_rounded;
    } else if (lower.contains('water') || lower.contains('pipe') || lower.contains('drain')) {
      return Icons.water_drop_rounded;
    } else if (lower.contains('sanitat') || lower.contains('waste') || lower.contains('garbage')) {
      return Icons.delete_outline_rounded;
    } else if (lower.contains('access') || lower.contains('disab') || lower.contains('ramp')) {
      return Icons.accessible_forward_rounded;
    } else if (lower.contains('safe') || lower.contains('police') || lower.contains('crime')) {
      return Icons.shield_rounded;
    } else if (lower.contains('pollut') || lower.contains('environ') || lower.contains('river')) {
      return Icons.eco_rounded;
    } else if (lower.contains('edu') || lower.contains('school')) {
      return Icons.school_rounded;
    } else if (lower.contains('health') || lower.contains('hosp')) {
      return Icons.local_hospital_rounded;
    }
    return Icons.public_rounded;
  }

  void _showRedditOverflowMenu(BuildContext context) {
    final isDark = ThemeService.instance.isDark;
    showModalBottomSheet(
      context: context,
      backgroundColor: isDark ? const Color(0xFF1A1A1B) : Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: isDark ? const Color(0xFF343536) : const Color(0xFFE5E7EB),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              ListTile(
                leading: Icon(Icons.share_outlined, color: AppColors.primaryText),
                title: Text('Share Post', style: TextStyle(color: AppColors.primaryText)),
                onTap: () {
                  Navigator.pop(ctx);
                  onShareTap?.call();
                },
              ),
              ListTile(
                leading: Icon(Icons.link_rounded, color: AppColors.primaryText),
                title: Text('Copy link to grievance', style: TextStyle(color: AppColors.primaryText)),
                onTap: () {
                  Navigator.pop(ctx);
                  Clipboard.setData(ClipboardData(text: 'https://civicdesk.org/issue/${issue.id}'));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Link copied to clipboard')),
                  );
                },
              ),
              ListTile(
                leading: Icon(Icons.bookmark_border_rounded, color: AppColors.primaryText),
                title: Text('Save for later', style: TextStyle(color: AppColors.primaryText)),
                onTap: () {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Saved to your profile')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.flag_outlined, color: Color(0xFFEF4444)),
                title: const Text('Report post', style: TextStyle(color: Color(0xFFEF4444))),
                onTap: () {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Report submitted for moderator review')),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = ThemeService.instance.isDark;
    final catColor = _getCategoryColor(issue.category);
    final catIcon = _getCategoryIcon(issue.category);

    // Dark mode colors tuned to old Reddit Mobile AMOLED & Charcoal dark theme
    final cardBg = isDark ? const Color(0xFF1A1A1B) : Colors.white;
    final cardBorder = isDark ? const Color(0xFF2D2E30) : const Color(0xFFE5E7EB);
    final pillBg = isDark ? const Color(0xFF272729) : const Color(0xFFF3F4F6);
    final pillBorder = isDark ? const Color(0xFF383A3D) : const Color(0xFFE5E7EB);

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 8.0),
      decoration: BoxDecoration(
        color: cardBg,
        border: Border(
          top: BorderSide(
            color: cardBorder,
            width: 0.8,
          ),
          bottom: BorderSide(
            color: cardBorder,
            width: 0.8,
          ),
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: isDetailView ? null : onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 1. TOP HEADER: Subreddit Icon + r/Subreddit + u/User • Timestamp • Location + Overflow Menu
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    // Subreddit circular avatar
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: catColor.withValues(alpha: isDark ? 0.22 : 0.14),
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: catColor.withValues(alpha: 0.35),
                          width: 1.0,
                        ),
                      ),
                      child: Center(
                        child: Icon(catIcon, size: 16, color: catColor),
                      ),
                    ),
                    const SizedBox(width: 9),

                    // Subreddit and author lines (like Reddit Mobile)
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // r/SubredditName
                          Text(
                            issue.subredditName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 13.5,
                              fontWeight: FontWeight.w700,
                              color: AppColors.primaryText,
                              letterSpacing: -0.1,
                            ),
                          ),
                          const SizedBox(height: 1),
                          // u/author • 13h • Location
                          Row(
                            children: [
                              Flexible(
                                child: Text(
                                  'u/${issue.author}',
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                    fontSize: 11.5,
                                    fontWeight: FontWeight.w400,
                                    color: AppColors.secondaryText,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 4),
                              Text(
                                '•',
                                style: TextStyle(
                                  fontSize: 11.5,
                                  color: AppColors.secondaryText,
                                ),
                              ),
                              const SizedBox(width: 4),
                              Text(
                                issue.timeAgo,
                                style: TextStyle(
                                  fontSize: 11.5,
                                  fontWeight: FontWeight.w400,
                                  color: AppColors.secondaryText,
                                ),
                              ),
                              if (issue.location.trim().isNotEmpty) ...[
                                const SizedBox(width: 4),
                                Text(
                                  '•',
                                  style: TextStyle(
                                    fontSize: 11.5,
                                    color: AppColors.secondaryText,
                                  ),
                                ),
                                const SizedBox(width: 4),
                                Flexible(
                                  child: Text(
                                    issue.location.trim(),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w400,
                                      color: AppColors.secondaryText,
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),

                    // Overflow Menu Button
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () => _showRedditOverflowMenu(context),
                      child: Padding(
                        padding: const EdgeInsets.all(4.0),
                        child: Icon(
                          Icons.more_horiz_rounded,
                          size: 20,
                          color: AppColors.secondaryText,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 10),

                // 2. POST TITLE (Bold, prominent, matching Reddit Mobile)
                Text(
                  issue.title,
                  maxLines: isDetailView ? null : 3,
                  overflow: isDetailView ? null : TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 16.5,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primaryText,
                    height: 1.28,
                    letterSpacing: -0.2,
                  ),
                ),

                const SizedBox(height: 8),

                // 3. POST DESCRIPTION (Text body - matching Reddit Mobile clean layout)
                Text(
                  issue.description,
                  maxLines: isDetailView ? null : 3,
                  overflow: isDetailView ? null : TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 13.5,
                    height: 1.45,
                    color: isDark ? const Color(0xFFD1D5DB) : const Color(0xFF374151),
                  ),
                ),

                const SizedBox(height: 12),

                // 4. BOTTOM ACTION PILL ROW (OLD REDDIT MOBILE UI)
                // Pill 1: [ ↑ 217 ↓ ]  |  Pill 2: [ 💬 38 Comments ]  |  Pill 3: [ ↗ 41 ]
                Row(
                  children: [
                    // Vote Pill: [ ↑  217  ↓ ]
                    Container(
                      height: 34,
                      padding: const EdgeInsets.symmetric(horizontal: 4.0),
                      decoration: BoxDecoration(
                        color: pillBg,
                        borderRadius: BorderRadius.circular(20.0),
                        border: Border.all(
                          color: issue.isUpvoted
                              ? const Color(0xFFFF4500).withValues(alpha: 0.5)
                              : (issue.isDownvoted
                                  ? const Color(0xFF7193FF).withValues(alpha: 0.5)
                                  : pillBorder),
                          width: 1.0,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // Upvote
                          GestureDetector(
                            behavior: HitTestBehavior.opaque,
                            onTap: onUpvote,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 7.0, vertical: 4.0),
                              child: Icon(
                                Icons.arrow_upward_rounded,
                                size: 16,
                                color: issue.isUpvoted
                                    ? const Color(0xFFFF4500)
                                    : AppColors.secondaryText,
                              ),
                            ),
                          ),
                          // Count
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 2.0),
                            child: Text(
                              '${issue.upvotes}',
                              style: TextStyle(
                                fontSize: 12.5,
                                fontWeight: FontWeight.w700,
                                color: issue.isUpvoted
                                    ? const Color(0xFFFF4500)
                                    : (issue.isDownvoted
                                        ? const Color(0xFF7193FF)
                                        : AppColors.primaryText),
                              ),
                            ),
                          ),
                          // Downvote
                          GestureDetector(
                            behavior: HitTestBehavior.opaque,
                            onTap: onDownvote,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 7.0, vertical: 4.0),
                              child: Icon(
                                Icons.arrow_downward_rounded,
                                size: 16,
                                color: issue.isDownvoted
                                    ? const Color(0xFF7193FF)
                                    : AppColors.secondaryText,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(width: 8),

                    // Comments Pill: [ 💬 38 Comments ]
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: onCommentTap,
                      child: Container(
                        height: 34,
                        padding: const EdgeInsets.symmetric(horizontal: 12.0),
                        decoration: BoxDecoration(
                          color: pillBg,
                          borderRadius: BorderRadius.circular(20.0),
                          border: Border.all(color: pillBorder, width: 1.0),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.chat_bubble_outline_rounded,
                              size: 15,
                              color: AppColors.secondaryText,
                            ),
                            const SizedBox(width: 6),
                            Text(
                              '${issue.comments.length} Comments',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: AppColors.primaryText,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(width: 8),

                    // Share Pill: [ ↗ 41 ]
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: onShareTap ??
                          () {
                            Clipboard.setData(
                              ClipboardData(text: 'https://civicdesk.org/issue/${issue.id}'),
                            );
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('Issue link copied to clipboard: ${issue.title}'),
                                duration: const Duration(seconds: 2),
                              ),
                            );
                          },
                      child: Container(
                        height: 34,
                        padding: const EdgeInsets.symmetric(horizontal: 11.0),
                        decoration: BoxDecoration(
                          color: pillBg,
                          borderRadius: BorderRadius.circular(20.0),
                          border: Border.all(color: pillBorder, width: 1.0),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Transform.flip(
                              flipX: true,
                              child: Icon(
                                Icons.reply_rounded,
                                size: 16,
                                color: AppColors.secondaryText,
                              ),
                            ),
                            const SizedBox(width: 5),
                            Text(
                              '${issue.shares}',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: AppColors.primaryText,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
