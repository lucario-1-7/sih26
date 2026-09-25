import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/community_issue_model.dart';
import '../services/theme_service.dart';
import '../theme/app_theme.dart';

/// Old Reddit Mobile UI Style Comments Bottom Sheet
class CommunityCommentsSheet extends StatefulWidget {
  final CommunityIssue issue;
  final void Function(CommunityComment newComment) onCommentAdded;

  const CommunityCommentsSheet({
    super.key,
    required this.issue,
    required this.onCommentAdded,
  });

  static void show(
    BuildContext context, {
    required CommunityIssue issue,
    required void Function(CommunityComment newComment) onCommentAdded,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => CommunityCommentsSheet(
        issue: issue,
        onCommentAdded: onCommentAdded,
      ),
    );
  }

  @override
  State<CommunityCommentsSheet> createState() => _CommunityCommentsSheetState();
}

class _CommunityCommentsSheetState extends State<CommunityCommentsSheet> {
  final TextEditingController _commentController = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  CommunityComment? _replyingTo;

  @override
  void dispose() {
    _commentController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _submitComment() {
    final text = _commentController.text.trim();
    if (text.isEmpty) return;

    final newComment = CommunityComment(
      id: 'comm-${DateTime.now().millisecondsSinceEpoch}',
      author: 'You (Citizen)',
      role: 'Verified Resident',
      timeAgo: 'Just now',
      content: text,
      upvotes: 1,
      isUpvoted: true,
      isOp: false,
    );

    if (_replyingTo != null) {
      _replyingTo!.replies.add(newComment);
      _replyingTo = null;
    } else {
      widget.onCommentAdded(newComment);
    }

    _commentController.clear();
    FocusScope.of(context).unfocus();
    setState(() {});
  }

  void _toggleCommentUpvote(CommunityComment comment) {
    setState(() {
      if (comment.isUpvoted) {
        comment.upvotes--;
        comment.isUpvoted = false;
      } else {
        if (comment.isDownvoted) {
          comment.upvotes += 2;
          comment.isDownvoted = false;
        } else {
          comment.upvotes++;
        }
        comment.isUpvoted = true;
      }
    });
  }

  void _toggleCommentDownvote(CommunityComment comment) {
    setState(() {
      if (comment.isDownvoted) {
        comment.upvotes++;
        comment.isDownvoted = false;
      } else {
        if (comment.isUpvoted) {
          comment.upvotes -= 2;
          comment.isUpvoted = false;
        } else {
          comment.upvotes--;
        }
        comment.isDownvoted = true;
      }
    });
  }

  void _startReply(CommunityComment target) {
    setState(() {
      _replyingTo = target;
    });
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    final isDark = ThemeService.instance.isDark;
    final bg = isDark ? const Color(0xFF1A1A1B) : Colors.white;
    final border = isDark ? const Color(0xFF2D2E30) : const Color(0xFFE5E7EB);

    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      margin: EdgeInsets.only(bottom: bottomInset),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20.0)),
        border: Border(
          top: BorderSide(color: border, width: 1.0),
          left: BorderSide(color: border, width: 1.0),
          right: BorderSide(color: border, width: 1.0),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Drag handle
          const SizedBox(height: 10),
          Container(
            width: 38,
            height: 4,
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF383A3D) : const Color(0xFFD1D5DB),
              borderRadius: BorderRadius.circular(2.0),
            ),
          ),
          const SizedBox(height: 10),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.chat_bubble_outline_rounded,
                            size: 17,
                            color: AppColors.primaryText,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Comments (${widget.issue.comments.length})',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: AppColors.primaryText,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 3),
                      Text(
                        widget.issue.title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontSize: 11.5,
                          color: AppColors.secondaryText,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.close_rounded, size: 20, color: AppColors.secondaryText),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
          ),

          Divider(height: 16, thickness: 0.8, color: border),

          // Comments List
          Expanded(
            child: widget.issue.comments.isEmpty
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.chat_bubble_outline_rounded, size: 36, color: AppColors.mutedText),
                        const SizedBox(height: 10),
                        Text(
                          'No comments yet',
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.primaryText),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Be the first to share ground evidence or local updates.',
                          style: TextStyle(fontSize: 12, color: AppColors.secondaryText),
                        ),
                      ],
                    ),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 8.0),
                    physics: const BouncingScrollPhysics(),
                    itemCount: widget.issue.comments.length,
                    separatorBuilder: (context, index) => Divider(
                      height: 18,
                      thickness: 0.6,
                      color: isDark ? const Color(0xFF242528) : const Color(0xFFF3F4F6),
                    ),
                    itemBuilder: (context, index) {
                      final comment = widget.issue.comments[index];
                      return _buildCommentThread(comment, isDark);
                    },
                  ),
          ),

          // Bottom Comment Bar
          _buildBottomCommentBar(isDark),
        ],
      ),
    );
  }

  Widget _buildCommentThread(CommunityComment comment, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSingleCommentCard(comment, isDark, isNested: false),
        if (comment.replies.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.only(left: 14.0, top: 6.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 2.0,
                  margin: const EdgeInsets.only(right: 10.0, top: 4.0),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF383A3D) : const Color(0xFFD1D5DB),
                    borderRadius: BorderRadius.circular(1.0),
                  ),
                ),
                Expanded(
                  child: Column(
                    children: comment.replies.map((reply) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 6.0),
                        child: _buildSingleCommentCard(reply, isDark, isNested: true),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildSingleCommentCard(CommunityComment comment, bool isDark, {required bool isNested}) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: isNested ? 4.0 : 6.0, vertical: 4.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 22,
                height: 22,
                decoration: BoxDecoration(
                  color: comment.isOfficial
                      ? const Color(0xFF10B981)
                      : (comment.isOp
                          ? const Color(0xFF2563EB)
                          : (isDark ? const Color(0xFF374151) : const Color(0xFFE2E8F0))),
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Text(
                    comment.author.isNotEmpty ? comment.author[0].toUpperCase() : 'U',
                    style: TextStyle(
                      color: comment.isOfficial || comment.isOp
                          ? Colors.white
                          : (isDark ? Colors.white : Colors.black87),
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 6),
              Flexible(
                child: Text(
                  comment.author,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryText,
                  ),
                ),
              ),
              if (comment.isOp) ...[
                const SizedBox(width: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2563EB),
                    borderRadius: BorderRadius.circular(3.0),
                  ),
                  child: const Text(
                    'OP',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
              if (comment.isOfficial) ...[
                const SizedBox(width: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981),
                    borderRadius: BorderRadius.circular(3.0),
                  ),
                  child: const Text(
                    'OFFICIAL',
                    style: TextStyle(
                      fontSize: 8.5,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
              const SizedBox(width: 5),
              Text('•', style: TextStyle(fontSize: 10, color: AppColors.secondaryText)),
              const SizedBox(width: 5),
              Text(
                comment.timeAgo,
                style: TextStyle(fontSize: 11, color: AppColors.secondaryText),
              ),
            ],
          ),
          const SizedBox(height: 5),
          Padding(
            padding: const EdgeInsets.only(left: 28.0),
            child: Text(
              comment.content,
              style: TextStyle(
                fontSize: 13,
                height: 1.4,
                color: isDark ? const Color(0xFFE5E7EB) : const Color(0xFF1F2937),
              ),
            ),
          ),
          const SizedBox(height: 5),
          Padding(
            padding: const EdgeInsets.only(left: 24.0),
            child: Row(
              children: [
                GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () {
                    Clipboard.setData(ClipboardData(text: comment.content));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Comment copied')),
                    );
                  },
                  child: Padding(
                    padding: const EdgeInsets.all(4.0),
                    child: Icon(Icons.more_vert_rounded, size: 15, color: AppColors.secondaryText),
                  ),
                ),
                const SizedBox(width: 6),
                GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => _startReply(comment),
                  child: Padding(
                    padding: const EdgeInsets.all(4.0),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Transform.flip(
                          flipX: true,
                          child: Icon(Icons.reply_rounded, size: 14, color: AppColors.secondaryText),
                        ),
                        const SizedBox(width: 3),
                        Text(
                          'Reply',
                          style: TextStyle(fontSize: 11, color: AppColors.secondaryText, fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                  ),
                ),
                const Spacer(),
                // Vote Pill
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () => _toggleCommentUpvote(comment),
                      child: Padding(
                        padding: const EdgeInsets.all(3.0),
                        child: Icon(
                          Icons.arrow_upward_rounded,
                          size: 14,
                          color: comment.isUpvoted ? const Color(0xFFFF4500) : AppColors.secondaryText,
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 2.0),
                      child: Text(
                        '${comment.upvotes}',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: comment.isUpvoted
                              ? const Color(0xFFFF4500)
                              : (comment.isDownvoted ? const Color(0xFF7193FF) : AppColors.secondaryText),
                        ),
                      ),
                    ),
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () => _toggleCommentDownvote(comment),
                      child: Padding(
                        padding: const EdgeInsets.all(3.0),
                        child: Icon(
                          Icons.arrow_downward_rounded,
                          size: 14,
                          color: comment.isDownvoted ? const Color(0xFF7193FF) : AppColors.secondaryText,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomCommentBar(bool isDark) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1A1A1B) : Colors.white,
        border: Border(
          top: BorderSide(
            color: isDark ? const Color(0xFF2D2E30) : const Color(0xFFE5E7EB),
            width: 1.0,
          ),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_replyingTo != null) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
              margin: const EdgeInsets.only(bottom: 6.0),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF272729) : const Color(0xFFF3F4F6),
                borderRadius: BorderRadius.circular(6.0),
              ),
              child: Row(
                children: [
                  Icon(Icons.reply_rounded, size: 13, color: AppColors.secondaryText),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      'Replying to u/${_replyingTo!.author}...',
                      style: TextStyle(fontSize: 11, color: AppColors.secondaryText),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  GestureDetector(
                    onTap: () => setState(() => _replyingTo = null),
                    child: Icon(Icons.close_rounded, size: 14, color: AppColors.secondaryText),
                  ),
                ],
              ),
            ),
          ],
          Row(
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF272729) : const Color(0xFFF3F4F6),
                    borderRadius: BorderRadius.circular(20.0),
                    border: Border.all(
                      color: isDark ? const Color(0xFF383A3D) : const Color(0xFFE5E7EB),
                      width: 1.0,
                    ),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 12.0),
                  child: TextField(
                    controller: _commentController,
                    focusNode: _focusNode,
                    style: TextStyle(fontSize: 13, color: AppColors.primaryText),
                    decoration: InputDecoration(
                      hintText: _replyingTo != null ? 'Write your reply...' : 'Add a comment...',
                      hintStyle: TextStyle(fontSize: 12.5, color: AppColors.mutedText),
                      border: InputBorder.none,
                      isDense: true,
                      contentPadding: const EdgeInsets.symmetric(vertical: 9.0),
                    ),
                    onSubmitted: (_) => _submitComment(),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              GestureDetector(
                onTap: _submitComment,
                child: Container(
                  width: 34,
                  height: 34,
                  decoration: const BoxDecoration(
                    color: Color(0xFFFF4500),
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: Icon(Icons.arrow_upward_rounded, size: 18, color: Colors.white),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
