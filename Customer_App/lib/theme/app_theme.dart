import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/theme_service.dart';

class AppColors {
  // Light Palette
  static const Color lightBackground = Color(0xFFFFFFFF);
  static const Color lightCard = Color(0xFFFFFFFF);
  static const Color lightPrimaryText = Color(0xFF111111);
  static const Color lightSecondaryText = Color(0xFF555555);
  static const Color lightMutedText = Color(0xFF8E8E93);
  static const Color lightInputBackground = Color(0xFFF6F6F8);
  static const Color lightBorder = Color(0xFFE5E5EA);
  static const Color lightPrimaryButton = Color(0xFF111111);
  static const Color lightButtonText = Color(0xFFFFFFFF);
  static const Color lightDisabledButton = Color(0xFFE5E5EA);
  static const Color lightDisabledText = Color(0xFF8E8E93);
  static const Color lightDivider = Color(0xFFE5E5EA);

  // Dark Palette
  static const Color darkBackground = Color(0xFF0E1015);
  static const Color darkCard = Color(0xFF171922);
  static const Color darkPrimaryText = Color(0xFFF8F9FA);
  static const Color darkSecondaryText = Color(0xFFA1A1AA);
  static const Color darkMutedText = Color(0xFF71717A);
  static const Color darkInputBackground = Color(0xFF1E212B);
  static const Color darkBorder = Color(0xFF2C303E);
  static const Color darkPrimaryButton = Color(0xFFF8F9FA);
  static const Color darkButtonText = Color(0xFF0E1015);
  static const Color darkDisabledButton = Color(0xFF242733);
  static const Color darkDisabledText = Color(0xFF52525B);
  static const Color darkDivider = Color(0xFF242733);

  // Dynamic Getters
  static Color get background => ThemeService.instance.isDark ? darkBackground : lightBackground;
  static Color get card => ThemeService.instance.isDark ? darkCard : lightCard;
  static Color get primaryText => ThemeService.instance.isDark ? darkPrimaryText : lightPrimaryText;
  static Color get secondaryText => ThemeService.instance.isDark ? darkSecondaryText : lightSecondaryText;
  static Color get mutedText => ThemeService.instance.isDark ? darkMutedText : lightMutedText;
  static Color get inputBackground => ThemeService.instance.isDark ? darkInputBackground : lightInputBackground;
  static Color get border => ThemeService.instance.isDark ? darkBorder : lightBorder;
  static Color get primaryButton => ThemeService.instance.isDark ? darkPrimaryButton : lightPrimaryButton;
  static Color get buttonText => ThemeService.instance.isDark ? darkButtonText : lightButtonText;
  static Color get disabledButton => ThemeService.instance.isDark ? darkDisabledButton : lightDisabledButton;
  static Color get disabledText => ThemeService.instance.isDark ? darkDisabledText : lightDisabledText;
  static Color get divider => ThemeService.instance.isDark ? darkDivider : lightDivider;

  // Context-aware color selector helper
  static Color of(BuildContext context, {required Color light, required Color dark}) {
    final isDark = ThemeService.instance.isDarkMode(context);
    return isDark ? dark : light;
  }
}

class AppTypography {
  static TextStyle heading(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 28,
      fontWeight: FontWeight.w700,
      color: AppColors.primaryText,
      height: 1.15,
      letterSpacing: -0.5,
    );
  }

  static TextStyle supporting(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 15,
      fontWeight: FontWeight.w400,
      color: AppColors.secondaryText,
      height: 1.4,
    );
  }

  static TextStyle body(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.w400,
      color: AppColors.primaryText,
      height: 1.45,
    );
  }

  static TextStyle phoneHighlight(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 15,
      fontWeight: FontWeight.w600,
      color: AppColors.primaryText,
      height: 1.4,
    );
  }

  static TextStyle button(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: AppColors.buttonText,
      letterSpacing: -0.2,
    );
  }

  static TextStyle inputText(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w500,
      color: AppColors.primaryText,
    );
  }

  static TextStyle placeholder(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w400,
      color: AppColors.mutedText,
    );
  }

  static TextStyle countryCode(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: AppColors.primaryText,
    );
  }

  static TextStyle otpDigit(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 22,
      fontWeight: FontWeight.w700,
      color: AppColors.primaryText,
    );
  }

  static TextStyle link(BuildContext context) {
    return GoogleFonts.inter(
      fontSize: 14,
      fontWeight: FontWeight.w600,
      color: AppColors.primaryText,
      decoration: TextDecoration.underline,
    );
  }
}

ThemeData buildLightTheme() {
  final baseTheme = ThemeData(
    scaffoldBackgroundColor: AppColors.lightBackground,
    brightness: Brightness.light,
    colorScheme: const ColorScheme.light(
      primary: AppColors.lightPrimaryButton,
      onPrimary: AppColors.lightButtonText,
      surface: AppColors.lightBackground,
      onSurface: AppColors.lightPrimaryText,
      outline: AppColors.lightBorder,
    ),
    dividerColor: AppColors.lightDivider,
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.lightBackground,
      foregroundColor: AppColors.lightPrimaryText,
      elevation: 0,
    ),
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: AppColors.lightBackground,
    ),
    dialogTheme: const DialogThemeData(
      backgroundColor: AppColors.lightBackground,
    ),
  );

  return baseTheme.copyWith(
    textTheme: GoogleFonts.interTextTheme(baseTheme.textTheme),
  );
}

ThemeData buildDarkTheme() {
  final baseTheme = ThemeData(
    scaffoldBackgroundColor: AppColors.darkBackground,
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: AppColors.darkPrimaryButton,
      onPrimary: AppColors.darkButtonText,
      surface: AppColors.darkBackground,
      onSurface: AppColors.darkPrimaryText,
      outline: AppColors.darkBorder,
    ),
    dividerColor: AppColors.darkDivider,
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.darkBackground,
      foregroundColor: AppColors.darkPrimaryText,
      elevation: 0,
    ),
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: AppColors.darkCard,
    ),
    dialogTheme: const DialogThemeData(
      backgroundColor: AppColors.darkCard,
    ),
  );

  return baseTheme.copyWith(
    textTheme: GoogleFonts.interTextTheme(baseTheme.textTheme),
  );
}

/// Backward compatible alias for initial theme setup
ThemeData buildAppTheme() => buildLightTheme();
