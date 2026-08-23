import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
import '../models/issue_model.dart';
import '../services/language_service.dart';
import '../theme/app_theme.dart';
import '../widgets/primary_button.dart';

class IssueSuccessScreen extends StatelessWidget {
  final IssueItem createdIssue;

  const IssueSuccessScreen({
    super.key,
    required this.createdIssue,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: LanguageService.instance,
      builder: (context, _) {
        final citizenName = createdIssue.citizenName ?? 'Dhyan Kannoth';
        final citizenEmail = createdIssue.citizenEmail ?? 'dhyan@janseva.gov.in';
        final citizenMobile = createdIssue.citizenMobile ?? '+91 98765 43210';
        final cityWard = createdIssue.cityWard ?? 'Chennai';
        final pincode = createdIssue.pincode ?? '600001';
        final hasPhoto = createdIssue.imagePath != null && createdIssue.imagePath!.isNotEmpty;

        return Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(
            backgroundColor: AppColors.background,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(FeatherIcons.arrowLeft, color: AppColors.primaryText, size: 20),
              onPressed: () => Navigator.pop(context, 'go_home'),
            ),
            title: Text(
              'Grievance Confirmation',
              style: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: AppColors.primaryText,
              ),
            ),
            centerTitle: true,
            actions: [
              IconButton(
                icon: const Icon(FeatherIcons.x, color: AppColors.primaryText, size: 20),
                onPressed: () => Navigator.pop(context, 'go_home'),
              ),
            ],
          ),
          body: SafeArea(
            child: Column(
              children: [
                Expanded(
                  child: SingleChildScrollView(
                    physics: const BouncingScrollPhysics(),
                    padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        const SizedBox(height: 8),

                        // Lottie Successful Animation
                        Center(
                          child: SizedBox(
                            height: 210,
                            child: Lottie.asset(
                              'lib/assets/successful.json',
                              fit: BoxFit.contain,
                              repeat: true,
                              errorBuilder: (context, error, stackTrace) {
                                return Lottie.asset(
                                  'assets/animations/successful.json',
                                  fit: BoxFit.contain,
                                  repeat: true,
                                  errorBuilder: (context, err2, stack2) {
                                    return Container(
                                      width: 100,
                                      height: 100,
                                      decoration: const BoxDecoration(
                                        color: Color(0xFF10B981),
                                        shape: BoxShape.circle,
                                      ),
                                      child: const Icon(
                                        FeatherIcons.check,
                                        color: Colors.white,
                                        size: 48,
                                      ),
                                    );
                                  },
                                );
                              },
                            ),
                          ),
                        ),

                        const SizedBox(height: 16),

                        // Successfully Filed Issue Message
                        Text(
                          LanguageService.instance.currentLanguageCode == 'en'
                              ? 'Successfully Filed Issue'
                              : LanguageService.t('success_title'),
                          textAlign: TextAlign.center,
                          style: GoogleFonts.inter(
                            fontSize: 26,
                            fontWeight: FontWeight.w800,
                            color: AppColors.primaryText,
                            letterSpacing: -0.5,
                          ),
                        ),

                        const SizedBox(height: 22),

                        // OVERVIEW CONTAINER: Filed Grievance Summary
                        Container(
                          width: double.infinity,
                          decoration: BoxDecoration(
                            color: AppColors.background,
                            borderRadius: BorderRadius.circular(16.0),
                            border: Border.all(color: AppColors.border, width: 1.2),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Overview Header with Ref ID
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
                                decoration: const BoxDecoration(
                                  color: AppColors.inputBackground,
                                  borderRadius: BorderRadius.only(
                                    topLeft: Radius.circular(15.0),
                                    topRight: Radius.circular(15.0),
                                  ),
                                  border: Border(
                                    bottom: BorderSide(color: AppColors.border, width: 1.0),
                                  ),
                                ),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      LanguageService.t('reference_id'),
                                      style: GoogleFonts.inter(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w700,
                                        color: AppColors.mutedText,
                                        letterSpacing: 0.6,
                                      ),
                                    ),
                                    Text(
                                      createdIssue.id,
                                      style: GoogleFonts.robotoMono(
                                        fontSize: 13.5,
                                        fontWeight: FontWeight.w700,
                                        color: AppColors.primaryText,
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    // SECTION 1: Contact Info
                                    _buildSectionBadge(1, 'Contact Information'),
                                    const SizedBox(height: 8),
                                    _buildInfoRow(FeatherIcons.user, 'Citizen', citizenName),
                                    const SizedBox(height: 6),
                                    _buildInfoRow(FeatherIcons.mail, 'Email', citizenEmail),
                                    const SizedBox(height: 6),
                                    _buildInfoRow(FeatherIcons.phone, 'Mobile', citizenMobile),

                                    const Padding(
                                      padding: EdgeInsets.symmetric(vertical: 12.0),
                                      child: Divider(height: 1, color: AppColors.divider),
                                    ),

                                    // SECTION 2: Location Details
                                    _buildSectionBadge(2, 'Location Details'),
                                    const SizedBox(height: 8),
                                    _buildInfoRow(FeatherIcons.mapPin, 'Address', createdIssue.location),
                                    const SizedBox(height: 6),
                                    _buildInfoRow(FeatherIcons.compass, 'Ward / PIN', '$cityWard • $pincode'),

                                    const Padding(
                                      padding: EdgeInsets.symmetric(vertical: 12.0),
                                      child: Divider(height: 1, color: AppColors.divider),
                                    ),

                                    // SECTION 3: Issue Details
                                    _buildSectionBadge(3, 'Issue Details'),
                                    const SizedBox(height: 8),
                                    _buildInfoRow(FeatherIcons.fileText, 'Subject', createdIssue.title, isBold: true),
                                    const SizedBox(height: 6),
                                    _buildInfoRow(FeatherIcons.tag, 'Category', createdIssue.category),
                                    const SizedBox(height: 6),
                                    _buildInfoRow(FeatherIcons.alignLeft, 'Description', createdIssue.description),

                                    const Padding(
                                      padding: EdgeInsets.symmetric(vertical: 12.0),
                                      child: Divider(height: 1, color: AppColors.divider),
                                    ),

                                    // SECTION 4: Media Evidence
                                    _buildSectionBadge(4, 'Photo Evidence'),
                                    const SizedBox(height: 8),
                                    Row(
                                      children: [
                                        Icon(
                                          hasPhoto ? FeatherIcons.image : FeatherIcons.cameraOff,
                                          size: 15,
                                          color: hasPhoto ? const Color(0xFF059669) : AppColors.mutedText,
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          hasPhoto ? 'Photo Attached (Geo-tagged)' : 'No Photo Attached (Optional)',
                                          style: GoogleFonts.inter(
                                            fontSize: 12.5,
                                            fontWeight: hasPhoto ? FontWeight.w600 : FontWeight.w400,
                                            color: hasPhoto ? const Color(0xFF065F46) : AppColors.secondaryText,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 20),
                      ],
                    ),
                  ),
                ),

                // Bottom Action Buttons
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 14.0),
                  decoration: const BoxDecoration(
                    color: AppColors.background,
                    border: Border(
                      top: BorderSide(color: AppColors.border, width: 1.0),
                    ),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 1. File Another Grievance (Primary Button)
                      PrimaryButton(
                        text: LanguageService.instance.currentLanguageCode == 'en'
                            ? 'File Another Grievance'
                            : LanguageService.t('file_another_btn'),
                        onPressed: () {
                          Navigator.pop(context, 'file_another');
                        },
                      ),

                      const SizedBox(height: 10),

                      // 2. Home Button (Secondary Rounded Button)
                      SizedBox(
                        width: double.infinity,
                        height: 54,
                        child: OutlinedButton(
                          onPressed: () {
                            Navigator.pop(context, 'go_home');
                          },
                          style: OutlinedButton.styleFrom(
                            backgroundColor: AppColors.inputBackground,
                            side: const BorderSide(color: AppColors.border, width: 1.2),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(27.0),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 24.0),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(FeatherIcons.home, size: 17, color: AppColors.primaryText),
                              const SizedBox(width: 8),
                              Text(
                                LanguageService.instance.currentLanguageCode == 'en'
                                    ? 'Home'
                                    : LanguageService.t('nav_home'),
                                style: GoogleFonts.inter(
                                  fontSize: 15,
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
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // Section Header Badge
  Widget _buildSectionBadge(int step, String title) {
    return Row(
      children: [
        Container(
          width: 18,
          height: 18,
          decoration: const BoxDecoration(
            color: AppColors.primaryText,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$step',
              style: GoogleFonts.inter(
                fontSize: 10.5,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ),
        ),
        const SizedBox(width: 6),
        Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 12.5,
            fontWeight: FontWeight.w700,
            color: AppColors.primaryText,
          ),
        ),
      ],
    );
  }

  // Key-Value information row
  Widget _buildInfoRow(IconData icon, String label, String value, {bool isBold = false}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 2.0),
          child: Icon(icon, size: 13, color: AppColors.secondaryText),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 76,
          child: Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: AppColors.mutedText,
            ),
          ),
        ),
        const SizedBox(width: 6),
        Expanded(
          child: Text(
            value,
            style: GoogleFonts.inter(
              fontSize: 12.5,
              fontWeight: isBold ? FontWeight.w600 : FontWeight.w500,
              color: AppColors.primaryText,
              height: 1.3,
            ),
          ),
        ),
      ],
    );
  }
}
