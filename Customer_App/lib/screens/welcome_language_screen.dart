import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import '../core/config/api_config.dart';
import '../services/language_service.dart';
import '../theme/app_theme.dart';
import '../widgets/primary_button.dart';
import '../widgets/smooth_page_route.dart';
import 'demo_citizen_auth_screen.dart';
import 'phone_number_screen.dart';

class WelcomeLanguageScreen extends StatefulWidget {
  const WelcomeLanguageScreen({super.key});

  @override
  State<WelcomeLanguageScreen> createState() => _WelcomeLanguageScreenState();
}

class _WelcomeLanguageScreenState extends State<WelcomeLanguageScreen> {
  final _languageService = LanguageService.instance;

  void _onContinue() {
    // DemoConfig.enabled is hardcoded true: language selection always leads
    // to the real demo-citizen login (a genuine `/auth/demo/login` call and
    // JWT, not a phone/OTP challenge), so the dashboard afterwards fetches
    // the real "Demo Citizen" backend user's real records from Postgres.
    Navigator.push(
      context,
      SmoothPageRoute(
        child: DemoConfig.enabled ? const DemoCitizenAuthScreen() : const PhoneNumberScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _languageService,
      builder: (context, _) {
        final selectedLang = _languageService.currentLanguage;

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

                        // Welcome Headings with dynamic multilingual translations
                        Text(
                          _languageService.translate('welcome_title'),
                          style: AppTypography.heading(context).copyWith(
                            fontSize: 24,
                            letterSpacing: -0.5,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          '${selectedLang.greeting} • ${_languageService.translate('welcome_sub')}',
                          style: AppTypography.supporting(context).copyWith(
                            fontSize: 14,
                            color: AppColors.secondaryText,
                          ),
                        ),

                        const SizedBox(height: 24),
                        const Divider(height: 1, thickness: 1, color: AppColors.divider),
                        const SizedBox(height: 20),

                        // Section Title in translated language
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              _languageService.translate('choose_language'),
                              style: AppTypography.heading(context).copyWith(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            Text(
                              selectedLang.nativeName,
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
                          itemCount: LanguageService.supportedLanguages.length,
                          itemBuilder: (context, index) {
                            final lang = LanguageService.supportedLanguages[index];
                            final isSelected = lang.code == _languageService.currentLanguageCode;

                            return InkWell(
                              onTap: () {
                                _languageService.setLanguage(lang.code);
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

                // Bottom CTA Button with translated text
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                  decoration: const BoxDecoration(
                    color: AppColors.background,
                    border: Border(
                      top: BorderSide(color: AppColors.border, width: 1.0),
                    ),
                  ),
                  child: PrimaryButton(
                    text: _languageService.translate('continue_btn'),
                    onPressed: _onContinue,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

