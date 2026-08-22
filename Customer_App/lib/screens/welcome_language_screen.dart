import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import '../theme/app_theme.dart';
import '../widgets/primary_button.dart';
import '../widgets/smooth_page_route.dart';
import 'phone_number_screen.dart';

class LanguageOption {
  final String code;
  final String nativeName;
  final String englishName;
  final String greeting;

  const LanguageOption({
    required this.code,
    required this.nativeName,
    required this.englishName,
    required this.greeting,
  });
}

class WelcomeLanguageScreen extends StatefulWidget {
  const WelcomeLanguageScreen({super.key});

  @override
  State<WelcomeLanguageScreen> createState() => _WelcomeLanguageScreenState();
}

class _WelcomeLanguageScreenState extends State<WelcomeLanguageScreen> {
  static const List<LanguageOption> _languages = [
    LanguageOption(
      code: 'en',
      nativeName: 'English',
      englishName: 'English',
      greeting: 'Welcome',
    ),
    LanguageOption(
      code: 'hi',
      nativeName: 'हिन्दी',
      englishName: 'Hindi',
      greeting: 'स्वागत है',
    ),
    LanguageOption(
      code: 'ta',
      nativeName: 'தமிழ்',
      englishName: 'Tamil',
      greeting: 'வணக்கம்',
    ),
    LanguageOption(
      code: 'te',
      nativeName: 'తెలుగు',
      englishName: 'Telugu',
      greeting: 'స్వాగతం',
    ),
    LanguageOption(
      code: 'kn',
      nativeName: 'ಕನ್ನಡ',
      englishName: 'Kannada',
      greeting: 'ಸ್ವಾಗತ',
    ),
    LanguageOption(
      code: 'ml',
      nativeName: 'മലയാളം',
      englishName: 'Malayalam',
      greeting: 'സ്വാഗതം',
    ),
    LanguageOption(
      code: 'mr',
      nativeName: 'मराठी',
      englishName: 'Marathi',
      greeting: 'स्वागत आहे',
    ),
    LanguageOption(
      code: 'bn',
      nativeName: 'বাংলা',
      englishName: 'Bengali',
      greeting: 'স্বাগতম',
    ),
    LanguageOption(
      code: 'gu',
      nativeName: 'ગુજરાતી',
      englishName: 'Gujarati',
      greeting: 'સ્વાગત છે',
    ),
    LanguageOption(
      code: 'pa',
      nativeName: 'ਪੰਜਾਬੀ',
      englishName: 'Punjabi',
      greeting: 'ਜੀ ਆਇਆਂ ਨੂੰ',
    ),
  ];

  String _selectedLanguageCode = 'en';

  void _onContinue() {
    Navigator.push(
      context,
      SmoothPageRoute(
        child: const PhoneNumberScreen(),
      ),
    );
  }

  LanguageOption get _selectedLanguage => _languages.firstWhere(
        (lang) => lang.code == _selectedLanguageCode,
        orElse: () => _languages.first,
      );

  @override
  Widget build(BuildContext context) {
    final selectedLang = _selectedLanguage;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 8),

                    // Lottie Welcome Animation
                    Center(
                      child: SizedBox(
                        height: 210,
                        child: Lottie.asset(
                          'lib/assets/welcome.json',
                          fit: BoxFit.contain,
                          errorBuilder: (context, error, stackTrace) {
                            return Container(
                              height: 180,
                              width: 180,
                              decoration: BoxDecoration(
                                color: AppColors.inputBackground,
                                shape: BoxShape.circle,
                                border: Border.all(color: AppColors.border),
                              ),
                              child: const Icon(
                                FeatherIcons.globe,
                                size: 64,
                                color: AppColors.primaryText,
                              ),
                            );
                          },
                        ),
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Welcome Headings with dynamic multilingual subtitle
                    Text(
                      'Welcome to Social Serve',
                      style: AppTypography.heading(context).copyWith(
                        fontSize: 24,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '${selectedLang.greeting} • Select your preferred language to continue.',
                      style: AppTypography.supporting(context).copyWith(
                        fontSize: 14,
                        color: AppColors.secondaryText,
                      ),
                    ),

                    const SizedBox(height: 24),
                    const Divider(height: 1, thickness: 1, color: AppColors.divider),
                    const SizedBox(height: 20),

                    // Section Title
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Choose Language',
                          style: AppTypography.heading(context).copyWith(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        Text(
                          'भाषा चुनें',
                          style: AppTypography.supporting(context).copyWith(
                            fontSize: 13,
                            color: AppColors.mutedText,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 14),

                    // 2-Column Grid of Languages in native script
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 12.0,
                        mainAxisSpacing: 12.0,
                        childAspectRatio: 2.2,
                      ),
                      itemCount: _languages.length,
                      itemBuilder: (context, index) {
                        final lang = _languages[index];
                        final isSelected = lang.code == _selectedLanguageCode;

                        return InkWell(
                          onTap: () {
                            setState(() {
                              _selectedLanguageCode = lang.code;
                            });
                          },
                          borderRadius: BorderRadius.circular(14.0),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 200),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 14.0,
                              vertical: 10.0,
                            ),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? AppColors.inputBackground
                                  : AppColors.background,
                              borderRadius: BorderRadius.circular(14.0),
                              border: Border.all(
                                color: isSelected
                                    ? AppColors.primaryText
                                    : AppColors.border,
                                width: isSelected ? 1.8 : 1.0,
                              ),
                            ),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Text(
                                        lang.nativeName,
                                        style: AppTypography.heading(context).copyWith(
                                          fontSize: 15,
                                          fontWeight: isSelected
                                              ? FontWeight.w700
                                              : FontWeight.w600,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        lang.englishName,
                                        style: AppTypography.supporting(context).copyWith(
                                          fontSize: 11,
                                          color: isSelected
                                              ? AppColors.primaryText
                                              : AppColors.secondaryText,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ],
                                  ),
                                ),
                                Icon(
                                  isSelected
                                      ? FeatherIcons.checkCircle
                                      : FeatherIcons.circle,
                                  size: 16,
                                  color: isSelected
                                      ? AppColors.primaryText
                                      : AppColors.mutedText,
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),

                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),

            // Bottom CTA Button
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
              decoration: const BoxDecoration(
                color: AppColors.background,
                border: Border(
                  top: BorderSide(color: AppColors.border, width: 1.0),
                ),
              ),
              child: PrimaryButton(
                text: 'Continue',
                onPressed: _onContinue,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
