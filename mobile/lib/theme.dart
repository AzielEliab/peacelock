import 'package:flutter/material.dart';

/// Paper / charcoal surfaces. Gold focus. Follows the system theme.
const Color kPaper = Color(0xFFF7F4EC);
const Color kInk = Color(0xFF1C1914);
const Color kMatteBlack = Color(0xFF12110E);
const Color kSurface = Color(0xFF1C1B16);
const Color kGold = Color(0xFFC9A227);
const Color kGoldDim = Color(0xFF8A7219);
const Color kIvory = Color(0xFFF4EFE4);

ThemeData buildAppTheme() => buildDarkTheme();

ThemeData buildLightTheme() {
  const scheme = ColorScheme.light(
    brightness: Brightness.light,
    primary: kGold,
    onPrimary: kInk,
    secondary: kGoldDim,
    onSecondary: kIvory,
    surface: Color(0xFFFFFDF8),
    onSurface: kInk,
    error: Color(0xFF8C2F2C),
    onError: kIvory,
  );
  return _theme(scheme, kPaper, kInk);
}

ThemeData buildDarkTheme() {
  const scheme = ColorScheme.dark(
    brightness: Brightness.dark,
    primary: kGold,
    onPrimary: kInk,
    secondary: kGoldDim,
    onSecondary: kIvory,
    surface: kSurface,
    onSurface: kIvory,
    error: Color(0xFFF0B4AE),
    onError: kInk,
  );
  return _theme(scheme, kMatteBlack, kIvory);
}

ThemeData _theme(ColorScheme scheme, Color scaffold, Color ink) {
  return ThemeData(
    useMaterial3: true,
    brightness: scheme.brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: scaffold,
    focusColor: kGold,
    appBarTheme: AppBarTheme(
      backgroundColor: scaffold,
      foregroundColor: ink,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0x33C9A227)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.surface,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: kGold, width: 2),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: kGold,
        foregroundColor: kInk,
        minimumSize: const Size.fromHeight(48),
      ),
    ),
  );
}
