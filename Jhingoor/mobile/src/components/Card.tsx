import { ReactNode } from "react";
import { StyleSheet, View, ViewStyle } from "react-native";

import { colors } from "../theme/colors";

type Accent = "lime" | "teal" | "none";

type Props = {
  children: ReactNode;
  style?: ViewStyle;
  accent?: Accent;
};

export function Card({ children, style, accent = "none" }: Props) {
  const accentBar =
    accent === "lime"
      ? styles.accentLime
      : accent === "teal"
        ? styles.accentTeal
        : null;
  return (
    <View style={[styles.card, style]}>
      {accentBar ? <View style={[styles.accentBar, accentBar]} /> : null}
      <View style={styles.inner}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surfaceContainerHigh,
    borderRadius: 20,
    overflow: "hidden",
    flexDirection: "row",
  },
  accentBar: { width: 4 },
  accentLime: { backgroundColor: colors.primaryContainer },
  accentTeal: { backgroundColor: colors.secondary },
  inner: { flex: 1, padding: 16 },
});
