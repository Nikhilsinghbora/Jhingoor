import { useQuery } from "@tanstack/react-query";
import { RefreshControl, ScrollView, StyleSheet, Text, View } from "react-native";
import { useNavigation } from "@react-navigation/native";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { PrimaryButton } from "../components/PrimaryButton";
import type { HealthStackParamList } from "../navigation/HealthStackNavigator";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";

type AdvancedInsights = {
  summary: string;
  structured: Record<string, { summary: string; payload: Record<string, unknown> }>;
};

export function InsightsDashboardScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<HealthStackParamList>>();
  const insights = useQuery({
    queryKey: ["advanced-insights"],
    queryFn: async () => (await api.get<AdvancedInsights>("/health/insights/advanced")).data,
    refetchInterval: 20_000,
  });

  const entries = Object.entries(insights.data?.structured ?? {});

  return (
    <View style={styles.screen}>
      <AppHeader />
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={insights.isFetching}
            onRefresh={() => void insights.refetch()}
            tintColor={colors.primaryContainer}
          />
        }
      >
        <Card style={{ marginBottom: 12 }} accent="lime">
          <Text style={typography.label}>ADVANCED INSIGHTS</Text>
          <Text style={[typography.body, { marginTop: 8, fontStyle: "italic" }]}>
            {insights.data?.summary ?? "Loading AI insights..."}
          </Text>
        </Card>
        <View style={{ gap: 8, marginBottom: 12 }}>
          <PrimaryButton title="OPEN NUTRITION TRACKER" onPress={() => navigation.navigate("NutritionTracker")} />
          <PrimaryButton title="OPEN SLEEP TRACKER" variant="outline" onPress={() => navigation.navigate("SleepTracker")} />
          <PrimaryButton title="OPEN MOOD TRACKER" variant="outline" onPress={() => navigation.navigate("MoodTracker")} />
        </View>

        {entries.map(([key, value]) => (
          <Card key={key} style={{ marginBottom: 10 }}>
            <Text style={typography.label}>{key.toUpperCase().replace("_", " ")}</Text>
            <Text style={[typography.caption, { marginTop: 6 }]}>{value.summary}</Text>
          </Card>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: 16, paddingBottom: 32 },
});
