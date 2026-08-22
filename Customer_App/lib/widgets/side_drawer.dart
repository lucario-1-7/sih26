import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

enum DrawerRoute { home, issues, fileIssue, profile, settings }

class SideDrawer extends StatelessWidget {
  final DrawerRoute currentRoute;
  final Function(DrawerRoute route) onSelectRoute;

  const SideDrawer({
    super.key,
    required this.currentRoute,
    required this.onSelectRoute,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: AppColors.background,
      elevation: 0,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.zero,
      ),
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drawer Header
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 24.0, vertical: 28.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Social Serve',
                    style: AppTypography.heading(context).copyWith(
                      fontSize: 24,
                      letterSpacing: -0.6,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Citizen Platform',
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 13,
                      color: AppColors.mutedText,
                    ),
                  ),
                ],
              ),
            ),

            const Divider(
              height: 1,
              thickness: 1,
              color: AppColors.divider,
            ),
            const SizedBox(height: 16),

            // Main Nav Options
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                children: [
                  _buildNavItem(
                    context: context,
                    icon: Icons.home_outlined,
                    activeIcon: Icons.home,
                    label: 'Home',
                    route: DrawerRoute.home,
                  ),
                  _buildNavItem(
                    context: context,
                    icon: Icons.format_list_bulleted_outlined,
                    activeIcon: Icons.format_list_bulleted,
                    label: 'Issues',
                    route: DrawerRoute.issues,
                  ),
                  _buildNavItem(
                    context: context,
                    icon: Icons.add_circle_outline_rounded,
                    activeIcon: Icons.add_circle_rounded,
                    label: 'File an Issue',
                    route: DrawerRoute.fileIssue,
                  ),
                  _buildNavItem(
                    context: context,
                    icon: Icons.person_outline_rounded,
                    activeIcon: Icons.person_rounded,
                    label: 'Profile',
                    route: DrawerRoute.profile,
                  ),
                  _buildNavItem(
                    context: context,
                    icon: Icons.settings_outlined,
                    activeIcon: Icons.settings,
                    label: 'Settings',
                    route: DrawerRoute.settings,
                  ),
                ],
              ),
            ),

            const Divider(
              height: 1,
              thickness: 1,
              color: AppColors.divider,
            ),

            // Logout Option
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
              child: InkWell(
                onTap: () {
                  Navigator.pop(context); // Close drawer
                  // Navigate back to Phone auth screen
                  Navigator.popUntil(context, (route) => route.isFirst);
                },
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16.0, vertical: 14.0),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.logout_rounded,
                        size: 20,
                        color: AppColors.secondaryText,
                      ),
                      const SizedBox(width: 14),
                      Text(
                        'Logout',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 15,
                          fontWeight: FontWeight.w500,
                          color: AppColors.secondaryText,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required BuildContext context,
    required IconData icon,
    required IconData activeIcon,
    required String label,
    required DrawerRoute route,
  }) {
    final isActive = currentRoute == route;

    return Container(
      margin: const EdgeInsets.only(bottom: 6.0),
      decoration: BoxDecoration(
        color: isActive ? AppColors.inputBackground : Colors.transparent,
        borderRadius: BorderRadius.circular(12.0),
        border: isActive
            ? Border.all(color: AppColors.border, width: 1.0)
            : Border.all(color: Colors.transparent, width: 1.0),
      ),
      child: InkWell(
        onTap: () {
          Navigator.pop(context); // Close drawer first
          onSelectRoute(route);
        },
        borderRadius: BorderRadius.circular(12.0),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
          child: Row(
            children: [
              Icon(
                isActive ? activeIcon : icon,
                size: 20,
                color: isActive
                    ? AppColors.primaryText
                    : AppColors.secondaryText,
              ),
              const SizedBox(width: 14),
              Text(
                label,
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 15,
                  fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                  color: isActive
                      ? AppColors.primaryText
                      : AppColors.secondaryText,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
