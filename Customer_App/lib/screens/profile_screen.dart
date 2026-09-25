import 'package:customer_app/theme/feather_icons.dart';
import 'package:flutter/material.dart';
import '../services/theme_service.dart';
import '../theme/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: ThemeService.instance,
      builder: (context, _) {
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
              'Citizen Profile',
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
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Column(
                      children: [
                        Container(
                          width: 84,
                          height: 84,
                          decoration: BoxDecoration(
                            color: AppColors.inputBackground,
                            shape: BoxShape.circle,
                            border: Border.all(color: AppColors.border, width: 1.5),
                          ),
                          child: Center(
                            child: Icon(
                              FeatherIcons.user,
                              size: 38,
                              color: AppColors.primaryText,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Dhyan Kannoth',
                          style: AppTypography.heading(context).copyWith(
                            fontSize: 22,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Verified Citizen • Chennai, TN',
                          style: AppTypography.supporting(context).copyWith(
                            fontSize: 14,
                            color: AppColors.secondaryText,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 32),
                  Divider(height: 1, thickness: 1, color: AppColors.divider),
                  const SizedBox(height: 24),

                  _buildProfileField(context, 'Full Name', 'Dhyan Kannoth'),
                  const SizedBox(height: 16),
                  _buildProfileField(context, 'Phone Number', '+91 98765 43210'),
                  const SizedBox(height: 16),
                  _buildProfileField(context, 'Email', 'dhyan@janseva.gov.in'),
                  const SizedBox(height: 16),
                  _buildProfileField(context, 'Preferred Language', 'English'),
                  const SizedBox(height: 16),
                  _buildProfileField(
                    context,
                    'Current Theme',
                    ThemeService.instance.themeMode == ThemeMode.system
                        ? 'System Default'
                        : (ThemeService.instance.isDark ? 'Dark Mode' : 'Light Mode'),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildProfileField(
      BuildContext context, String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTypography.supporting(context).copyWith(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: AppColors.mutedText,
          ),
        ),
        const SizedBox(height: 6),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
          decoration: BoxDecoration(
            color: AppColors.inputBackground,
            borderRadius: BorderRadius.circular(12.0),
            border: Border.all(color: AppColors.border, width: 1.0),
          ),
          child: Text(
            value,
            style: AppTypography.inputText(context).copyWith(
              fontSize: 15,
            ),
          ),
        ),
      ],
    );
  }
}
