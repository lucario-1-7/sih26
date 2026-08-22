import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

class MediaUploadCard extends StatefulWidget {
  final ValueChanged<bool> onMediaSelected;

  const MediaUploadCard({
    super.key,
    required this.onMediaSelected,
  });

  @override
  State<MediaUploadCard> createState() => _MediaUploadCardState();
}

class _MediaUploadCardState extends State<MediaUploadCard> {
  bool _hasPhoto = false;
  String _sourceType = 'Camera'; // 'Camera' or 'Gallery'

  void _showMediaPickerBottomSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.background,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20.0)),
      ),
      builder: (ctx) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 36,
                    height: 4,
                    decoration: BoxDecoration(
                      color: AppColors.border,
                      borderRadius: BorderRadius.circular(2.0),
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  'Attach Photo Evidence',
                  style: GoogleFonts.inter(
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primaryText,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Select how you want to add photo proof for this grievance.',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: AppColors.secondaryText,
                    fontWeight: FontWeight.w400,
                  ),
                ),
                const SizedBox(height: 20),
                _buildPickerOption(
                  icon: FeatherIcons.camera,
                  title: 'Take a Photo',
                  subtitle: 'Use your phone camera to capture issue',
                  onTap: () {
                    Navigator.pop(ctx);
                    _setPhoto(true, 'Camera');
                  },
                ),
                const SizedBox(height: 10),
                _buildPickerOption(
                  icon: FeatherIcons.image,
                  title: 'Upload from Gallery',
                  subtitle: 'Select an existing photo from device',
                  onTap: () {
                    Navigator.pop(ctx);
                    _setPhoto(true, 'Gallery');
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPickerOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12.0),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
        decoration: BoxDecoration(
          color: AppColors.inputBackground,
          borderRadius: BorderRadius.circular(12.0),
          border: Border.all(color: AppColors.border, width: 1.0),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.background,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.border, width: 1.0),
              ),
              child: Center(
                child: Icon(icon, size: 18, color: AppColors.primaryText),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.inter(
                      fontSize: 14.5,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primaryText,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      color: AppColors.secondaryText,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              FeatherIcons.chevronRight,
              size: 18,
              color: AppColors.mutedText,
            ),
          ],
        ),
      ),
    );
  }

  void _setPhoto(bool hasPhoto, [String source = 'Camera']) {
    setState(() {
      _hasPhoto = hasPhoto;
      _sourceType = source;
    });
    widget.onMediaSelected(hasPhoto);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label Header with Optional Chip
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Upload or Click Photo',
              style: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppColors.primaryText,
                letterSpacing: -0.2,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
              decoration: BoxDecoration(
                color: AppColors.inputBackground,
                borderRadius: BorderRadius.circular(6.0),
                border: Border.all(color: AppColors.border, width: 0.8),
              ),
              child: Text(
                'Optional',
                style: GoogleFonts.inter(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: AppColors.secondaryText,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),

        if (_hasPhoto)
          _buildAttachedState()
        else
          _buildEmptyUploadCard(),
      ],
    );
  }

  Widget _buildEmptyUploadCard() {
    return InkWell(
      onTap: _showMediaPickerBottomSheet,
      borderRadius: BorderRadius.circular(14.0),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 20.0, horizontal: 16.0),
        decoration: BoxDecoration(
          color: AppColors.background,
          borderRadius: BorderRadius.circular(14.0),
          border: Border.all(
            color: AppColors.border,
            width: 1.0,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Centered icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.inputBackground,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.border, width: 1.0),
              ),
              child: const Center(
                child: Icon(
                  FeatherIcons.camera,
                  size: 20,
                  color: AppColors.primaryText,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Upload or Click Photo',
              style: GoogleFonts.inter(
                fontSize: 14.5,
                fontWeight: FontWeight.w600,
                color: AppColors.primaryText,
                letterSpacing: -0.2,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Take a picture with camera or select from device',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 12.5,
                color: AppColors.secondaryText,
                fontWeight: FontWeight.w400,
              ),
            ),
            const SizedBox(height: 14),

            // Two Quick Action Buttons inside the card
            Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: () => _setPhoto(true, 'Camera'),
                    borderRadius: BorderRadius.circular(10.0),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 9.0),
                      decoration: BoxDecoration(
                        color: AppColors.inputBackground,
                        borderRadius: BorderRadius.circular(10.0),
                        border: Border.all(color: AppColors.border, width: 1.0),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            FeatherIcons.camera,
                            size: 14,
                            color: AppColors.primaryText,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'Take Photo',
                            style: GoogleFonts.inter(
                              fontSize: 12.5,
                              fontWeight: FontWeight.w600,
                              color: AppColors.primaryText,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: InkWell(
                    onTap: () => _setPhoto(true, 'Gallery'),
                    borderRadius: BorderRadius.circular(10.0),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 9.0),
                      decoration: BoxDecoration(
                        color: AppColors.inputBackground,
                        borderRadius: BorderRadius.circular(10.0),
                        border: Border.all(color: AppColors.border, width: 1.0),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            FeatherIcons.uploadCloud,
                            size: 14,
                            color: AppColors.primaryText,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'From Gallery',
                            style: GoogleFonts.inter(
                              fontSize: 12.5,
                              fontWeight: FontWeight.w600,
                              color: AppColors.primaryText,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Supports JPG, PNG, WEBP up to 10 MB',
              style: GoogleFonts.inter(
                fontSize: 11,
                color: AppColors.mutedText,
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAttachedState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: AppColors.inputBackground,
        borderRadius: BorderRadius.circular(14.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Row(
        children: [
          // Photo Thumbnail Box with checkmark
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: AppColors.background,
                  borderRadius: BorderRadius.circular(10.0),
                  border: Border.all(color: AppColors.border, width: 1.0),
                ),
                child: Center(
                  child: Icon(
                    _sourceType == 'Camera'
                        ? FeatherIcons.camera
                        : FeatherIcons.image,
                    size: 24,
                    color: AppColors.primaryText,
                  ),
                ),
              ),
              Positioned(
                right: -3,
                bottom: -3,
                child: Container(
                  width: 18,
                  height: 18,
                  decoration: const BoxDecoration(
                    color: Color(0xFF10B981),
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: Icon(
                      FeatherIcons.check,
                      size: 11,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: 14),

          // File metadata
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _sourceType == 'Camera'
                      ? 'camera_capture_01.jpg'
                      : 'gallery_evidence.jpg',
                  style: GoogleFonts.inter(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryText,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 3),
                Text(
                  '2.4 MB • Ready to upload',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: AppColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),

          // Action Buttons: Retake / Remove
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                icon: const Icon(FeatherIcons.refreshCw, size: 16),
                color: AppColors.primaryText,
                tooltip: 'Retake Photo',
                onPressed: _showMediaPickerBottomSheet,
              ),
              IconButton(
                icon: const Icon(FeatherIcons.trash2, size: 16),
                color: const Color(0xFFEF4444),
                tooltip: 'Remove Photo',
                onPressed: () => _setPhoto(false),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
