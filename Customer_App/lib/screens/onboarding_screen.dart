import 'package:feather_icons/feather_icons.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import '../theme/app_theme.dart';
import '../widgets/auth_progress_indicator.dart';
import '../widgets/primary_button.dart';
import '../widgets/smooth_page_route.dart';
import 'main_dashboard_screen.dart';

class OnboardingItem {
  final String animationPath;
  final String title;
  final String description;

  const OnboardingItem({
    required this.animationPath,
    required this.title,
    required this.description,
  });
}

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<OnboardingItem> _items = const [
    OnboardingItem(
      animationPath: 'assets/animations/connect.json',
      title: 'Connect & Collaborate',
      description:
          'Engage with verified community leaders and local social initiatives in real time.',
    ),
    OnboardingItem(
      animationPath: 'assets/animations/reporting.json',
      title: 'Report Local Issues',
      description:
          'Submit issues and requests with photos and live location to drive immediate action.',
    ),
    OnboardingItem(
      animationPath: 'assets/animations/progress.json',
      title: 'Track Real-Time Progress',
      description:
          'Follow the journey of your requests from initial review to complete resolution.',
    ),
    OnboardingItem(
      animationPath: 'assets/animations/file_loading.json',
      title: 'Verified Community Impact',
      description:
          'Access transparent documentation and celebrate neighborhood milestones together.',
    ),
  ];

  void _onNext() {
    if (_currentPage < _items.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 380),
        curve: Curves.easeInOutCubic,
      );
    } else {
      _onFinish();
    }
  }

  void _onSkip() {
    _onFinish();
  }

  void _onFinish() {
    Navigator.pushAndRemoveUntil(
      context,
      SmoothPageRoute(
        child: const MainDashboardScreen(),
      ),
      (route) => false,
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isLastPage = _currentPage == _items.length - 1;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            children: [
              // Top Action Row (Back / Skip)
              Padding(
                padding: const EdgeInsets.only(top: 8.0, bottom: 4.0),
                child: SizedBox(
                  height: 40,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (_currentPage > 0)
                        GestureDetector(
                          behavior: HitTestBehavior.opaque,
                          onTap: () {
                            _pageController.previousPage(
                              duration: const Duration(milliseconds: 350),
                              curve: Curves.easeInOutCubic,
                            );
                          },
                          child: const Icon(
                            FeatherIcons.arrowLeft,
                            size: 20,
                            color: AppColors.primaryText,
                          ),
                        )
                      else
                        GestureDetector(
                          behavior: HitTestBehavior.opaque,
                          onTap: () => Navigator.pop(context),
                          child: const Icon(
                            FeatherIcons.arrowLeft,
                            size: 20,
                            color: AppColors.primaryText,
                          ),
                        ),
                      if (!isLastPage)
                        GestureDetector(
                          behavior: HitTestBehavior.opaque,
                          onTap: _onSkip,
                          child: Text(
                            'Skip',
                            style: AppTypography.supporting(context).copyWith(
                              fontWeight: FontWeight.w500,
                              color: AppColors.mutedText,
                            ),
                          ),
                        )
                      else
                        const SizedBox(width: 32),
                    ],
                  ),
                ),
              ),

              // Connected Subtle Progress Bar (Steps 3 to 6 out of 6)
              AuthProgressIndicator(
                currentStep: 3 + _currentPage,
                totalSteps: 6,
              ),

              // Page View with Animations and Text
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  physics: const BouncingScrollPhysics(),
                  onPageChanged: (index) {
                    setState(() {
                      _currentPage = index;
                    });
                  },
                  itemCount: _items.length,
                  itemBuilder: (context, index) {
                    final item = _items[index];
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 8.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Spacer(flex: 1),
                          // Increased Lottie Animation Size (280px)
                          SizedBox(
                            height: 280,
                            child: Lottie.asset(
                              item.animationPath,
                              fit: BoxFit.contain,
                              errorBuilder: (context, error, stackTrace) {
                                return const SizedBox(height: 280);
                              },
                            ),
                          ),
                          const SizedBox(height: 24),
                          // Title
                          Text(
                            item.title,
                            textAlign: TextAlign.center,
                            style: AppTypography.heading(context).copyWith(
                              fontSize: 26,
                            ),
                          ),
                          const SizedBox(height: 12),
                          // Description
                          Text(
                            item.description,
                            textAlign: TextAlign.center,
                            style: AppTypography.supporting(context),
                          ),
                          const Spacer(flex: 2),
                        ],
                      ),
                    );
                  },
                ),
              ),

              // Monochromatic Page Indicator Dots
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(_items.length, (index) {
                  final isSelected = index == _currentPage;
                  return AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    margin: const EdgeInsets.symmetric(horizontal: 4.0),
                    height: 6.0,
                    width: isSelected ? 24.0 : 6.0,
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppColors.primaryText
                          : AppColors.border,
                      borderRadius: BorderRadius.circular(3.0),
                    ),
                  );
                }),
              ),

              const SizedBox(height: 28),

              // Bottom CTA Pill Button
              Padding(
                padding: const EdgeInsets.only(bottom: 20.0),
                child: PrimaryButton(
                  text: isLastPage ? 'Get Started' : 'Continue',
                  onPressed: _onNext,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
