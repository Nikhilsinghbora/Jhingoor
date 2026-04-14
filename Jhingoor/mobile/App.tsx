import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  useFonts as useInterFonts,
} from "@expo-google-fonts/inter";
import {
  Manrope_600SemiBold,
  Manrope_700Bold,
  Manrope_800ExtraBold,
  useFonts as useManropeFonts,
} from "@expo-google-fonts/manrope";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Text, View } from "react-native";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { QueryClientAuthBridge } from "./src/components/QueryClientAuthBridge";
import { RootNavigator } from "./src/navigation/RootNavigator";
import { colors } from "./src/theme/colors";

SplashScreen.preventAutoHideAsync().catch(() => undefined);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
});

const FONT_WAIT_MS = 10_000;

export default function App() {
  const [interLoaded, interError] = useInterFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
  });
  const [manropeLoaded, manropeError] = useManropeFonts({
    Manrope_600SemiBold,
    Manrope_700Bold,
    Manrope_800ExtraBold,
  });

  const [fontWaitElapsed, setFontWaitElapsed] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setFontWaitElapsed(true), FONT_WAIT_MS);
    return () => clearTimeout(t);
  }, []);

  const fontsOk =
    (interLoaded && manropeLoaded) ||
    interError != null ||
    manropeError != null ||
    fontWaitElapsed;

  const hideSplash = useCallback(async () => {
    if (fontsOk) await SplashScreen.hideAsync();
  }, [fontsOk]);

  useEffect(() => {
    void hideSplash();
  }, [hideSplash]);

  if (!fontsOk) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: colors.background,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator size="large" color={colors.primaryContainer} />
        <Text style={{ color: colors.onSurfaceVariant, marginTop: 16 }}>Loading…</Text>
      </View>
    );
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <QueryClientAuthBridge />
          <StatusBar style="light" />
          <RootNavigator />
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
