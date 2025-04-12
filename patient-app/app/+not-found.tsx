import { Link, Stack } from 'expo-router';
import { StyleSheet } from 'react-native';
import { Surface, Text, Button } from 'react-native-paper';

export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ title: 'Oops!' }} />
      <Surface style={styles.container}>
        <Text variant="headlineMedium">This screen doesn't exist.</Text>
        <Link href="/" asChild>
          <Button mode="contained" style={styles.link}>
            Go to home screen!
          </Button>
        </Link>
      </Surface>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  link: {
    marginTop: 15,
    paddingVertical: 8,
  },
});
