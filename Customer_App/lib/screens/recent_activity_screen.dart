import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';

class NotificationItemData {
  final String id;
  final String title;
  final String description;
  final String time;
  final IconData icon;
  final Color iconColor;
  final Color iconBgColor;
  bool isRead;

  NotificationItemData({
    required this.id,
    required this.title,
    required this.description,
    required this.time,
    required this.icon,
    required this.iconColor,
    required this.iconBgColor,
    this.isRead = false,
  });
}

class RecentActivityScreen extends StatefulWidget {
  final List<IssueItem>? issues;

  const RecentActivityScreen({
    super.key,
    this.issues,
  });

  @override
  State<RecentActivityScreen> createState() => _RecentActivityScreenState();
}

class _RecentActivityScreenState extends State<RecentActivityScreen> {
  late List<NotificationItemData> _notifications;

  @override
  void initState() {
    super.initState();
    _notifications = [
      NotificationItemData(
        id: 'notif-1',
        title: 'App Update',
        description:
            'New update out now! Discover improved grievance tracking and faster response tools.',
        time: '2 hours ago',
        icon: FeatherIcons.refreshCw,
        iconColor: const Color(0xFF10B981),
        iconBgColor: const Color(0xFFE6F7F0),
        isRead: false,
      ),
      NotificationItemData(
        id: 'notif-2',
        title: 'Civic Advisory',
        description:
            'Scheduled water supply maintenance in Sector 4 starting tomorrow at 8:00 AM.',
        time: 'Yesterday',
        icon: FeatherIcons.volume2,
        iconColor: const Color(0xFFF97316),
        iconBgColor: const Color(0xFFFFF3EB),
        isRead: false,
      ),
      NotificationItemData(
        id: 'notif-3',
        title: 'Grievance Resolved',
        description:
            'Streetlight outage on 5th Cross marked as resolved by the Municipal Electrical Division.',
        time: '2 days ago',
        icon: FeatherIcons.checkCircle,
        iconColor: const Color(0xFF10B981),
        iconBgColor: const Color(0xFFE6F7F0),
        isRead: false,
      ),
      NotificationItemData(
        id: 'notif-4',
        title: 'Inspection Scheduled',
        description:
            'Road damage inspection near Main Road assigned to Public Works Department field unit.',
        time: '3 days ago',
        icon: FeatherIcons.truck,
        iconColor: const Color(0xFF3B82F6),
        iconBgColor: const Color(0xFFEFF6FF),
        isRead: true,
      ),
      NotificationItemData(
        id: 'notif-5',
        title: 'Grievance Registered',
        description:
            'Your grievance ISS-2026-001 has been received and routed to the municipal triage desk.',
        time: '5 days ago',
        icon: FeatherIcons.fileText,
        iconColor: const Color(0xFF8B5CF6),
        iconBgColor: const Color(0xFFF5F3FF),
        isRead: true,
      ),
    ];
  }

  void _markAsRead(String id) {
    setState(() {
      final index = _notifications.indexWhere((n) => n.id == id);
      if (index != -1) {
        _notifications[index].isRead = true;
      }
    });
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(FeatherIcons.checkCircle, color: Colors.white, size: 16),
            const SizedBox(width: 8),
            Text(
              'Marked as read',
              style: GoogleFonts.inter(fontSize: 13, color: Colors.white),
            ),
          ],
        ),
        backgroundColor: const Color(0xFF2563EB),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
        duration: const Duration(milliseconds: 1500),
      ),
    );
  }

  void _toggleRead(String id) {
    setState(() {
      final index = _notifications.indexWhere((n) => n.id == id);
      if (index != -1) {
        _notifications[index].isRead = !_notifications[index].isRead;
      }
    });
  }

  void _deleteNotification(String id) {
    setState(() {
      _notifications.removeWhere((n) => n.id == id);
    });
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Notification deleted',
          style: GoogleFonts.inter(fontSize: 13, color: Colors.white),
        ),
        backgroundColor: const Color(0xFF1F2937),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(
            FeatherIcons.arrowLeft,
            color: AppColors.primaryText,
            size: 22,
          ),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'NOTIFICATIONS',
          style: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.8,
            color: AppColors.primaryText,
          ),
        ),
      ),
      body: SafeArea(
        child: _notifications.isEmpty
            ? _buildEmptyState()
            : ListView.builder(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
                itemCount: _notifications.length,
                itemBuilder: (context, index) {
                  final item = _notifications[index];
                  return _SwipeableNotificationTile(
                    key: ValueKey(item.id),
                    item: item,
                    onMarkAsRead: () => _markAsRead(item.id),
                    onToggleRead: () => _toggleRead(item.id),
                    onDelete: () => _deleteNotification(item.id),
                  );
                },
              ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: const BoxDecoration(
              color: AppColors.inputBackground,
              shape: BoxShape.circle,
            ),
            child: const Center(
              child: Icon(
                FeatherIcons.bell,
                size: 32,
                color: AppColors.mutedText,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'No Notifications',
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: AppColors.primaryText,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'You are all caught up!',
            style: GoogleFonts.inter(
              fontSize: 13.5,
              fontWeight: FontWeight.w400,
              color: AppColors.secondaryText,
            ),
          ),
        ],
      ),
    );
  }
}

class _SwipeableNotificationTile extends StatefulWidget {
  final NotificationItemData item;
  final VoidCallback onMarkAsRead;
  final VoidCallback onToggleRead;
  final VoidCallback onDelete;

  const _SwipeableNotificationTile({
    super.key,
    required this.item,
    required this.onMarkAsRead,
    required this.onToggleRead,
    required this.onDelete,
  });

  @override
  State<_SwipeableNotificationTile> createState() => _SwipeableNotificationTileState();
}

class _SwipeableNotificationTileState extends State<_SwipeableNotificationTile>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _animation;
  double _dragOffset = 0.0;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    );
    _animController.addListener(() {
      setState(() {
        _dragOffset = _animation.value;
      });
    });
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  void _animateBack() {
    _animation = Tween<double>(
      begin: _dragOffset,
      end: 0.0,
    ).animate(CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic));
    _animController.forward(from: 0.0);
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Strict cap: only pulled till half the section
        final maxDrag = constraints.maxWidth * 0.5;

        return Container(
          margin: const EdgeInsets.symmetric(vertical: 6.0),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14.0),
          ),
          clipBehavior: Clip.antiAlias,
          child: Stack(
            children: [
              // Blue background revealed on the left side
              Positioned.fill(
                child: Container(
                  alignment: Alignment.centerLeft,
                  padding: const EdgeInsets.symmetric(horizontal: 18.0),
                  color: const Color(0xFF2563EB),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        FeatherIcons.check,
                        color: Colors.white,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Mark as read',
                        style: GoogleFonts.inter(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Foreground card sliding up to maximum half the width
              Transform.translate(
                offset: Offset(_dragOffset, 0),
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onHorizontalDragStart: (_) {
                    _animController.stop();
                  },
                  onHorizontalDragUpdate: (details) {
                    setState(() {
                      // Clamp between 0 and half the card width (maxDrag)
                      _dragOffset = (_dragOffset + details.primaryDelta!).clamp(0.0, maxDrag);
                    });
                  },
                  onHorizontalDragEnd: (details) {
                    if (_dragOffset >= maxDrag * 0.5 && !widget.item.isRead) {
                      widget.onMarkAsRead();
                    }
                    _animateBack();
                  },
                  onHorizontalDragCancel: () {
                    _animateBack();
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
                    color: AppColors.background,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Circular leading icon
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: widget.item.iconBgColor,
                            shape: BoxShape.circle,
                          ),
                          child: Center(
                            child: Icon(
                              widget.item.icon,
                              color: widget.item.iconColor,
                              size: 20,
                            ),
                          ),
                        ),
                        const SizedBox(width: 14),

                        // Content area
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Title + Unread indicator
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      widget.item.title,
                                      style: GoogleFonts.inter(
                                        fontSize: 15.5,
                                        fontWeight: widget.item.isRead
                                            ? FontWeight.w600
                                            : FontWeight.w700,
                                        color: AppColors.primaryText,
                                      ),
                                    ),
                                  ),
                                  if (!widget.item.isRead)
                                    Container(
                                      width: 7,
                                      height: 7,
                                      margin: const EdgeInsets.only(right: 6.0),
                                      decoration: const BoxDecoration(
                                        color: Color(0xFF2563EB),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 4),

                              // Description
                              Text(
                                widget.item.description,
                                style: GoogleFonts.inter(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w400,
                                  color: widget.item.isRead
                                      ? AppColors.mutedText
                                      : AppColors.secondaryText,
                                  height: 1.35,
                                ),
                              ),
                              const SizedBox(height: 6),

                              // Time ago
                              Text(
                                widget.item.time,
                                style: GoogleFonts.inter(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w400,
                                  color: AppColors.mutedText,
                                ),
                              ),
                            ],
                          ),
                        ),

                        // 3-dots popup menu
                        PopupMenuButton<String>(
                          icon: const Icon(
                            FeatherIcons.moreVertical,
                            size: 18,
                            color: AppColors.primaryText,
                          ),
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12.0),
                          ),
                          color: AppColors.background,
                          onSelected: (value) {
                            if (value == 'read') {
                              widget.onToggleRead();
                            } else if (value == 'delete') {
                              widget.onDelete();
                            }
                          },
                          itemBuilder: (BuildContext context) => [
                            PopupMenuItem<String>(
                              value: 'read',
                              height: 40,
                              child: Text(
                                widget.item.isRead ? 'Mark as unread' : 'Mark as read',
                                style: GoogleFonts.inter(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: AppColors.primaryText,
                                ),
                              ),
                            ),
                            PopupMenuItem<String>(
                              value: 'delete',
                              height: 40,
                              child: Text(
                                'Delete',
                                style: GoogleFonts.inter(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: const Color(0xFFEF4444),
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
            ],
          ),
        );
      },
    );
  }
}
