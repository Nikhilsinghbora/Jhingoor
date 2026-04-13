import { TextStyle } from "react-native";

export const typography = {
  displayBrand: {
    fontFamily: "Manrope_800ExtraBold",
    fontStyle: "italic" as TextStyle["fontStyle"],
    fontSize: 22,
    letterSpacing: 1,
    color: "#daf900",
  },
  headline: {
    fontFamily: "Manrope_700Bold",
    fontSize: 20,
    color: "#f9f9fd",
  },
  title: {
    fontFamily: "Manrope_600SemiBold",
    fontSize: 16,
    color: "#f9f9fd",
  },
  body: {
    fontFamily: "Inter_400Regular",
    fontSize: 14,
    color: "#f9f9fd",
  },
  caption: {
    fontFamily: "Inter_500Medium",
    fontSize: 12,
    color: "#aaabaf",
  },
  label: {
    fontFamily: "Inter_600SemiBold",
    fontSize: 11,
    letterSpacing: 0.6,
    color: "#aaabaf",
  },
};
