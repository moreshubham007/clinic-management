import { StyleSheet } from 'react-native';
import { Surface, Text } from 'react-native-paper';

export default function DoctorsScreen() {
  return (
    <Surface style={styles.container}>
      <Text variant="headlineMedium">Doctors</Text>
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
}); 