import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { Card } from "../components/Card";
import { PrimaryButton } from "../components/PrimaryButton";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

export function MoodTrackerScreen() {
  const qc = useQueryClient();
  const [mood, setMood] = useState("focused");
  const [energy, setEnergy] = useState("7");
  const [notes, setNotes] = useState("");

  const logMood = useMutation({
    mutationFn: async () =>
      api.post("/health/mood/log", {
        date: new Date().toISOString().slice(0, 10),
        mood,
        energy_level: Number(energy) || 1,
        notes: notes || null,
      }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["advanced-insights"] });
    },
  });

  return (
    <View style={styles.screen}>
      <AppHeader />
      <ScrollView contentContainerStyle={styles.content}>
        <Card accent="teal">
          <Text style={typography.title}>Mood Check-in</Text>
          <TextInput style={styles.input} value={mood} onChangeText={setMood} placeholder="Mood (e.g. focused, tired)" placeholderTextColor={colors.onSurfaceVariant} />
          <TextInput style={styles.input} value={energy} onChangeText={setEnergy} keyboardType="number-pad" placeholder="Energy level (1-10)" placeholderTextColor={colors.onSurfaceVariant} />
          <TextInput
            style={[styles.input, styles.notes]}
            value={notes}
            onChangeText={setNotes}
            placeholder="Notes"
            placeholderTextColor={colors.onSurfaceVariant}
            multiline
          />
          <PrimaryButton title="SAVE MOOD LOG" loading={logMood.isPending} onPress={() => logMood.mutate()} style={{ marginTop: 10 }} />
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
  notes: { minHeight: 90, textAlignVertical: "top" },
});
