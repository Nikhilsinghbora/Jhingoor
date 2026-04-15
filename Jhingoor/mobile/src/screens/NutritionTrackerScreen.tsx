import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { RefreshControl, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { PrimaryButton } from "../components/PrimaryButton";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

type NutritionPlan = {
  summary: string;
  tdee: number;
  macros: { calories: number; protein_g: number; carbs_g: number; fat_g: number };
  meals: { name: string; calories: number | null; source: string }[];
};

export function NutritionTrackerScreen() {
  const qc = useQueryClient();
  const [calories, setCalories] = useState("2100");
  const [protein, setProtein] = useState("140");
  const [carbs, setCarbs] = useState("230");
  const [fat, setFat] = useState("65");

  const plan = useQuery({
    queryKey: ["nutrition-plan"],
    queryFn: async () => (await api.get<NutritionPlan>("/health/nutrition/plan")).data,
    refetchInterval: 30_000,
  });

  const logMutation = useMutation({
    mutationFn: async () =>
      api.post("/health/nutrition/log", {
        date: new Date().toISOString().slice(0, 10),
        calories: Number(calories) || 0,
        protein: Number(protein) || 0,
        carbs: Number(carbs) || 0,
        fat: Number(fat) || 0,
        source: "manual",
      }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["nutrition-plan"] });
      await qc.invalidateQueries({ queryKey: ["advanced-insights"] });
    },
  });

  const totalMacros = useMemo(
    () => (Number(protein) || 0) + (Number(carbs) || 0) + (Number(fat) || 0),
    [protein, carbs, fat],
  );

  return (
    <View style={styles.screen}>
      <AppHeader />
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={plan.isFetching}
            onRefresh={() => void plan.refetch()}
            tintColor={colors.primaryContainer}
          />
        }
      >
        <Card style={{ marginBottom: 12 }}>
          <Text style={typography.label}>NUTRITION PLAN</Text>
          <Text style={[typography.title, { marginTop: 6 }]}>{Math.round(plan.data?.tdee ?? 0)} kcal target</Text>
          <Text style={[typography.caption, { marginTop: 8 }]}>{plan.data?.summary ?? "Loading plan..."}</Text>
        </Card>

        <Card style={{ marginBottom: 12 }} accent="teal">
          <Text style={typography.title}>Log Daily Nutrition</Text>
          <TextInput style={styles.input} value={calories} onChangeText={setCalories} keyboardType="number-pad" placeholder="Calories" placeholderTextColor={colors.onSurfaceVariant} />
          <TextInput style={styles.input} value={protein} onChangeText={setProtein} keyboardType="number-pad" placeholder="Protein (g)" placeholderTextColor={colors.onSurfaceVariant} />
          <TextInput style={styles.input} value={carbs} onChangeText={setCarbs} keyboardType="number-pad" placeholder="Carbs (g)" placeholderTextColor={colors.onSurfaceVariant} />
          <TextInput style={styles.input} value={fat} onChangeText={setFat} keyboardType="number-pad" placeholder="Fat (g)" placeholderTextColor={colors.onSurfaceVariant} />
          <Text style={typography.caption}>Macro total: {totalMacros} g</Text>
          <PrimaryButton title="SAVE NUTRITION LOG" loading={logMutation.isPending} onPress={() => logMutation.mutate()} style={{ marginTop: 10 }} />
        </Card>

        <Card>
          <Text style={typography.label}>MEAL SUGGESTIONS</Text>
          {(plan.data?.meals ?? []).slice(0, 5).map((meal, idx) => (
            <Text key={`${meal.name}-${idx}`} style={[typography.caption, { marginTop: 6 }]}>
              {meal.name} {meal.calories ? `· ${Math.round(meal.calories)} kcal` : ""} · {meal.source}
            </Text>
          ))}
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
