import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { RefreshControl, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { PrimaryButton } from "../components/PrimaryButton";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

type RecoveryData = { score: number; status: string; sleep_entries: number };

export function SleepTrackerScreen() {
  const qc = useQueryClient();
  const [sleepHours, setSleepHours] = useState("7.5");
  const [sleepQuality, setSleepQuality] = useState("8");

  const recovery = useQuery({
    queryKey: ["recovery-score"],
    queryFn: async () => (await api.get<RecoveryData>("/health/recovery")).data,
    refetchInterval: 20_000,
  });

  const logSleep = useMutation({
    mutationFn: async () =>
      api.post("/health/sleep/log", {
        date: new Date().toISOString().slice(0, 10),
        sleep_hours: Number(sleepHours) || 0,
        sleep_quality: Number(sleepQuality) || 1,
      }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["recovery-score"] });
      await qc.invalidateQueries({ queryKey: ["advanced-insights"] });
    },
  });

  return (
    <View style={styles.screen}>
      <AppHeader />
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={recovery.isFetching}
            onRefresh={() => void recovery.refetch()}
            tintColor={colors.primaryContainer}
          />
        }
      >
        <Card style={{ marginBottom: 12 }}>
          <Text style={typography.label}>RECOVERY</Text>
          <Text style={[typography.title, { marginTop: 8 }]}>Score: {recovery.data?.score ?? 0}</Text>
          <Text style={typography.caption}>
            Status: {recovery.data?.status ?? "unknown"} · Entries: {recovery.data?.sleep_entries ?? 0}
          </Text>
        </Card>

        <Card accent="lime">
          <Text style={typography.title}>Log Sleep</Text>
          <TextInput style={styles.input} value={sleepHours} onChangeText={setSleepHours} keyboardType="decimal-pad" placeholder="Sleep hours" placeholderTextColor={colors.onSurfaceVariant} />
          <TextInput style={styles.input} value={sleepQuality} onChangeText={setSleepQuality} keyboardType="number-pad" placeholder="Sleep quality (1-10)" placeholderTextColor={colors.onSurfaceVariant} />
          <PrimaryButton title="SAVE SLEEP LOG" loading={logSleep.isPending} onPress={() => logSleep.mutate()} style={{ marginTop: 10 }} />
        </Card>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: 16, paddingBottom: 32 },
  input: {
    backgroundColor: colors.surfaceContainerHighest,
    borderRadius: 10,
    color: colors.onSurface,
    padding: 12,
    marginTop: 8,
  },
});
