import 'package:flutter/material.dart';
import '../models/issue_model.dart';
import '../theme/app_theme.dart';
import '../widgets/custom_dropdown_field.dart';
import '../widgets/custom_input_field.dart';
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
  final TextEditingController _mobileController =
      TextEditingController(text: '9876543210');
  final TextEditingController _emailController =
      TextEditingController(text: 'rahul.tiwari@janseva.gov.in');
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  String _selectedLanguage = 'English';
  String _selectedCategory = 'Auto-Detect via AI (Recommended)';
  bool _hasAttachedMedia = false;

  final List<String> _languages = ['English', 'Tamil', 'Hindi'];
  final List<String> _categories = [
    'Auto-Detect via AI (Recommended)',
    'Roads & Infrastructure',
    'Water & Sanitation',
    'Electrical & Streetlights',
    'Public Health',
    'Other Civic Concerns',
  ];

  void _onSubmit() {
    final titleText = _titleController.text.trim().isEmpty
        ? 'Civic Grievance Report'
        : _titleController.text.trim();
    final descriptionText = _descriptionController.text.trim().isEmpty
        ? 'Reported issue submitted for review and resolution.'
        : _descriptionController.text.trim();

    final newIssue = IssueItem(
      id: 'ISS-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
      title: titleText,
      category: _selectedCategory.contains('AI')
          ? 'Roads & Infrastructure'
          : _selectedCategory,
      description: descriptionText,
      location: 'Sector 12, Main Ward',
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
    _mobileController.dispose();
    _emailController.dispose();
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.primaryText),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'File an Issue',
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
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Section matching reference image
              Text(
                'Lodge a Citizen Grievance',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'Submit public municipal issues for automated classification, priority triage, and departmental redressal.',
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 14,
                  height: 1.4,
                ),
              ),

              const SizedBox(height: 28),
              const Divider(height: 1, thickness: 1, color: AppColors.divider),
              const SizedBox(height: 24),

              // SECTION 1: Personal Information
              Text(
                'Personal Information',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Citizen contact details required for SMS status alerts and field engineer verification.',
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 13,
                  color: AppColors.secondaryText,
                ),
              ),
              const SizedBox(height: 20),

              CustomDropdownField(
                label: 'Preferred Language',
                value: _selectedLanguage,
                items: _languages,
                onChanged: (val) {
                  if (val != null) setState(() => _selectedLanguage = val);
                },
              ),
              const SizedBox(height: 16),

              CustomInputField(
                label: 'Full Name',
                placeholder: 'Enter full name',
                controller: _fullNameController,
                isRequired: true,
              ),
              const SizedBox(height: 16),

              CustomInputField(
                label: 'Mobile Number (For SMS Updates)',
                placeholder: 'Enter mobile number',
                controller: _mobileController,
                isRequired: true,
                keyboardType: TextInputType.phone,
              ),
              const SizedBox(height: 16),

              CustomInputField(
                label: 'Email Address (Optional)',
                placeholder: 'Enter email address',
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
              ),

              const SizedBox(height: 28),
              const Divider(height: 1, thickness: 1, color: AppColors.divider),
              const SizedBox(height: 24),

              // SECTION 2: Grievance Details
              Text(
                'Grievance Details',
                style: AppTypography.heading(context).copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Describe the civic issue in detail to facilitate swift categorization and departmental triage.',
                style: AppTypography.supporting(context).copyWith(
                  fontSize: 13,
                  color: AppColors.secondaryText,
                ),
              ),
              const SizedBox(height: 20),

              CustomDropdownField(
                label: 'Department Category',
                value: _selectedCategory,
                items: _categories,
                onChanged: (val) {
                  if (val != null) setState(() => _selectedCategory = val);
                },
              ),
              const SizedBox(height: 16),

              CustomInputField(
                label: 'Subject / Short Title',
                placeholder: 'e.g. Broken pipe flooding Sector 12',
                controller: _titleController,
                isRequired: true,
              ),
              const SizedBox(height: 16),

              CustomInputField(
                label: 'Detailed Problem Description',
                placeholder:
                    'Explain the issue in detail (e.g. Exact location, safety risks, duration of issue)...',
                controller: _descriptionController,
                isRequired: true,
                maxLines: 4,
              ),
              const SizedBox(height: 20),

              MediaUploadCard(
                onMediaSelected: (hasPhoto) {
                  setState(() => _hasAttachedMedia = hasPhoto);
                },
              ),

              const SizedBox(height: 32),

              PrimaryButton(
                text: 'Submit Issue',
                onPressed: _onSubmit,
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
