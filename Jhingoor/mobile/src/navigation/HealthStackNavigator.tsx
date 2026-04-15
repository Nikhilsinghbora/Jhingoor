import { createNativeStackNavigator } from "@react-navigation/native-stack";

import { InsightsDashboardScreen } from "../screens/InsightsDashboardScreen";
import { MoodTrackerScreen } from "../screens/MoodTrackerScreen";
import { NutritionTrackerScreen } from "../screens/NutritionTrackerScreen";
import { SleepTrackerScreen } from "../screens/SleepTrackerScreen";
import { colors } from "../theme/colors";

export type HealthStackParamList = {
  InsightsDashboard: undefined;
  NutritionTracker: undefined;
  SleepTracker: undefined;
  MoodTracker: undefined;
};

const Stack = createNativeStackNavigator<HealthStackParamList>();

export function HealthStackNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="InsightsDashboard"
      screenOptions={{
        headerStyle: { backgroundColor: colors.surfaceContainerLow },
        headerTintColor: colors.onSurface,
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen name="InsightsDashboard" component={InsightsDashboardScreen} options={{ title: "Insights Dashboard" }} />
      <Stack.Screen name="NutritionTracker" component={NutritionTrackerScreen} options={{ title: "Nutrition Tracker" }} />
      <Stack.Screen name="SleepTracker" component={SleepTrackerScreen} options={{ title: "Sleep Tracker" }} />
      <Stack.Screen name="MoodTracker" component={MoodTrackerScreen} options={{ title: "Mood Tracker" }} />
    </Stack.Navigator>
  );
}
