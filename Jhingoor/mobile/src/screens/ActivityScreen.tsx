import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { FlatList, RefreshControl, StyleSheet, Text, TextInput, View } from "react-native";
import Slider from "@react-native-community/slider";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { PrimaryButton } from "../components/PrimaryButton";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

type StreamItem = {
  id: string;
  kind: string;
  time_label: string;
  title: string;
  subtitle: string | null;
  status: string | null;
  accent: string | null;
  calories: number | null;
  protein_g: number | null;
  carbs_g: number | null;
  fats_g: number | null;
  avg_hr: number | null;
  sets_count: number | null;
};

export function ActivityScreen() {
  const qc = useQueryClient();
  const [duration, setDuration] = useState(45);
  const [intensity, setIntensity] = useState(6);
  const [mealName, setMealName] = useState("");
  const [mealKcal, setMealKcal] = useState("320");

  const stream = useQuery({
    queryKey: ["activity-stream"],
    queryFn: async () => (await api.get<{ items: StreamItem[] }>("/activity-stream")).data,
  });

  const workoutMut = useMutation({
    mutationFn: async () =>
      api.post("/workouts", {
        workout_type: "Strength Training",
        duration_min: duration,
        intensity: Math.round(intensity),
        calories: Math.round(duration * 6),
        title: "Strength Training",
        subtitle: `Session · ${duration} mins`,
      }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["activity-stream"] }),
  });

  const mealMut = useMutation({
    mutationFn: async () =>
      api.post("/meals", {
        name: mealName || "Custom meal",
        calories: Number(mealKcal) || 0,
        protein_g: 20,
        carbs_g: 30,
        fats_g: 10,
      }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["activity-stream"] }),
  });

  return (
    <View style={styles.screen}>
      <AppHeader />
      <FlatList
        data={stream.data?.items ?? []}
        keyExtractor={(i) => i.id}
        refreshControl={
          <RefreshControl refreshing={stream.isFetching} onRefresh={() => void stream.refetch()} tintColor={colors.primaryContainer} />
        }
        ListHeaderComponent={
          <View style={{ paddingHorizontal: 16, paddingTop: 8 }}>
            <Text style={[typography.label, { marginBottom: 8 }]}>ACTIVITY STREAM</Text>
            <Card style={{ marginBottom: 16 }} accent="lime">
              <Text style={typography.title}>Log Workout</Text>
              <Text style={[typography.caption, { marginTop: 8 }]}>Duration (min)</Text>
              <TextInput
                style={styles.input}
                keyboardType="number-pad"
                value={String(duration)}
                onChangeText={(t) => setDuration(Number(t.replace(/\D/g, "")) || 0)}
              />
              <Text style={[typography.caption, { marginTop: 12 }]}>Intensity</Text>
              <Slider
                minimumValue={1}
                maximumValue={10}
                step={1}
                value={intensity}
                onValueChange={setIntensity}
                minimumTrackTintColor={colors.primaryContainer}
                maximumTrackTintColor={colors.surfaceBright}
                thumbTintColor={colors.primaryContainer}
              />
              <PrimaryButton title="SAVE WORKOUT" loading={workoutMut.isPending} onPress={() => workoutMut.mutate()} />
            </Card>
            <Card style={{ marginBottom: 16 }} accent="teal">
              <Text style={typography.title}>Log Meal</Text>
              <TextInput
                style={[styles.input, { marginTop: 8 }]}
                placeholder="Item name"
                placeholderTextColor={colors.onSurfaceVariant}
                value={mealName}
                onChangeText={setMealName}
              />
              <TextInput
                style={styles.input}
                placeholder="Kcal"
                placeholderTextColor={colors.onSurfaceVariant}
                keyboardType="number-pad"
                value={mealKcal}
                onChangeText={setMealKcal}
              />
              <PrimaryButton
                title="ADD TO MEAL PLAN"
                variant="outline"
                loading={mealMut.isPending}
                onPress={() => mealMut.mutate()}
              />
            </Card>
          </View>
        }
        contentContainerStyle={{ paddingBottom: 120 }}
        renderItem={({ item }) => (
          <View style={{ paddingHorizontal: 16, marginBottom: 10 }}>
            <Text style={typography.caption}>
              {item.time_label} {item.status ? `· ${item.status}` : ""}
            </Text>
            <Card accent={item.kind === "meal" ? "teal" : item.accent === "muted" ? "none" : "lime"}>
              <Text style={typography.title}>{item.title}</Text>
              {item.subtitle ? <Text style={typography.caption}>{item.subtitle}</Text> : null}
              {item.calories != null ? (
                <Text style={[typography.body, { marginTop: 6 }]}>{item.calories} kcal</Text>
              ) : null}
            </Card>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  input: {
    backgroundColor: colors.surfaceContainerHighest,
    borderRadius: 12,
    padding: 12,
    color: colors.onSurface,
    marginTop: 6,
  },
});
