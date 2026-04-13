import type { ReactNode } from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { BarChart3, Bot, Dumbbell, LayoutGrid, UserRound } from "lucide-react-native";
import { StyleSheet, Text, View } from "react-native";

import { ActivityScreen } from "../screens/ActivityScreen";
import { ChatScreen } from "../screens/ChatScreen";
import { HomeScreen } from "../screens/HomeScreen";
import { ProfileScreen } from "../screens/ProfileScreen";
import { TrendsScreen } from "../screens/TrendsScreen";
import { colors } from "../theme/colors";

export type MainTabParamList = {
  Home: undefined;
  Activity: undefined;
  AIChat: undefined;
  Trends: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

function TabIcon({
  focused,
  children,
  label,
}: {
  focused: boolean;
  children: ReactNode;
  label: string;
}) {
  return (
    <View style={styles.tabItem}>
      <View style={[styles.iconWrap, focused && styles.iconWrapActive]}>{children}</View>
      <Text style={[styles.label, focused && styles.labelActive]}>{label}</Text>
    </View>
  );
}

export function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.surfaceContainerLow,
          borderTopColor: colors.outlineVariant,
          height: 64,
          paddingBottom: 8,
          paddingTop: 6,
        },
        tabBarShowLabel: false,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} label="HOME">
              <LayoutGrid color={focused ? colors.primaryContainer : colors.onSurfaceVariant} size={22} />
            </TabIcon>
          ),
        }}
      />
      <Tab.Screen
        name="Activity"
        component={ActivityScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} label="ACTIVITY">
              <Dumbbell color={focused ? colors.primaryContainer : colors.onSurfaceVariant} size={22} />
            </TabIcon>
          ),
        }}
      />
      <Tab.Screen
        name="AIChat"
        component={ChatScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} label="AI CHAT">
              <Bot color={focused ? colors.primaryContainer : colors.onSurfaceVariant} size={22} />
            </TabIcon>
          ),
        }}
      />
      <Tab.Screen
        name="Trends"
        component={TrendsScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} label="TRENDS">
              <BarChart3 color={focused ? colors.primaryContainer : colors.onSurfaceVariant} size={22} />
            </TabIcon>
          ),
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} label="PROFILE">
              <UserRound color={focused ? colors.primaryContainer : colors.onSurfaceVariant} size={22} />
            </TabIcon>
          ),
        }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  tabItem: { alignItems: "center", minWidth: 56 },
  iconWrap: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  iconWrapActive: {
    backgroundColor: colors.surfaceContainerHigh,
    shadowColor: colors.primaryContainer,
    shadowOpacity: 0.45,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 0 },
    elevation: 6,
  },
  label: {
    marginTop: 2,
    fontSize: 9,
    fontWeight: "700",
    color: colors.onSurfaceVariant,
    letterSpacing: 0.4,
  },
  labelActive: { color: colors.primaryContainer },
});
