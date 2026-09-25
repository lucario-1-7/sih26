import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/community_issue_model.dart';
import '../services/theme_service.dart';
import '../theme/app_theme.dart';
import '../widgets/community_issue_card.dart';

/// Old Reddit Mobile UI Style Discussions / Comments Screen
class CommunityDiscussionScreen extends StatefulWidget {
  final CommunityIssue issue;
  final VoidCallback? onIssueUpdated;

  const CommunityDiscussionScreen({
    super.key,
    required this.issue,
    this.onIssueUpdated,
  });

  @override
  State<CommunityDiscussionScreen> createState() => _CommunityDiscussionScreenState();
}

class _CommunityDiscussionScreenState extends State<CommunityDiscussionScreen> {
  final TextEditingController _commentController = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  String _sortBy = 'best'; // 'best', 'top', 'new'
  CommunityComment? _replyingTo;

  @override
  void dispose() {
    _commentController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _togglePostUpvote() {
    setState(() {
      if (widget.issue.isUpvoted) {
        widget.issue.upvotes--;
        widget.issue.isUpvoted = false;
      } else {
        if (widget.issue.isDownvoted) {
          widget.issue.upvotes += 2;
          widget.issue.isDownvoted = false;
        } else {
          widget.issue.upvotes++;
        }
        widget.issue.isUpvoted = true;
      }
    });
    widget.onIssueUpdated?.call();
  }

  void _togglePostDownvote() {
    setState(() {
      if (widget.issue.isDownvoted) {
        widget.issue.upvotes++;
        widget.issue.isDownvoted = false;
      } else {
        if (widget.issue.isUpvoted) {
          widget.issue.upvotes -= 2;
          widget.issue.isUpvoted = false;
        } else {
          widget.issue.upvotes--;
        }
        widget.issue.isDownvoted = true;
      }
    });
    widget.onIssueUpdated?.call();
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

  void _startReply(CommunityComment targetComment) {
    setState(() {
      _replyingTo = targetComment;
    });
    _focusNode.requestFocus();
  }

  void _cancelReply() {
    setState(() {
      _replyingTo = null;
    });
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

    setState(() {
      if (_replyingTo != null) {
        _replyingTo!.replies.add(newComment);
        _replyingTo = null;
      } else {
        widget.issue.comments.insert(0, newComment);
      }
      widget.issue.commentsCount = widget.issue.comments.length;
    });

    _commentController.clear();
    FocusScope.of(context).unfocus();
    widget.onIssueUpdated?.call();
  }

  List<CommunityComment> _getSortedComments() {
    final list = List<CommunityComment>.from(widget.issue.comments);
    if (_sortBy == 'top') {
      list.sort((a, b) => b.upvotes.compareTo(a.upvotes));
    } else if (_sortBy == 'new') {
      list.sort((a, b) => b.id.compareTo(a.id));
    }
    return list;
  }

  @override
  Widget build(BuildContext context) {
    final isDark = ThemeService.instance.isDark;
    final sortedComments = _getSortedComments();

    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF0E0E10) : const Color(0xFFF9FAFB),
      appBar: AppBar(
        backgroundColor: isDark ? const Color(0xFF1A1A1B) : Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: Icon(
            Icons.arrow_back_ios_new_rounded,
            size: 20,
            color: AppColors.primaryText,
          ),
          onPressed: () => Navigator.pop(context),
        ),
        titleSpacing: 0,
        title: Row(
          children: [
            Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                color: const Color(0xFFFF4500).withValues(alpha: 0.18),
                shape: BoxShape.circle,
              ),
              child: const Center(
                child: Text('c/', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFFF4500))),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                widget.issue.subredditName,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryText,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.share_outlined, size: 20, color: AppColors.primaryText),
            onPressed: () {
              Clipboard.setData(ClipboardData(text: 'https://civicdesk.org/issue/${widget.issue.id}'));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Issue link copied to clipboard')),
              );
            },
          ),
          IconButton(
            icon: Icon(Icons.more_vert_rounded, size: 20, color: AppColors.primaryText),
            onPressed: () {},
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Scrollable Content: Post Card + Discussion Comments
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.only(top: 0.0, bottom: 20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // TOP POST CARD (Reddit Mobile style, NO blue image!)
                    CommunityIssueCard(
                      issue: widget.issue,
                      isDetailView: true,
                      onUpvote: _togglePostUpvote,
                      onDownvote: _togglePostDownvote,
                      onCommentTap: () {
                        _focusNode.requestFocus();
                      },
                      onTap: () {},
                    ),

                    const SizedBox(height: 8),

                    // DISCUSSION HEADER: Comments Count + Sort Selector
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Text(
                                'COMMENTS (${widget.issue.comments.length})',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w800,
                                  color: AppColors.secondaryText,
                                  letterSpacing: 0.6,
                                ),
                              ),
                            ],
                          ),

                          // Sort Dropdown
                          PopupMenuButton<String>(
                            initialValue: _sortBy,
                            onSelected: (val) {
                              setState(() {
                                _sortBy = val;
                              });
                            },
                            color: isDark ? const Color(0xFF272729) : Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            itemBuilder: (ctx) => [
                              const PopupMenuItem(value: 'best', child: Text('🔥 Best Comments')),
                              const PopupMenuItem(value: 'top', child: Text('⬆️ Top Upvoted')),
                              const PopupMenuItem(value: 'new', child: Text('✨ Newest First')),
                            ],
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
                              decoration: BoxDecoration(
                                color: isDark ? const Color(0xFF272729) : const Color(0xFFF3F4F6),
                                borderRadius: BorderRadius.circular(14.0),
                                border: Border.all(
                                  color: isDark ? const Color(0xFF383A3D) : const Color(0xFFE5E7EB),
                                  width: 0.8,
                                ),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    _sortBy == 'best'
                                        ? 'Best'
                                        : (_sortBy == 'top' ? 'Top' : 'New'),
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w600,
                                      color: AppColors.primaryText,
                                    ),
                                  ),
                                  const SizedBox(width: 4),
                                  Icon(Icons.keyboard_arrow_down_rounded, size: 16, color: AppColors.secondaryText),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    Divider(
                      height: 12,
                      thickness: 0.8,
                      color: isDark ? const Color(0xFF272729) : const Color(0xFFE5E7EB),
                    ),

                    const SizedBox(height: 6),

                    // COMMENTS LIST (OLD REDDIT MOBILE UI WITH NESTED THREAD LINES!)
                    if (sortedComments.isEmpty)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 40.0),
                        child: Center(
                          child: Column(
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
                        ),
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: sortedComments.length,
                        separatorBuilder: (ctx, i) => Divider(
                          height: 20,
                          thickness: 0.6,
                          color: isDark ? const Color(0xFF222428) : const Color(0xFFF1F5F9),
                        ),
                        itemBuilder: (ctx, index) {
                          final comment = sortedComments[index];
                          return _buildCommentThread(comment, isDark);
                        },
                      ),

                    const SizedBox(height: 30),
                  ],
                ),
              ),
            ),

            // BOTTOM DOCKED COMMENT BAR (Old Reddit Mobile Input)
            _buildBottomCommentBar(isDark),
          ],
        ),
      ),
    );
  }

  /// Builds a comment and its nested threaded replies with the signature Reddit indentation line
  Widget _buildCommentThread(CommunityComment comment, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Parent Comment Item
        _buildSingleCommentCard(comment, isDark, isNested: false),

        // Nested Replies (Indented with vertical thread line, matching screenshot!)
        if (comment.replies.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.only(left: 14.0, top: 6.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Vertical Thread Guide Line
                Container(
                  width: 2.0,
                  margin: const EdgeInsets.only(right: 12.0, top: 4.0),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF383A3D) : const Color(0xFFD1D5DB),
                    borderRadius: BorderRadius.circular(1.0),
                  ),
                ),
                // Nested Replies Column
                Expanded(
                  child: Column(
                    children: comment.replies.map((reply) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8.0),
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

  /// Single Reddit Comment View matching the exact structure from the reference screenshot
  Widget _buildSingleCommentCard(CommunityComment comment, bool isDark, {required bool isNested}) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: isNested ? 4.0 : 8.0, vertical: 4.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Author row: Avatar + Username + OP/Official Badge + Timestamp
          Row(
            children: [
              // User Avatar
              Container(
                width: 24,
                height: 24,
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
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 7),

              // Username: u/username
              Flexible(
                child: Text(
                  comment.author,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 12.5,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryText,
                  ),
                ),
              ),

              // OP Badge (Blue pill, exactly like "manor2003 OP" in screenshot!)
              if (comment.isOp) ...[
                const SizedBox(width: 5),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2563EB),
                    borderRadius: BorderRadius.circular(4.0),
                  ),
                  child: const Text(
                    'OP',
                    style: TextStyle(
                      fontSize: 9.5,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                      letterSpacing: 0.3,
                    ),
                  ),
                ),
              ],

              // Official Govt Badge
              if (comment.isOfficial) ...[
                const SizedBox(width: 5),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981),
                    borderRadius: BorderRadius.circular(4.0),
                  ),
                  child: const Text(
                    'OFFICIAL',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                      letterSpacing: 0.3,
                    ),
                  ),
                ),
              ],

              const SizedBox(width: 5),
              Text('•', style: TextStyle(fontSize: 11, color: AppColors.secondaryText)),
              const SizedBox(width: 5),

              // Timestamp
              Text(
                comment.timeAgo,
                style: TextStyle(
                  fontSize: 11.5,
                  color: AppColors.secondaryText,
                ),
              ),
            ],
          ),

          const SizedBox(height: 6),

          // 2. Comment Content Body
          Padding(
            padding: const EdgeInsets.only(left: 31.0),
            child: Text(
              comment.content,
              style: TextStyle(
                fontSize: 13.5,
                height: 1.42,
                color: isDark ? const Color(0xFFE5E7EB) : const Color(0xFF1F2937),
              ),
            ),
          ),

          const SizedBox(height: 6),

          // 3. Comment Action Footer: [ ⋮ ]  [ ↩ Reply ]  [ ↑ 27 ↓ ] (Matching screenshot!)
          Padding(
            padding: const EdgeInsets.only(left: 28.0),
            child: Row(
              children: [
                // Overflow Three Dots Menu
                GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () {
                    Clipboard.setData(ClipboardData(text: comment.content));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Comment copied to clipboard')),
                    );
                  },
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 6.0, vertical: 4.0),
                    child: Icon(
                      Icons.more_vert_rounded,
                      size: 16,
                      color: AppColors.secondaryText,
                    ),
                  ),
                ),

                const SizedBox(width: 8),

                // Reply Button
                GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => _startReply(comment),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 6.0, vertical: 4.0),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Transform.flip(
                          flipX: true,
                          child: Icon(
                            Icons.reply_rounded,
                            size: 15,
                            color: AppColors.secondaryText,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'Reply',
                          style: TextStyle(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w600,
                            color: AppColors.secondaryText,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const Spacer(),

                // Comment Upvote / Downvote Pill: [ ↑  27  ↓ ]
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0, vertical: 2.0),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Upvote Arrow
                      GestureDetector(
                        behavior: HitTestBehavior.opaque,
                        onTap: () => _toggleCommentUpvote(comment),
                        child: Padding(
                          padding: const EdgeInsets.all(4.0),
                          child: Icon(
                            Icons.arrow_upward_rounded,
                            size: 15,
                            color: comment.isUpvoted
                                ? const Color(0xFFFF4500)
                                : AppColors.secondaryText,
                          ),
                        ),
                      ),
                      // Upvote Count
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 2.0),
                        child: Text(
                          '${comment.upvotes}',
                          style: TextStyle(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w700,
                            color: comment.isUpvoted
                                ? const Color(0xFFFF4500)
                                : (comment.isDownvoted
                                    ? const Color(0xFF7193FF)
                                    : AppColors.secondaryText),
                          ),
                        ),
                      ),
                      // Downvote Arrow
                      GestureDetector(
                        behavior: HitTestBehavior.opaque,
                        onTap: () => _toggleCommentDownvote(comment),
                        child: Padding(
                          padding: const EdgeInsets.all(4.0),
                          child: Icon(
                            Icons.arrow_downward_rounded,
                            size: 15,
                            color: comment.isDownvoted
                                ? const Color(0xFF7193FF)
                                : AppColors.secondaryText,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Bottom docked comment bar matching Old Reddit Mobile UI
  Widget _buildBottomCommentBar(bool isDark) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 10.0),
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
          // Replying indicator (if replying to a specific comment)
          if (_replyingTo != null) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 4.0),
              margin: const EdgeInsets.only(bottom: 8.0),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF272729) : const Color(0xFFF3F4F6),
                borderRadius: BorderRadius.circular(8.0),
              ),
              child: Row(
                children: [
                  Icon(Icons.reply_rounded, size: 14, color: AppColors.secondaryText),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Replying to u/${_replyingTo!.author}...',
                      style: TextStyle(
                        fontSize: 11.5,
                        color: AppColors.secondaryText,
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  GestureDetector(
                    onTap: _cancelReply,
                    child: Icon(Icons.close_rounded, size: 16, color: AppColors.secondaryText),
                  ),
                ],
              ),
            ),
          ],

          Row(
            children: [
              // User avatar
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: isDark ? const Color(0xFF383A3D) : const Color(0xFFE2E8F0),
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Icon(Icons.person_rounded, size: 18, color: AppColors.secondaryText),
                ),
              ),
              const SizedBox(width: 10),

              // Comment input field
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF272729) : const Color(0xFFF3F4F6),
                    borderRadius: BorderRadius.circular(22.0),
                    border: Border.all(
                      color: isDark ? const Color(0xFF383A3D) : const Color(0xFFE5E7EB),
                      width: 1.0,
                    ),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 14.0),
                  child: TextField(
                    controller: _commentController,
                    focusNode: _focusNode,
                    style: TextStyle(
                      fontSize: 13.5,
                      color: AppColors.primaryText,
                    ),
                    decoration: InputDecoration(
                      hintText: _replyingTo != null
                          ? 'Write your reply...'
                          : 'Add a comment...',
                      hintStyle: TextStyle(
                        fontSize: 13,
                        color: AppColors.mutedText,
                      ),
                      border: InputBorder.none,
                      isDense: true,
                      contentPadding: const EdgeInsets.symmetric(vertical: 10.0),
                    ),
                    onSubmitted: (_) => _submitComment(),
                  ),
                ),
              ),

              const SizedBox(width: 8),

              // Send button
              GestureDetector(
                onTap: _submitComment,
                child: Container(
                  width: 36,
                  height: 36,
                  decoration: const BoxDecoration(
                    color: Color(0xFFFF4500), // Reddit Orange
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: Icon(
                      Icons.arrow_upward_rounded,
                      size: 20,
                      color: Colors.white,
                    ),
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
