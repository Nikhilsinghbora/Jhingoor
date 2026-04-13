import { useQuery } from "@tanstack/react-query";
import { Activity, Droplets, Dumbbell } from "lucide-react-native";
import { RefreshControl, ScrollView, StyleSheet, Text, View } from "react-native";
import Svg, { Circle } from "react-native-svg";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { PrimaryButton } from "../components/PrimaryButton";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

type Dashboard = {
  active_energy_kcal: number;
  steps: number;
  sleep_minutes: number;
  insight: string | null;
  hydration_target_ml: number;
  hydration_current_ml: number;
  next_workout_title: string | null;
  biometrics: { metric: string; value: number; change: string | null }[];
};

export function HomeScreen() {
  const q = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get<Dashboard>("/user/dashboard")).data,
  });

  const data = q.data;
  const ringPct = data ? Math.min(1, data.active_energy_kcal / 2500) : 0;

  return (
    <View style={styles.screen}>
      <AppHeader />
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={q.isFetching} onRefresh={() => void q.refetch()} tintColor={colors.primaryContainer} />}
      >
        <Card style={{ marginBottom: 16 }}>
          <Text style={typography.label}>ACTIVE ENERGY</Text>
          <View style={styles.energyRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.energyVal}>{data?.active_energy_kcal ?? "—"} kcal</Text>
              <Text style={styles.subStats}>
                Steps {data?.steps ?? "—"} · Sleep {data ? Math.floor(data.sleep_minutes / 60) : "—"}h{" "}
                {data ? data.sleep_minutes % 60 : ""}m
              </Text>
            </View>
            <View style={styles.ringWrap}>
              <Svg width={72} height={72}>
                <Circle cx={36} cy={36} r={30} stroke={colors.surfaceBright} strokeWidth={8} fill="none" />
                <Circle
                  cx={36}
                  cy={36}
                  r={30}
                  stroke={colors.primaryContainer}
                  strokeWidth={8}
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 30 * ringPct} ${2 * Math.PI * 30}`}
                  strokeLinecap="round"
                  transform="rotate(-90 36 36)"
                />
              </Svg>
              <View style={styles.bolt}>
                <Activity color={colors.primaryContainer} size={22} />
              </View>
            </View>
          </View>
        </Card>

        <Card style={{ marginBottom: 16 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <Dumbbell color={colors.primaryContainer} size={18} />
            <Text style={[typography.label, { color: colors.primaryContainer }]}>AI PULSE INSIGHT</Text>
          </View>
          <Text style={[typography.body, { fontStyle: "italic", color: colors.onSurface }]}>
            {data?.insight ?? "Your coach insight will appear here."}
          </Text>
        </Card>

        <Text style={[typography.title, { marginBottom: 8 }]}>Biometric Trends</Text>
        <View style={styles.grid}>
          {(data?.biometrics ?? []).slice(0, 4).map((b) => (
            <Card key={b.metric} style={{ flex: 1, minWidth: "45%", margin: 4 }}>
              <Text style={typography.label}>{b.metric.toUpperCase()}</Text>
              <Text style={styles.metricVal}>{b.value}</Text>
              <Text style={{ color: colors.secondary, marginTop: 4 }}>{b.change}</Text>
            </Card>
          ))}
        </View>

        <View style={styles.actionsRow}>
          <Card style={{ flex: 1, marginRight: 6 }} accent="teal">
            <Droplets color={colors.secondary} size={22} />
            <Text style={[typography.title, { marginTop: 8 }]}>Log Hydration</Text>
            <Text style={typography.caption}>
              Target: {(data?.hydration_target_ml ?? 3500) / 1000}L · Current:{" "}
              {(data?.hydration_current_ml ?? 0) / 1000}L
            </Text>
          </Card>
          <Card style={{ flex: 1, marginLeft: 6 }} accent="lime">
            <Dumbbell color={colors.primaryContainer} size={22} />
            <Text style={[typography.title, { marginTop: 8, color: colors.primaryContainer }]}>Start Session</Text>
            <Text style={typography.caption}>Next: {data?.next_workout_title ?? "—"}</Text>
          </Card>
        </View>

        <PrimaryButton title="Refresh pulse" onPress={() => void q.refetch()} style={{ marginTop: 20 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 16, paddingBottom: 32 },
  energyRow: { flexDirection: "row", alignItems: "center", marginTop: 8 },
  energyVal: { fontFamily: "Manrope_800ExtraBold", fontSize: 28, color: colors.primaryContainer },
  subStats: { marginTop: 8, color: colors.onSurfaceVariant },
  ringWrap: { width: 72, height: 72, alignItems: "center", justifyContent: "center" },
  bolt: { position: "absolute" },
  grid: { flexDirection: "row", flexWrap: "wrap", marginHorizontal: -4 },
  actionsRow: { flexDirection: "row", marginTop: 16 },
  metricVal: { fontFamily: "Manrope_700Bold", fontSize: 22, marginTop: 4 },
});
