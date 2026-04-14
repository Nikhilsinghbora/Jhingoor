import { NavigationContainer, DarkTheme } from "@react-navigation/native";
import { useEffect } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

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
      let t: string | null = null;
      try {
        t = await getAccessToken();
      } catch {
        t = null;
      } finally {
        hydrateFromStorage(t);
      }
    })();
  }, [hydrateFromStorage]);

  if (!hydrated) {
    return (
      <View style={styles.boot}>
        <ActivityIndicator color={colors.primaryContainer} size="large" />
        <Text style={{ color: colors.onSurfaceVariant, marginTop: 12 }}>Starting…</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <NavigationContainer theme={navTheme}>
        {token ? <MainTabs /> : <AuthNavigator />}
      </NavigationContainer>
    </View>
  );
}

const styles = StyleSheet.create({
  boot: { flex: 1, backgroundColor: colors.background, alignItems: "center", justifyContent: "center" },
});
