import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _smsNotifications = true;
  bool _emailAlerts = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(FeatherIcons.arrowLeft, color: AppColors.primaryText),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Settings',
          style: AppTypography.heading(context).copyWith(
            fontSize: 18,
            fontWeight: FontWeight.w700,
          ),
        ),
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1.0),
          child: Divider(height: 1, thickness: 1, color: AppColors.divider),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          children: [
            Text(
              'Notifications',
              style: AppTypography.heading(context).copyWith(
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 12),
            _buildSwitchTile(
              title: 'SMS Status Alerts',
              subtitle: 'Receive text updates when issue status changes',
              value: _smsNotifications,
              onChanged: (val) => setState(() => _smsNotifications = val),
            ),
            _buildSwitchTile(
              title: 'Email Summary Reports',
              subtitle: 'Weekly summary of resolved civic issues in your area',
              value: _emailAlerts,
              onChanged: (val) => setState(() => _emailAlerts = val),
            ),
            const SizedBox(height: 24),
            const Divider(height: 1, thickness: 1, color: AppColors.divider),
            const SizedBox(height: 24),
            Text(
              'About Social Serve',
              style: AppTypography.heading(context).copyWith(
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Social Serve v1.0.0 (Citizen App)\nEmpowering citizens to report civic grievances and track institutional progress in real-time.',
              style: AppTypography.supporting(context).copyWith(
                fontSize: 14,
                height: 1.45,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
      decoration: BoxDecoration(
        color: AppColors.inputBackground,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTypography.heading(context).copyWith(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: AppTypography.supporting(context).copyWith(
                    fontSize: 12,
                    color: AppColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            activeThumbColor: AppColors.primaryText,
            activeTrackColor: AppColors.border,
            inactiveThumbColor: AppColors.mutedText,
            inactiveTrackColor: AppColors.inputBackground,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}
