import { Bell, UserRound } from "lucide-react-native";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

type Props = {
  onBellPress?: () => void;
};

export function AppHeader({ onBellPress }: Props) {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.wrap, { paddingTop: insets.top + 8 }]}>
      <Pressable style={styles.avatar}>
        <UserRound color={colors.onSurface} size={22} />
      </Pressable>
      <Text style={[typography.displayBrand, styles.logo]}>JHINGOOR</Text>
      <Pressable onPress={onBellPress} hitSlop={12} style={styles.bell}>
        <Bell color={colors.primaryContainer} size={24} />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingBottom: 12,
    backgroundColor: colors.surface,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: colors.primaryContainer,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surfaceContainerHigh,
  },
  logo: {
    flex: 1,
    textAlign: "center",
  },
  bell: { padding: 4 },
});
