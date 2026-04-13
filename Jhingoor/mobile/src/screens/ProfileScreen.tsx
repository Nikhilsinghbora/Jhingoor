import type { ReactNode } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronRight, Languages, Lock, LogOut, Target } from "lucide-react-native";
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { PrimaryButton } from "../components/PrimaryButton";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";
import { useAuthStore } from "../store/authStore";

export function ProfileScreen() {
  const qc = useQueryClient();
  const setSession = useAuthStore((s) => s.setSession);
  const profile = useQuery({
    queryKey: ["profile"],
    queryFn: async () => (await api.get("/user/profile")).data as Record<string, string | number>,
  });
  const goals = useQuery({
    queryKey: ["goals"],
    queryFn: async () => (await api.get("/user/goals")).data as Record<string, number | null>,
  });
  const sub = useQuery({
    queryKey: ["subscription"],
    queryFn: async () => (await api.get("/user/subscription")).data as Record<string, unknown>,
  });

  const signOut = async () => {
    try {
      await api.post("/user/logout");
    } catch {
      /* noop */
    }
    qc.clear();
    await setSession(null);
  };

  return (
    <View style={styles.screen}>
      <AppHeader />
      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
        <Text style={styles.name}>{String(profile.data?.display_name ?? "")}</Text>
        <Text style={styles.bio}>{String(profile.data?.bio ?? "")}</Text>
        <View style={styles.pills}>
          <View style={styles.pillPremium}>
            <Text style={styles.pillPremiumText}>PREMIUM MEMBER</Text>
          </View>
          <View style={styles.pillLvl}>
            <Text style={styles.pillLvlText}>LVL {String(profile.data?.level ?? "")}</Text>
          </View>
        </View>

        <Card style={{ marginTop: 20 }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
            <Text style={typography.title}>Goal Settings</Text>
            <Target color={colors.primaryContainer} size={22} />
          </View>
          <View style={styles.goalCols}>
            <View>
              <Text style={typography.caption}>Target Weight</Text>
              <Text style={styles.goalVal}>{goals.data?.target_weight_kg ?? "—"} kg</Text>
            </View>
            <View>
              <Text style={typography.caption}>Daily Steps</Text>
              <Text style={styles.goalVal}>{goals.data?.daily_steps_target ?? "—"}</Text>
            </View>
          </View>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${goals.data?.goal_progress_pct ?? 0}%` }]} />
          </View>
        </Card>

        <Card style={{ marginTop: 16 }}>
          <Text style={[typography.title, { marginBottom: 12 }]}>Current Plan</Text>
          <Text style={[typography.label, { color: colors.primaryContainer }]}>PRO</Text>
          <Text style={[typography.title, { marginTop: 8 }]}>{String(sub.data?.plan ?? "—")}</Text>
          <Text style={[typography.caption, { marginTop: 6 }]}>
            Next billing {String(sub.data?.next_billing_date ?? "")} for {String(sub.data?.price_display ?? "")}
          </Text>
          <View style={{ flexDirection: "row", marginTop: 16, gap: 10 }}>
            <PrimaryButton title="Manage Plan" onPress={() => Alert.alert("Billing", "Connect your provider.")} style={{ flex: 1 }} />
            <PrimaryButton title="Cancel" variant="outline" onPress={() => Alert.alert("Cancel", "Not implemented.")} style={{ flex: 1 }} />
          </View>
        </Card>

        <Card style={{ marginTop: 16 }}>
          <Row icon={<Lock size={20} color={colors.onSurface} />} title="Privacy & Security" />
          <Row icon={<Languages size={20} color={colors.onSurface} />} title="Language" />
          <Pressable onPress={signOut} style={styles.signOutRow}>
            <LogOut size={20} color="#ff9f7a" />
            <Text style={styles.signOut}>Sign Out</Text>
            <View style={{ flex: 1 }} />
            <ChevronRight color={colors.onSurfaceVariant} size={20} />
          </Pressable>
        </Card>
      </ScrollView>
    </View>
  );
}

function Row({ icon, title }: { icon: ReactNode; title: string }) {
  return (
    <Pressable style={styles.row} onPress={() => Alert.alert(title, "Coming soon.")}>
      {icon}
      <Text style={[typography.body, { marginLeft: 12, flex: 1 }]}>{title}</Text>
      <ChevronRight color={colors.onSurfaceVariant} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  name: { fontFamily: "Manrope_800ExtraBold", fontSize: 26, color: colors.onSurface },
  bio: { marginTop: 8, color: colors.onSurfaceVariant, lineHeight: 20 },
  pills: { flexDirection: "row", gap: 10, marginTop: 12 },
  pillPremium: {
    borderWidth: 1,
    borderColor: colors.primaryContainer,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  pillPremiumText: { color: colors.primaryContainer, fontWeight: "800", fontSize: 10 },
  pillLvl: { backgroundColor: colors.surfaceContainerHigh, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 6 },
  pillLvlText: { color: colors.onSurface, fontWeight: "700", fontSize: 10 },
  goalCols: { flexDirection: "row", justifyContent: "space-between", marginTop: 16 },
  goalVal: { fontFamily: "Manrope_700Bold", fontSize: 22, color: colors.onSurface, marginTop: 4 },
  progressTrack: {
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.surfaceBright,
    marginTop: 16,
    overflow: "hidden",
  },
  progressFill: { height: 8, backgroundColor: colors.primaryContainer },
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.outlineVariant,
  },
  signOutRow: { flexDirection: "row", alignItems: "center", paddingVertical: 14 },
  signOut: { marginLeft: 12, color: "#ff9f7a", fontWeight: "700", flex: 1 },
});
