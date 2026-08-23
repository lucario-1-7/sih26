import 'package:flutter/material.dart';

class SmoothPageRoute<T> extends PageRouteBuilder<T> {
  final Widget child;

  SmoothPageRoute({
    required this.child,
    super.settings,
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => child,
          transitionDuration: const Duration(milliseconds: 320),
          reverseTransitionDuration: const Duration(milliseconds: 280),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            // Easing curves
            final primaryCurve = CurvedAnimation(
              parent: animation,
              curve: const Cubic(0.25, 1.0, 0.5, 1.0), // Fast start, smooth deceleration
              reverseCurve: Curves.easeInOutCubic,
            );

            final secondaryCurve = CurvedAnimation(
              parent: secondaryAnimation,
              curve: const Cubic(0.25, 1.0, 0.5, 1.0),
              reverseCurve: Curves.easeInOutCubic,
            );

            // Incoming slide + fade
            final inSlide = Tween<Offset>(
              begin: const Offset(0.25, 0.0),
              end: Offset.zero,
            ).animate(primaryCurve);

            final inFade = Tween<double>(
              begin: 0.0,
              end: 1.0,
            ).animate(primaryCurve);

            // Outgoing subtle parallax slide + fade
            final outSlide = Tween<Offset>(
              begin: Offset.zero,
              end: const Offset(-0.08, 0.0),
            ).animate(secondaryCurve);

            final outFade = Tween<double>(
              begin: 1.0,
              end: 0.85,
            ).animate(secondaryCurve);

            return SlideTransition(
              position: outSlide,
              child: FadeTransition(
                opacity: outFade,
                child: SlideTransition(
                  position: inSlide,
                  child: FadeTransition(
                    opacity: inFade,
                    child: child,
                  ),
                ),
              ),
            );
          },
        );
}
