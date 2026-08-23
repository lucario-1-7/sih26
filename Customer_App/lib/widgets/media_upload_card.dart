import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
import '../services/language_service.dart';
import '../theme/app_theme.dart';

class MediaUploadCard extends StatefulWidget {
  final ValueChanged<bool> onMediaSelected;
  final bool showHeading;

  const MediaUploadCard({
    super.key,
    required this.onMediaSelected,
    this.showHeading = false,
  });

  @override
  State<MediaUploadCard> createState() => _MediaUploadCardState();
}

class _MediaUploadCardState extends State<MediaUploadCard> {
  bool _hasPhoto = false;
  bool _isLoading = false;
  String _sourceType = 'Gallery'; // 'Camera' or 'Gallery'

  void _triggerPhotoUpload(String source) {
    setState(() {
      _isLoading = true;
      _sourceType = source;
    });

    // Simulate image loading & processing with animation
    Future.delayed(const Duration(milliseconds: 950), () {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _hasPhoto = true;
        });
        widget.onMediaSelected(true);
      }
    });
  }

  void _removePhoto() {
    setState(() {
      _hasPhoto = false;
      _isLoading = false;
    });
    widget.onMediaSelected(false);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: LanguageService.instance,
      builder: (context, _) {
        if (widget.showHeading) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                LanguageService.t('step4_title'),
                style: GoogleFonts.inter(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryText,
                ),
              ),
              const SizedBox(height: 10),
              _buildBody(),
            ],
          );
        }

        return _buildBody();
      },
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return _buildLoadingState();
    }
    if (_hasPhoto) {
      return _buildAttachedState();
    }
    return _buildUploadSection();
  }

  // 1. Loading Animation State
  Widget _buildLoadingState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24.0, horizontal: 16.0),
      decoration: BoxDecoration(
        color: AppColors.inputBackground,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            height: 90,
            child: Lottie.asset(
              'lib/assets/file_loading.json',
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) {
                return Lottie.asset(
                  'assets/animations/file_loading.json',
                  fit: BoxFit.contain,
                  errorBuilder: (context, err2, stack2) {
                    return const CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(AppColors.primaryText),
                      strokeWidth: 2.5,
                    );
                  },
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          Text(
            _sourceType == 'Camera'
                ? 'Processing camera photo...'
                : 'Loading and verifying image...',
            style: GoogleFonts.inter(
              fontSize: 13.5,
              fontWeight: FontWeight.w600,
              color: AppColors.primaryText,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Optimizing photo for civic verification',
            style: GoogleFonts.inter(
              fontSize: 12,
              color: AppColors.secondaryText,
            ),
          ),
        ],
      ),
    );
  }

  // 2. Default Upload Options matching reference
  Widget _buildUploadSection() {
    return Column(
      children: [
        // Top Box: "Select file"
        InkWell(
          onTap: () => _triggerPhotoUpload('Gallery'),
          borderRadius: BorderRadius.circular(16.0),
          child: Container(
            width: double.infinity,
            height: 140,
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(16.0),
              border: Border.all(
                color: AppColors.border,
                width: 1.2,
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const Icon(
                  FeatherIcons.image,
                  size: 26,
                  color: AppColors.secondaryText,
                ),
                const SizedBox(height: 10),
                Text(
                  LanguageService.t('select_file'),
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: AppColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 14),

        // Divider with "or"
        Row(
          children: [
            const Expanded(
              child: Divider(
                color: AppColors.border,
                thickness: 1.0,
                height: 1.0,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14.0),
              child: Text(
                LanguageService.t('or_text'),
                style: GoogleFonts.inter(
                  fontSize: 12.5,
                  fontWeight: FontWeight.w400,
                  color: AppColors.mutedText,
                ),
              ),
            ),
            const Expanded(
              child: Divider(
                color: AppColors.border,
                thickness: 1.0,
                height: 1.0,
              ),
            ),
          ],
        ),

        const SizedBox(height: 14),

        // Pill Button: "Open Camera & Take Photo"
        InkWell(
          onTap: () => _triggerPhotoUpload('Camera'),
          borderRadius: BorderRadius.circular(30.0),
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 13.0),
            decoration: BoxDecoration(
              color: AppColors.inputBackground,
              borderRadius: BorderRadius.circular(30.0),
              border: Border.all(
                color: AppColors.border,
                width: 1.0,
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  FeatherIcons.camera,
                  size: 16,
                  color: AppColors.primaryText,
                ),
                const SizedBox(width: 8),
                Text(
                  LanguageService.t('open_camera'),
                  style: GoogleFonts.inter(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryText,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // 3. Viewable Photo Confirmation State
  Widget _buildAttachedState() {
    final fileName = _sourceType == 'Camera'
        ? 'CAMERA_EVIDENCE_2026.JPG'
        : 'GALLERY_UPLOAD_2026.JPG';

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Viewable Image Preview Container
          Image.network(
            'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&q=80',
            height: 180,
            width: double.infinity,
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) {
              return Container(
                height: 180,
                width: double.infinity,
                color: AppColors.inputBackground,
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        FeatherIcons.image,
                        size: 40,
                        color: AppColors.primaryText,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        fileName,
                        style: GoogleFonts.inter(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primaryText,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),

          // File Details & Actions Underneath
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        fileName,
                        style: GoogleFonts.inter(
                          fontSize: 13.5,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primaryText,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '2.4 MB • Ready for submission',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: AppColors.secondaryText,
                        ),
                      ),
                    ],
                  ),
                ),

                // Action buttons: Replace & Remove
                IconButton(
                  onPressed: () => _triggerPhotoUpload(_sourceType == 'Camera' ? 'Gallery' : 'Camera'),
                  icon: const Icon(FeatherIcons.refreshCw, size: 15),
                  color: AppColors.primaryText,
                  tooltip: 'Replace photo',
                  style: IconButton.styleFrom(
                    backgroundColor: AppColors.inputBackground,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: const BorderSide(color: AppColors.border),
                    ),
                    padding: const EdgeInsets.all(8),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _removePhoto,
                  icon: const Icon(FeatherIcons.trash2, size: 15),
                  color: AppColors.primaryText,
                  tooltip: 'Remove photo',
                  style: IconButton.styleFrom(
                    backgroundColor: AppColors.inputBackground,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: const BorderSide(color: AppColors.border),
                    ),
                    padding: const EdgeInsets.all(8),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

