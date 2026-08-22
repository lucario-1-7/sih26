import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppColors {
  // Monochromatic Palette
  static const Color background = Color(0xFFFFFFFF);
  static const Color primaryText = Color(0xFF000000);
  static const Color secondaryText = Color(0xFF555555);
  static const Color mutedText = Color(0xFF8E8E93);
  static const Color inputBackground = Color(0xFFF6F6F8);
  static const Color border = Color(0xFFE5E5EA);
  static const Color primaryButton = Color(0xFF000000);
  static const Color buttonText = Color(0xFFFFFFFF);
  static const Color disabledButton = Color(0xFFE5E5EA);
  static const Color disabledText = Color(0xFF8E8E93);
  static const Color divider = Color(0xFFE5E5EA);
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

ThemeData buildAppTheme() {
  final baseTheme = ThemeData(
    scaffoldBackgroundColor: AppColors.background,
    brightness: Brightness.light,
    colorScheme: const ColorScheme.light(
      primary: AppColors.primaryButton,
      onPrimary: AppColors.buttonText,
      surface: AppColors.background,
      onSurface: AppColors.primaryText,
    ),
  );

  return baseTheme.copyWith(
    textTheme: GoogleFonts.interTextTheme(baseTheme.textTheme),
  );
}
