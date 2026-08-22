import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';
import '../widgets/media_upload_card.dart';
import '../widgets/primary_button.dart';
import 'issue_success_screen.dart';

class IssueFilingScreen extends StatefulWidget {
  const IssueFilingScreen({super.key});

  @override
  State<IssueFilingScreen> createState() => _IssueFilingScreenState();
}

class _IssueFilingScreenState extends State<IssueFilingScreen> {
  // Form Controllers
  final TextEditingController _fullNameController =
      TextEditingController(text: 'Rahul Tiwari');
  final TextEditingController _emailController =
      TextEditingController(text: 'rahul.tiwari@janseva.gov.in');
  final TextEditingController _mobileController =
      TextEditingController(text: '9876543210');
  final TextEditingController _addressController =
      TextEditingController(text: 'House 42, Outer Ring Road');
  final TextEditingController _cityWardController =
      TextEditingController(text: 'Sector 12, Ward 4');
  final TextEditingController _pincodeController =
      TextEditingController(text: '600028');
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  bool _hasAttachedMedia = false;
  bool _isLocationShared = false;

  Future<void> _requestLocationPermission() async {
    final bool? granted = await showDialog<bool>(
      context: context,
      builder: (BuildContext ctx) {
        return Dialog(
          backgroundColor: AppColors.background,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.0),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppColors.inputBackground,
                    shape: BoxShape.circle,
                    border: Border.all(color: AppColors.border),
                  ),
                  child: const Icon(
                    FeatherIcons.mapPin,
                    size: 22,
                    color: AppColors.primaryText,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Allow JanSeva to access this device\'s location?',
                  textAlign: TextAlign.center,
                  style: AppTypography.heading(context).copyWith(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Precise GPS location is used to pinpoint civic issues and dispatch departmental response teams directly to the site.',
                  textAlign: TextAlign.center,
                  style: AppTypography.supporting(context).copyWith(
                    fontSize: 12.5,
                    color: AppColors.secondaryText,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primaryButton,
                      foregroundColor: AppColors.buttonText,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12.0),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 12.0),
                      elevation: 0,
                    ),
                    onPressed: () => Navigator.pop(ctx, true),
                    child: const Text(
                      'While Using the App',
                      style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13.5),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: TextButton(
                    style: TextButton.styleFrom(
                      foregroundColor: AppColors.secondaryText,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12.0),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 10.0),
                    ),
                    onPressed: () => Navigator.pop(ctx, false),
                    child: const Text(
                      'Don\'t Allow',
                      style: TextStyle(fontWeight: FontWeight.w500, fontSize: 13.5),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );

    if (granted == true) {
      setState(() {
        _isLocationShared = true;
        _addressController.text = 'Near Anna Nagar Junction, 2nd Avenue';
        _cityWardController.text = 'Ward 4, Zone 2';
        _pincodeController.text = '600040';
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Location permission granted! Address details auto-filled from GPS.'),
            duration: Duration(seconds: 3),
          ),
        );
      }
    } else if (granted == false) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Location permission denied. Please enter address manually.'),
            duration: Duration(seconds: 3),
          ),
        );
      }
    }
  }

  void _onSubmit() {
    final titleText = _titleController.text.trim().isEmpty
        ? 'Civic Grievance Report'
        : _titleController.text.trim();
    final descriptionText = _descriptionController.text.trim().isEmpty
        ? 'Reported issue submitted for review and resolution.'
        : _descriptionController.text.trim();
    final locationText = _addressController.text.trim().isEmpty
        ? 'Sector 12, Main Ward'
        : '${_addressController.text.trim()}, ${_cityWardController.text.trim()}';

    // Model auto-classification based on reported content
    String detectedCategory = 'Roads & Infrastructure';
    final lower = '$titleText $descriptionText'.toLowerCase();
    if (lower.contains('water') || lower.contains('pipe') || lower.contains('drain') || lower.contains('leak')) {
      detectedCategory = 'Water & Utilities';
    } else if (lower.contains('light') || lower.contains('electric') || lower.contains('wire') || lower.contains('power')) {
      detectedCategory = 'Electrical & Lighting';
    } else if (lower.contains('waste') || lower.contains('garbage') || lower.contains('trash') || lower.contains('sanitation') || lower.contains('clean')) {
      detectedCategory = 'Sanitation & Health';
    } else if (lower.contains('road') || lower.contains('pothole') || lower.contains('traffic') || lower.contains('street') || lower.contains('bridge')) {
      detectedCategory = 'Roads & Infrastructure';
    } else {
      detectedCategory = 'Civic Infrastructure';
    }

    final newIssue = IssueItem(
      id: 'ISS-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
      title: titleText,
      category: detectedCategory,
      description: descriptionText,
      location: locationText,
      dateFiled: 'Today',
      status: IssueStatus.underReview,
      imagePath: _hasAttachedMedia ? 'mock_evidence.jpg' : null,
    );

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => IssueSuccessScreen(createdIssue: newIssue),
      ),
    );
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _mobileController.dispose();
    _addressController.dispose();
    _cityWardController.dispose();
    _pincodeController.dispose();
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Heading Bar matching reference image
              _buildTopBar(),

              const SizedBox(height: 18),

              // SECTION 1: Contact Information
              _buildSectionHeader(1, 'Contact Information'),
              const SizedBox(height: 12),
              _buildInputField(
                controller: _fullNameController,
                placeholder: 'Full Name',
                icon: FeatherIcons.user,
              ),
              const SizedBox(height: 10),
              _buildInputField(
                controller: _emailController,
                placeholder: 'Email Address',
                icon: FeatherIcons.mail,
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 10),
              _buildInputField(
                controller: _mobileController,
                placeholder: 'Phone Number',
                icon: FeatherIcons.phone,
                keyboardType: TextInputType.phone,
              ),

              const SizedBox(height: 24),

              // SECTION 2: Grievance Location
              _buildSectionHeader(
                2,
                'Grievance Location',
                trailing: GestureDetector(
                  onTap: _requestLocationPermission,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 5.0),
                    decoration: BoxDecoration(
                      color: _isLocationShared
                          ? AppColors.inputBackground
                          : AppColors.background,
                      borderRadius: BorderRadius.circular(20.0),
                      border: Border.all(
                        color: _isLocationShared
                            ? AppColors.primaryText
                            : AppColors.border,
                        width: 1.0,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _isLocationShared ? FeatherIcons.check : FeatherIcons.mapPin,
                          size: 13,
                          color: AppColors.primaryText,
                        ),
                        const SizedBox(width: 5),
                        Text(
                          _isLocationShared ? 'GPS Linked' : 'Use GPS',
                          style: AppTypography.supporting(context).copyWith(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w600,
                            color: AppColors.primaryText,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),

              _buildInputField(
                controller: _addressController,
                placeholder: 'Address (House no., Street name)',
                icon: FeatherIcons.mapPin,
                suffixIcon: FeatherIcons.crosshair,
                onSuffixTap: _requestLocationPermission,
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _buildInputField(
                      controller: _cityWardController,
                      placeholder: 'City / Ward',
                      icon: FeatherIcons.compass,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _buildInputField(
                      controller: _pincodeController,
                      placeholder: 'ZIP / Pincode',
                      icon: FeatherIcons.hash,
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // SECTION 3: Issue Details
              _buildSectionHeader(3, 'Issue Details'),
              const SizedBox(height: 12),

              _buildInputField(
                controller: _titleController,
                placeholder: 'Subject / Short Title (e.g. Broken water pipe)',
                icon: FeatherIcons.fileText,
              ),
              const SizedBox(height: 10),
              _buildInputField(
                controller: _descriptionController,
                placeholder: 'Detailed problem description...',
                icon: FeatherIcons.alignLeft,
                maxLines: 4,
              ),

              const SizedBox(height: 16),

              MediaUploadCard(
                onMediaSelected: (hasPhoto) {
                  setState(() => _hasAttachedMedia = hasPhoto);
                },
              ),

              const SizedBox(height: 24),

              PrimaryButton(
                text: 'Submit Grievance',
                onPressed: _onSubmit,
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTopBar() {
    return Row(
      children: [
        GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () => Navigator.pop(context),
          child: Container(
            width: 36,
            height: 36,
            alignment: Alignment.centerLeft,
            child: const Icon(
              FeatherIcons.arrowLeft,
              size: 20,
              color: AppColors.primaryText,
            ),
          ),
        ),
        Expanded(
          child: Center(
            child: Text(
              'File Grievance',
              style: AppTypography.heading(context).copyWith(
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
        const SizedBox(width: 36), // Balances the leading back button for true centering
      ],
    );
  }

  Widget _buildSectionHeader(int step, String title, {Widget? trailing}) {
    return Row(
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: const BoxDecoration(
            color: AppColors.primaryButton,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$step',
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            title,
            style: AppTypography.heading(context).copyWith(
              fontSize: 15,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        ?trailing,
      ],
    );
  }

  Widget _buildInputField({
    required TextEditingController controller,
    required String placeholder,
    required IconData icon,
    IconData? suffixIcon,
    VoidCallback? onSuffixTap,
    int maxLines = 1,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 2.0),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Row(
        crossAxisAlignment:
            maxLines > 1 ? CrossAxisAlignment.start : CrossAxisAlignment.center,
        children: [
          Padding(
            padding: EdgeInsets.only(top: maxLines > 1 ? 12.0 : 0.0),
            child: Icon(
              icon,
              size: 18,
              color: AppColors.secondaryText,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: controller,
              maxLines: maxLines,
              keyboardType: keyboardType,
              style: AppTypography.inputText(context).copyWith(fontSize: 14),
              decoration: InputDecoration(
                hintText: placeholder,
                hintStyle: AppTypography.placeholder(context).copyWith(
                  fontSize: 14,
                  color: AppColors.mutedText,
                ),
                border: InputBorder.none,
                isDense: true,
                contentPadding: const EdgeInsets.symmetric(vertical: 13.0),
              ),
            ),
          ),
          if (suffixIcon != null)
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: onSuffixTap,
              child: Padding(
                padding: const EdgeInsets.only(left: 6.0),
                child: Icon(
                  suffixIcon,
                  size: 18,
                  color: AppColors.primaryText,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
