import 'package:flutter/material.dart';
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

  void _togglePhoto() {
    setState(() {
      _hasPhoto = !_hasPhoto;
      widget.onMediaSelected(_hasPhoto);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Attach Photo of Issue (Optional)',
          style: AppTypography.supporting(context).copyWith(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.primaryText,
          ),
        ),
        const SizedBox(height: 8),
        GestureDetector(
          onTap: _togglePhoto,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 24.0, horizontal: 16.0),
            decoration: BoxDecoration(
              color: _hasPhoto ? AppColors.inputBackground : AppColors.background,
              borderRadius: BorderRadius.circular(14.0),
              border: Border.all(
                color: _hasPhoto ? AppColors.primaryText : AppColors.border,
                width: _hasPhoto ? 1.5 : 1.0,
              ),
            ),
            child: _hasPhoto
                ? Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: const BoxDecoration(
                          color: AppColors.primaryButton,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.check_rounded,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        '1 Photo Attached (mock_evidence.jpg)',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primaryText,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Tap to replace or remove photo',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 12,
                          color: AppColors.mutedText,
                        ),
                      ),
                    ],
                  )
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.upload_rounded,
                        size: 28,
                        color: AppColors.primaryText,
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Click to upload or drag photo',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primaryText,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'PNG, JPG or WEBP up to 10MB',
                        style: AppTypography.supporting(context).copyWith(
                          fontSize: 12,
                          color: AppColors.mutedText,
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ],
    );
  }
}
