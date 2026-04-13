import { NavigationContainer, DarkTheme } from "@react-navigation/native";
import { useEffect } from "react";
import { ActivityIndicator, StyleSheet, View } from "react-native";

import { getAccessToken } from "../auth/tokenStorage";
import { colors } from "../theme/colors";
import { useAuthStore } from "../store/authStore";
import { AuthNavigator } from "./AuthNavigator";
import { MainTabs } from "./MainTabs";

const navTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: colors.background,
    card: colors.surfaceContainerLow,
    text: colors.onSurface,
    border: colors.outlineVariant,
    primary: colors.primaryContainer,
  },
};

export function RootNavigator() {
  const token = useAuthStore((s) => s.token);
  const hydrated = useAuthStore((s) => s.hydrated);
  const hydrateFromStorage = useAuthStore((s) => s.hydrateFromStorage);

  useEffect(() => {
    void (async () => {
      const t = await getAccessToken();
      hydrateFromStorage(t);
    })();
  }, [hydrateFromStorage]);

  if (!hydrated) {
    return (
      <View style={styles.boot}>
        <ActivityIndicator color={colors.primaryContainer} size="large" />
      </View>
    );
  }

  return (
    <NavigationContainer theme={navTheme}>{token ? <MainTabs /> : <AuthNavigator />}</NavigationContainer>
  );
}

const styles = StyleSheet.create({
  boot: { flex: 1, backgroundColor: colors.background, alignItems: "center", justifyContent: "center" },
});
