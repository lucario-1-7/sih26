import 'package:customer_app/theme/feather_icons.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class AuthHeader extends StatelessWidget {
  final VoidCallback? onBack;
  final bool showBack;

  const AuthHeader({
    super.key,
    this.onBack,
    this.showBack = true,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 8.0, bottom: 4.0),
      child: Row(
        children: [
          if (showBack)
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: onBack ?? () => Navigator.maybePop(context),
              child: Container(
                width: 40,
                height: 40,
                alignment: Alignment.centerLeft,
                child: Icon(
                  FeatherIcons.arrowLeft,
                  size: 20,
                  color: AppColors.primaryText,
                ),
              ),
            )
          else
            const SizedBox(width: 40, height: 40),
        ],
      ),
    );
  }
}
