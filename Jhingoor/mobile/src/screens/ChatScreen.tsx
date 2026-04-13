import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { ArrowUp, Bot, Plus } from "lucide-react-native";

import { api } from "../api/client";
import { AppHeader } from "../components/AppHeader";
import { colors } from "../theme/colors";
import { typography } from "../theme/typography";

type Msg = { id: string; role: string; content: string };

export function ChatScreen() {
  const qc = useQueryClient();
  const [text, setText] = useState("");
  const q = useQuery({
    queryKey: ["chat"],
    queryFn: async () => (await api.get<{ messages: Msg[] }>("/chat/messages")).data,
  });

  const send = useMutation({
    mutationFn: async (message: string) => (await api.post<{ reply: string }>("/chat/messages", { message })).data,
    onSuccess: () => {
      setText("");
      void qc.invalidateQueries({ queryKey: ["chat"] });
    },
  });

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={88}
    >
      <AppHeader />
      <View style={styles.connected}>
        <View style={styles.dot} />
        <Text style={styles.connectedText}>CONNECTED</Text>
      </View>
      <View style={styles.hero}>
        <Bot color={colors.primaryContainer} size={40} />
        <Text style={styles.heroTitle}>Precision Performance AI</Text>
        <Text style={styles.heroSub}>Your elite squad of specialists. Ask anything about fitness, nutrition, or recovery.</Text>
      </View>
      <FlatList
        data={q.data?.messages ?? []}
        keyExtractor={(m) => m.id}
        contentContainerStyle={{ padding: 16, paddingBottom: 8 }}
        renderItem={({ item }) => (
          <View style={[styles.bubble, item.role === "user" ? styles.bubbleUser : styles.bubbleAi]}>
            {item.role === "assistant" ? (
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <Bot size={14} color={colors.primaryContainer} />
                <Text style={styles.aiLabel}>JHINGOOR INTELLIGENCE</Text>
              </View>
            ) : null}
            <Text style={typography.body}>{item.content}</Text>
          </View>
        )}
      />
      <View style={styles.inputRow}>
        <Pressable style={styles.plus}>
          <Plus color={colors.onSurfaceVariant} size={22} />
        </Pressable>
        <TextInput
          style={styles.input}
          placeholder="Type your request..."
          placeholderTextColor={colors.onSurfaceVariant}
          value={text}
          onChangeText={setText}
        />
        <Pressable
          style={styles.send}
          onPress={() => {
            if (!text.trim()) return;
            send.mutate(text.trim());
          }}
        >
          <ArrowUp color={colors.onPrimaryFixed} size={22} />
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  connected: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-end",
    marginRight: 16,
    gap: 6,
    backgroundColor: colors.surfaceContainerHigh,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  dot: { width: 6, height: 6, borderRadius: 3, backgroundColor: colors.secondary },
  connectedText: { color: colors.secondary, fontSize: 10, fontWeight: "700" },
  hero: { paddingHorizontal: 24, paddingVertical: 12, alignItems: "center" },
  heroTitle: { marginTop: 8, fontFamily: "Manrope_800ExtraBold", fontSize: 22, color: colors.onSurface, textAlign: "center" },
  heroSub: { marginTop: 8, color: colors.onSurfaceVariant, textAlign: "center", fontFamily: "Inter_400Regular" },
  bubble: {
    borderRadius: 16,
    padding: 12,
    marginBottom: 10,
    maxWidth: "92%",
  },
  bubbleUser: { alignSelf: "flex-end", backgroundColor: colors.surfaceContainerHigh },
  bubbleAi: { alignSelf: "flex-start", backgroundColor: colors.surfaceContainerLow },
  aiLabel: { color: colors.primaryContainer, fontSize: 10, fontWeight: "800", letterSpacing: 0.6 },
  inputRow: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    gap: 8,
    borderTopWidth: 1,
    borderTopColor: colors.outlineVariant,
    backgroundColor: colors.surface,
  },
  plus: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surfaceContainerHigh,
    alignItems: "center",
    justifyContent: "center",
  },
  input: {
    flex: 1,
    backgroundColor: colors.surfaceContainerHighest,
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: colors.onSurface,
  },
  send: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primaryContainer,
    alignItems: "center",
    justifyContent: "center",
  },
});
