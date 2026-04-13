import { useQuery } from "@tanstack/react-query";
import { Info } from "lucide-react-native";
import { RefreshControl, ScrollView, StyleSheet, Text, View } from "react-native";
import Svg, { Circle, Line, Polyline } from "react-native-svg";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

export function TrendsScreen() {
  const momentum = useQuery({
    queryKey: ["momentum"],
    queryFn: async () => (await api.get("/user/momentum")).data as Record<string, unknown>,
  });
  const weight = useQuery({
    queryKey: ["weight-history"],
    queryFn: async () => (await api.get("/user/weight-history")).data as { points: { day: string; weight_kg: number }[] },
  });
  const mix = useQuery({
    queryKey: ["activity-mix"],
    queryFn: async () => (await api.get("/user/activity-mix")).data as { rows: { label: string; hours: number }[]; ring_pct: number },
  });
  const insight = useQuery({
    queryKey: ["trends-insight"],
    queryFn: async () => (await api.get("/user/insights")).data as { text: string | null },
  });

  const pts = weight.data?.points ?? [];
  const w = 280;
  const h = 120;
  const minW = pts.length ? Math.min(...pts.map((p) => p.weight_kg)) : 0;
  const maxW = pts.length ? Math.max(...pts.map((p) => p.weight_kg)) : 1;
  const norm = (v: number) => (maxW === minW ? 0.5 : (v - minW) / (maxW - minW));
  const poly = pts
    .map((p, i) => {
      const x = 20 + (i / Math.max(pts.length - 1, 1)) * (w - 40);
      const y = 20 + (1 - norm(p.weight_kg)) * (h - 40);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <View style={styles.screen}>
      <AppHeader />
      <ScrollView
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
        refreshControl={
          <RefreshControl
            refreshing={momentum.isFetching || weight.isFetching}
            onRefresh={() => {
              void momentum.refetch();
              void weight.refetch();
              void mix.refetch();
              void insight.refetch();
            }}
            tintColor={colors.primaryContainer}
          />
        }
      >
        <Text style={[typography.label, { marginBottom: 8 }]}>CURRENT MOMENTUM</Text>
        <Card style={{ marginBottom: 16 }}>
          <Text style={styles.excellent}>{String(momentum.data?.status ?? "—")}</Text>
          <View style={styles.metricsRow}>
            <Text style={typography.caption}>
              {String(momentum.data?.bmi ?? "—")} BMI INDEX{"\n"}
              {String(momentum.data?.weight_change_month_kg ?? "—")} kg THIS MONTH
            </Text>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{String(momentum.data?.regional_rank_label ?? "")}</Text>
            </View>
          </View>
        </Card>

        <Text style={[typography.title, { marginBottom: 8 }]}>Weight trend</Text>
        <Card style={{ marginBottom: 16 }}>
          <Svg width={w} height={h}>
            {[0, 0.25, 0.5, 0.75, 1].map((t) => (
              <Line
                key={t}
                x1={10}
                x2={w - 10}
                y1={20 + t * (h - 40)}
                y2={20 + t * (h - 40)}
                stroke={colors.outlineVariant}
                strokeWidth={0.5}
              />
            ))}
            {poly ? <Polyline points={poly} fill="none" stroke={colors.primaryContainer} strokeWidth={3} /> : null}
          </Svg>
          <View style={styles.daysRow}>
            {pts.map((p) => (
              <Text key={p.day} style={typography.caption}>
                {p.day}
              </Text>
            ))}
          </View>
        </Card>

        <Card style={{ marginBottom: 16 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text style={typography.title}>Activity Mix</Text>
            <Info size={16} color={colors.onSurfaceVariant} />
          </View>
          <View style={{ flexDirection: "row", marginTop: 12, alignItems: "center" }}>
            <Svg width={100} height={100} style={{ marginRight: 16 }}>
              <Circle cx={50} cy={50} r={36} stroke={colors.surfaceBright} strokeWidth={10} fill="none" />
              <Circle
                cx={50}
                cy={50}
                r={36}
                stroke={colors.primaryContainer}
                strokeWidth={10}
                fill="none"
                strokeDasharray={`${2 * Math.PI * 36 * ((mix.data?.ring_pct ?? 0) / 100)} ${2 * Math.PI * 36}`}
                strokeLinecap="round"
                transform="rotate(-90 50 50)"
              />
            </Svg>
            <View style={{ flex: 1 }}>
              {(mix.data?.rows ?? []).map((r) => (
                <View key={r.label} style={{ marginBottom: 8 }}>
                  <Text style={typography.caption}>
                    {r.label} ({r.hours}h)
                  </Text>
                  <View style={styles.barTrack}>
                    <View
                      style={[
                        styles.barFill,
                        { width: `${Math.min(100, (r.hours / 14) * 100)}%` },
                        r.label.toLowerCase().includes("cardio") && { backgroundColor: colors.secondary },
                      ]}
                    />
                  </View>
                </View>
              ))}
            </View>
          </View>
        </Card>

        <Card style={{ borderWidth: 1, borderColor: colors.primaryContainer }}>
          <Text style={[typography.label, { color: colors.primaryContainer }]}>AI TRAINING INSIGHT</Text>
          <Text style={[typography.body, { marginTop: 8, fontStyle: "italic" }]}>
            {insight.data?.text ?? "—"}
          </Text>
        </Card>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  excellent: { fontFamily: "Manrope_800ExtraBold", fontSize: 28, color: colors.primaryContainer },
  metricsRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 12, alignItems: "center" },
  badge: { backgroundColor: "#2a2d1a", paddingHorizontal: 12, paddingVertical: 8, borderRadius: 999 },
  badgeText: { color: colors.primaryContainer, fontWeight: "800", fontSize: 10 },
  daysRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 8 },
  barTrack: { height: 8, borderRadius: 4, backgroundColor: colors.surfaceBright, marginTop: 4, overflow: "hidden" },
  barFill: { height: 8, borderRadius: 4, backgroundColor: colors.primaryContainer },
});
