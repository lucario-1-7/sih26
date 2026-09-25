import 'package:customer_app/theme/feather_icons.dart';
import 'package:flutter/material.dart';
import '../services/theme_service.dart';
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
    return AnimatedBuilder(
      animation: ThemeService.instance,
      builder: (context, _) {
        final currentMode = ThemeService.instance.themeMode;

        return Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(
            backgroundColor: AppColors.background,
            elevation: 0,
            leading: IconButton(
              icon: Icon(FeatherIcons.arrowLeft, color: AppColors.primaryText),
              onPressed: () => Navigator.pop(context),
            ),
            title: Text(
              'Settings',
              style: AppTypography.heading(context).copyWith(
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            bottom: PreferredSize(
              preferredSize: const Size.fromHeight(1.0),
              child: Divider(height: 1, thickness: 1, color: AppColors.divider),
            ),
          ),
          body: SafeArea(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
              children: [
                // Appearance & Theme Mode Section
                Text(
                  'Appearance',
                  style: AppTypography.heading(context).copyWith(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Customize how Social Serve looks on your device',
                  style: AppTypography.supporting(context).copyWith(
                    fontSize: 13,
                    color: AppColors.secondaryText,
                  ),
                ),
                const SizedBox(height: 14),

                // Theme Mode Selector Cards
                Row(
                  children: [
                    _buildThemeCard(
                      context: context,
                      title: 'System',
                      subtitle: 'Auto Match',
                      icon: FeatherIcons.smartphone,
                      isSelected: currentMode == ThemeMode.system,
                      onTap: () => ThemeService.instance.setThemeMode(ThemeMode.system),
                    ),
                    const SizedBox(width: 10),
                    _buildThemeCard(
                      context: context,
                      title: 'Light',
                      subtitle: 'Clean & Crisp',
                      icon: FeatherIcons.sun,
                      isSelected: currentMode == ThemeMode.light,
                      onTap: () => ThemeService.instance.setThemeMode(ThemeMode.light),
                    ),
                    const SizedBox(width: 10),
                    _buildThemeCard(
                      context: context,
                      title: 'Dark',
                      subtitle: 'Sleek Dark',
                      icon: FeatherIcons.moon,
                      isSelected: currentMode == ThemeMode.dark,
                      onTap: () => ThemeService.instance.setThemeMode(ThemeMode.dark),
                    ),
                  ],
                ),

                const SizedBox(height: 24),
                Divider(height: 1, thickness: 1, color: AppColors.divider),
                const SizedBox(height: 24),

                // Notifications Section
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
                Divider(height: 1, thickness: 1, color: AppColors.divider),
                const SizedBox(height: 24),

                // About Section
                Text(
                  'About Social Serve',
                  style: AppTypography.heading(context).copyWith(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(16.0),
                  decoration: BoxDecoration(
                    color: AppColors.inputBackground,
                    borderRadius: BorderRadius.circular(12.0),
                    border: Border.all(color: AppColors.border, width: 1.0),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 36,
                            height: 36,
                            decoration: BoxDecoration(
                              color: AppColors.primaryButton,
                              borderRadius: BorderRadius.circular(8.0),
                            ),
                            child: Center(
                              child: Icon(
                                FeatherIcons.shield,
                                size: 18,
                                color: AppColors.buttonText,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Social Serve Citizen v1.0.0',
                                style: AppTypography.heading(context).copyWith(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Privately Owned & Operated • Independent Platform',
                                style: AppTypography.supporting(context).copyWith(
                                  fontSize: 11.5,
                                  color: AppColors.mutedText,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 4.0),
                        decoration: BoxDecoration(
                          color: AppColors.primaryButton.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(6.0),
                          border: Border.all(color: AppColors.primaryButton.withValues(alpha: 0.25), width: 0.8),
                        ),
                        child: Text(
                          'Independent Private Entity • Separate from Government',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: AppColors.primaryButton,
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Social Serve is a privately owned and operated civic technology platform. We empower citizens to collectively highlight social problems, independently monitor resolutions, and coordinate with responsible providers and operators.',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 13,
                          height: 1.45,
                          color: AppColors.secondaryText,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildThemeCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14.0),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 220),
          padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 14.0),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.inputBackground : AppColors.background,
            borderRadius: BorderRadius.circular(14.0),
            border: Border.all(
              color: isSelected ? AppColors.primaryText : AppColors.border,
              width: isSelected ? 1.8 : 1.0,
            ),
          ),
          child: Column(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.primaryButton : AppColors.inputBackground,
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Icon(
                    icon,
                    size: 18,
                    color: isSelected ? AppColors.buttonText : AppColors.secondaryText,
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Text(
                title,
                style: AppTypography.heading(context).copyWith(
                  fontSize: 13,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                  color: isSelected ? AppColors.primaryText : AppColors.secondaryText,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 10,
                  color: AppColors.mutedText,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
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
