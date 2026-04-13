import { ActivityIndicator, Pressable, StyleSheet, Text, ViewStyle } from "react-native";

import { colors } from "../theme/colors";

type Props = {
  title: string;
  onPress: () => void;
  loading?: boolean;
  variant?: "lime" | "outline";
  style?: ViewStyle;
};

export function PrimaryButton({
  title,
  onPress,
  loading,
  variant = "lime",
  style,
}: Props) {
  const isOutline = variant === "outline";
  return (
    <Pressable
      onPress={onPress}
      disabled={loading}
      style={({ pressed }) => [
        styles.btn,
        isOutline ? styles.outline : styles.solid,
        pressed && styles.pressed,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={isOutline ? colors.secondary : colors.onPrimaryFixed} />
      ) : (
        <Text style={[styles.text, isOutline && styles.textOutline]}>{title}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    borderRadius: 999,
    paddingVertical: 16,
    alignItems: "center",
    justifyContent: "center",
  },
  solid: { backgroundColor: colors.primaryContainer },
  outline: {
    borderWidth: 1,
    borderColor: colors.secondary,
    backgroundColor: "transparent",
  },
  pressed: { opacity: 0.88 },
  text: {
    fontWeight: "800",
    color: colors.onPrimaryFixed,
    letterSpacing: 0.5,
  },
  textOutline: { color: colors.secondary },
});
