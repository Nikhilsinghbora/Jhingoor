import * as Google from "expo-auth-session/providers/google";
import { useEffect } from "react";
import { Alert } from "react-native";

import { api } from "../api/client";
import { PrimaryButton } from "../components/PrimaryButton";

type Props = {
  setSession: (token: string) => Promise<void>;
  loading: boolean;
  setLoading: (v: boolean) => void;
};

/**
 * Isolated so `useIdTokenAuthRequest` only runs when Google env is configured
 * (undefined client IDs can break the app on some platforms).
 */
export function GoogleSignInBlock({ setSession, loading, setLoading }: Props) {
  const [request, response, promptAsync] = Google.useIdTokenAuthRequest({
    iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID,
    androidClientId: process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID,
    webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
  });

  useEffect(() => {
    const run = async () => {
      if (response?.type !== "success") return;
      const idToken =
        (response.params as { id_token?: string }).id_token ||
        (response.authentication as { idToken?: string } | null)?.idToken;
      if (!idToken) return;
      setLoading(true);
      try {
        const { data } = await api.post<{ access_token: string }>("/auth/google", { id_token: idToken });
        await setSession(data.access_token);
      } catch (e) {
        Alert.alert("Google sign-in failed", String(e));
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [response, setSession, setLoading]);

  return (
    <PrimaryButton
      title="Google"
      variant="outline"
      loading={loading}
      onPress={async () => {
        if (!request) {
          Alert.alert("Google", "OAuth request not ready. Check EXPO_PUBLIC_GOOGLE_* in .env.");
          return;
        }
        await promptAsync();
      }}
      style={{ flex: 1, marginRight: 8, paddingVertical: 12 }}
    />
  );
}
