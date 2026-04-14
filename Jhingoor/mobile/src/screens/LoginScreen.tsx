import { zodResolver } from "@hookform/resolvers/zod";
import * as AppleAuthentication from "expo-apple-authentication";
import * as WebBrowser from "expo-web-browser";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Alert, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { z } from "zod";

import { api } from "../api/client";
import { PrimaryButton } from "../components/PrimaryButton";
import { GoogleSignInBlock } from "./GoogleSignInBlock";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";
import { useAuthStore } from "../store/authStore";

WebBrowser.maybeCompleteAuthSession();

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;

export function LoginScreen() {
  const insets = useSafeAreaInsets();
  const setSession = useAuthStore((s) => s.setSession);
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [loading, setLoading] = useState(false);

  const googleConfigured =
    !!process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID ||
    !!process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID ||
    !!process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID;

  const { control, handleSubmit, reset } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (values: FormValues) => {
    setLoading(true);
    try {
      const path = mode === "login" ? "/auth/login" : "/auth/signup";
      const { data } = await api.post<{ access_token: string }>(path, values);
      await setSession(data.access_token);
    } catch (err: unknown) {
      let msg = String(err);
      if (typeof err === "object" && err && "response" in err) {
        const r = err as { response?: { data?: unknown } };
        msg = JSON.stringify(r.response?.data ?? r);
      }
      Alert.alert("Authentication failed", msg);
    } finally {
      setLoading(false);
    }
  };

  const onApple = async () => {
    try {
      const cred = await AppleAuthentication.signInAsync({
        requestedScopes: [
          AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
          AppleAuthentication.AppleAuthenticationScope.EMAIL,
        ],
      });
      if (!cred.identityToken) {
        Alert.alert("Apple Sign In", "No identity token returned");
        return;
      }
      setLoading(true);
      const { data } = await api.post<{ access_token: string }>("/auth/apple", {
        identity_token: cred.identityToken,
      });
      await setSession(data.access_token);
    } catch (e: unknown) {
      if ((e as { code?: string }).code === "ERR_REQUEST_CANCELED") return;
      Alert.alert("Apple sign-in failed", String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={{ paddingBottom: insets.bottom + 24, paddingTop: insets.top + 8 }}
      keyboardShouldPersistTaps="handled"
    >
      <View style={styles.topRow}>
        <Text style={[typography.displayBrand, { fontSize: 18 }]}>JHINGOOR</Text>
        <Text style={styles.join}>JOIN THE PULSE</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.welcome}>Welcome back</Text>
        <Text style={styles.sub}>Ready to accelerate your performance?</Text>

        <View style={styles.segment}>
          <Pressable
            onPress={() => setMode("login")}
            style={[styles.segmentBtn, mode === "login" && styles.segmentActive]}
          >
            <Text style={[styles.segmentText, mode === "login" && styles.segmentTextActive]}>Login</Text>
          </Pressable>
          <Pressable
            onPress={() => setMode("signup")}
            style={[styles.segmentBtn, mode === "signup" && styles.segmentActive]}
          >
            <Text style={[styles.segmentText, mode === "signup" && styles.segmentTextActive]}>Signup</Text>
          </Pressable>
        </View>

        <Text style={styles.fieldLabel}>Email Address</Text>
        <Controller
          control={control}
          name="email"
          render={({ field: { onChange, onBlur, value } }) => (
            <TextInput
              style={styles.input}
              placeholder="name@example.com"
              placeholderTextColor={colors.onSurfaceVariant}
              autoCapitalize="none"
              keyboardType="email-address"
              onBlur={onBlur}
              onChangeText={onChange}
              value={value}
            />
          )}
        />

        <View style={styles.pwRow}>
          <Text style={styles.fieldLabel}>Password</Text>
          <Text style={styles.forgot}>Forgot?</Text>
        </View>
        <Controller
          control={control}
          name="password"
          render={({ field: { onChange, onBlur, value } }) => (
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              placeholderTextColor={colors.onSurfaceVariant}
              secureTextEntry
              onBlur={onBlur}
              onChangeText={onChange}
              value={value}
            />
          )}
        />

        <PrimaryButton
          title={mode === "login" ? "Start the Pulse" : "Create account"}
          loading={loading}
          onPress={handleSubmit(onSubmit)}
          style={{ marginTop: 16 }}
        />

        <View style={styles.dividerRow}>
          <View style={styles.divLine} />
          <Text style={styles.divText}>OR CONTINUE WITH</Text>
          <View style={styles.divLine} />
        </View>

        <View style={styles.socialRow}>
          {googleConfigured ? (
            <GoogleSignInBlock setSession={setSession} loading={loading} setLoading={setLoading} />
          ) : (
            <PrimaryButton
              title="Google"
              variant="outline"
              loading={loading}
              onPress={() =>
                Alert.alert("Google", "Set EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID (and iOS/Android IDs) in mobile/.env")
              }
              style={{ flex: 1, marginRight: 8, paddingVertical: 12 }}
            />
          )}
          {Platform.OS === "ios" ? (
            <PrimaryButton
              title="Apple"
              variant="outline"
              loading={loading}
              onPress={onApple}
              style={{ flex: 1, marginLeft: 8, paddingVertical: 12 }}
            />
          ) : (
            <View style={{ flex: 1, marginLeft: 8 }} />
          )}
        </View>

        <Pressable
          onPress={() => {
            setMode(mode === "login" ? "signup" : "login");
            reset();
          }}
          style={{ marginTop: 16 }}
        >
          <Text style={styles.footer}>
            {mode === "login" ? "Don't have an account? " : "Already have an account? "}
            <Text style={styles.footerLink}>Join the Pulse</Text>
          </Text>
        </Pressable>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#121212", paddingHorizontal: 16 },
  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  join: { color: colors.onSurface, fontSize: 10, fontWeight: "700", letterSpacing: 1 },
  card: {
    backgroundColor: colors.surfaceContainerHigh,
    borderRadius: 36,
    padding: 24,
  },
  welcome: { fontFamily: "Manrope_700Bold", fontSize: 26, color: colors.onSurface },
  sub: { marginTop: 6, color: colors.onSurfaceVariant, fontFamily: "Inter_400Regular", marginBottom: 20 },
  segment: {
    flexDirection: "row",
    backgroundColor: "#000",
    borderRadius: 999,
    padding: 4,
    marginBottom: 20,
  },
  segmentBtn: { flex: 1, paddingVertical: 10, borderRadius: 999, alignItems: "center" },
  segmentActive: { backgroundColor: colors.primaryContainer },
  segmentText: { color: colors.onSurface, fontWeight: "700" },
  segmentTextActive: { color: colors.onPrimaryFixed },
  fieldLabel: { ...typography.caption, marginBottom: 6 },
  input: {
    backgroundColor: colors.surfaceContainerHighest,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: colors.onSurface,
    marginBottom: 14,
  },
  pwRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  forgot: { color: colors.primaryContainer, fontWeight: "700", fontSize: 12 },
  dividerRow: { flexDirection: "row", alignItems: "center", marginVertical: 20 },
  divLine: { flex: 1, height: 1, backgroundColor: colors.outlineVariant },
  divText: { marginHorizontal: 8, color: colors.onSurfaceVariant, fontSize: 10, fontWeight: "700" },
  socialRow: { flexDirection: "row" },
  footer: { textAlign: "center", color: colors.onSurfaceVariant },
  footerLink: { color: colors.primaryContainer, fontWeight: "800" },
});
