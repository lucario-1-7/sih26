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

  String _selectedCategory = 'Roads & Infrastructure';
  bool _hasAttachedMedia = false;

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

    final newIssue = IssueItem(
      id: 'ISS-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
      title: titleText,
      category: _selectedCategory,
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
              _buildSectionHeader(2, 'Grievance Location'),
              const SizedBox(height: 12),
              _buildInputField(
                controller: _addressController,
                placeholder: 'Address (House no., Street name)',
                icon: FeatherIcons.mapPin,
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

              // SECTION 3: Issue Category & Details
              _buildSectionHeader(3, 'Issue Category & Details'),
              const SizedBox(height: 12),

              // 4 Category Tiles matching the reference selector style
              _buildCategoryTiles(),

              const SizedBox(height: 14),

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
                maxLines: 3,
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
          child: Column(
            children: [
              Text(
                'File Grievance',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                'Submit municipal issue securely',
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 12,
                  color: AppColors.secondaryText,
                ),
              ),
            ],
          ),
        ),
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(10.0),
            border: Border.all(color: const Color(0xFFDCFCE7), width: 1.0),
          ),
          child: const Center(
            child: Icon(
              FeatherIcons.shield,
              size: 16,
              color: Color(0xFF16A34A),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSectionHeader(int step, String title) {
    return Row(
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: const BoxDecoration(
            color: Color(0xFF16A34A),
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
        Text(
          title,
          style: AppTypography.heading(context).copyWith(
            fontSize: 15,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }

  Widget _buildInputField({
    required TextEditingController controller,
    required String placeholder,
    required IconData icon,
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
        ],
      ),
    );
  }

  Widget _buildCategoryTiles() {
    final categories = [
      {'id': 'Roads & Infrastructure', 'label': 'Roads', 'icon': FeatherIcons.mapPin},
      {'id': 'Water & Utilities', 'label': 'Water', 'icon': FeatherIcons.droplet},
      {'id': 'Electrical & Lighting', 'label': 'Electrical', 'icon': FeatherIcons.zap},
      {'id': 'Sanitation & Health', 'label': 'Sanitation', 'icon': FeatherIcons.trash},
    ];

    return Row(
      children: categories.map((cat) {
        final id = cat['id'] as String;
        final label = cat['label'] as String;
        final icon = cat['icon'] as IconData;
        final isSelected = _selectedCategory == id;

        return Expanded(
          child: GestureDetector(
            onTap: () {
              setState(() {
                _selectedCategory = id;
              });
            },
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 3.0),
              padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 4.0),
              decoration: BoxDecoration(
                color: isSelected ? const Color(0xFFF0FDF4) : AppColors.background,
                borderRadius: BorderRadius.circular(12.0),
                border: Border.all(
                  color: isSelected ? const Color(0xFF16A34A) : AppColors.border,
                  width: isSelected ? 1.5 : 1.0,
                ),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    icon,
                    size: 20,
                    color: isSelected ? const Color(0xFF16A34A) : AppColors.primaryText,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: AppTypography.supporting(context).copyWith(
                      fontSize: 11,
                      fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                      color: isSelected ? const Color(0xFF16A34A) : AppColors.primaryText,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
