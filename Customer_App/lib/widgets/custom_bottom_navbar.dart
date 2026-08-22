import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class CustomBottomNavbar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTabSelected;
  final VoidCallback onAddPressed;

  const CustomBottomNavbar({
    super.key,
    required this.currentIndex,
    required this.onTabSelected,
    required this.onAddPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: AppColors.background,
        border: Border(
          top: BorderSide(color: AppColors.border, width: 1.0),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Container(
          height: 64,
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(
                index: 0,
                icon: FeatherIcons.home,
                label: 'Home',
                context: context,
              ),
              _buildNavItem(
                index: 1,
                icon: FeatherIcons.fileText,
                label: 'My Issues',
                context: context,
              ),
              _buildNavItem(
                index: 2,
                icon: FeatherIcons.edit3,
                label: 'File Grievance',
                context: context,
              ),
              _buildNavItem(
                index: 3,
                icon: FeatherIcons.user,
                label: 'Profile',
                context: context,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required int index,
    required IconData icon,
    required String label,
    required BuildContext context,
    VoidCallback? onTap,
  }) {
    final isSelected = currentIndex == index;
    final color = isSelected ? AppColors.primaryText : AppColors.mutedText;

    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap ?? () => onTabSelected(index),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 6.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 20,
              color: color,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: AppTypography.supporting(context).copyWith(
                fontSize: 10,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
